from copy import deepcopy
import datetime
import math
import os
import re
import subprocess
import sys
import torch

from textattack.run_attack import get_args
from textattack.utils import color_text_terminal


def _cb(s): return color_text_terminal(str(s), color='blue')
def _cg(s): return color_text_terminal(str(s), color='green')
def _cr(s): return color_text_terminal(str(s), color='red')

result_regex = '----------------------------------- Result [0-9]* -----------------------------------'

def validate_args(args):
    """ Some arguments from `run_attack` may not be valid to run in parallel.
        Check for them and throw errors here. """
    if args.interactive:
        raise Error('Cannot run attack in parallel with --interactive set.')
    if not args.num_examples:
        raise Error('Cannot run attack with --num_examples set.')

def main():
    input_args = get_args()
    validate_args(input_args)
    
    num_devices = torch.cuda.device_count()
    num_examples_per_device = int(math.ceil(input_args.num_examples / float(num_devices)))
    
    input_args.num_examples = num_examples_per_device
    
    current_working_dir = os.path.dirname(os.path.abspath(__file__))
    run_attack_path = os.path.join(current_working_dir, 'run_attack.py')
    
    today = datetime.datetime.now()
    out_dir = input_args.out_dir or 'outputs'
    folder_name = os.path.join(current_working_dir, out_dir, 'attack-' + today.strftime('%Y-%m-%d-%H--%H:%M:%S'))
    os.makedirs(folder_name)
    
    arg_file = open(os.path.join(folder_name, 'args.txt'), 'w')
    processes = []
    out_file_names = []
    for i in range(num_devices):
        # Create outfiles for this thread.
        out_file_name = os.path.join(folder_name, f'out-{i}.txt')
        out_file = open(out_file_name, 'w')
        out_file_names.append(out_file_name)
        err_file = open(os.path.join(folder_name, f'err-{i}.txt'), 'w')
        # Create unique environment for this thread.
        new_env = os.environ.copy()
        new_env['CUDA_VISIBLE_DEVICES'] = str(i)
        new_env['PYTHONUNBUFFERED'] = '1'
        args = ['python', run_attack_path]
        command_line_args_list = sys.argv[1:]
        # Change number of examples in argument list.
        examples_at_i = str(num_examples_per_device)
        if '--num_examples' in command_line_args_list:
            _x = command_line_args_list.index('--num_examples')
            command_line_args_list[_x+1] = examples_at_i
        elif '--n' in command_line_args_list:
            _x = command_line_args_list.index('--n')
            command_line_args_list[_x+1] = examples_at_i
        else:
            command_line_args_list.extend(['--n', examples_at_i])
        # Change offset in argument list.
        offset_at_i = str(input_args.num_examples_offset + num_examples_per_device * i)
        if '--num_examples_offset' in command_line_args_list:
            _x = command_line_args_list.index('--num_examples_offset')
            command_line_args_list[_x+1] = offset_at_i
        elif '--o' in command_line_args_list:
            _x = command_line_args_list.index('--o')
            command_line_args_list[_x+1] = offset_at_i
        else:
            command_line_args_list.extend(['--num_examples_offset', offset_at_i])
        
        # Format and run command.
        full_args = args + command_line_args_list
        out_file.flush()
        p = subprocess.Popen(full_args, env=new_env, stdout=out_file, stderr=err_file)
        processes.append(p)
        arg_str = ' '.join(full_args)
        print(f'Started process {i}:', _cr(arg_str), '\n')
        arg_file.write(f'Started process {i}: ' + arg_str + '\n')
    
    arg_file.write('Attack started at ')
    arg_file.write(today.strftime('%Y-%m-%d at %H:%M:%S'))
    arg_file.write('\n')
    arg_file.close()
    
    print('Printing results for {} attack threads to folder {}'.format(_cg(num_devices), 
        _cb(folder_name)))
    
    # Wait for attacks to run and aggregate results.
    for p in processes:
        if p.wait() != 0:
            print('Error running process ', p)
    final_out_file = open(os.path.join(folder_name, 'final.txt'), 'w')
    i = 1
    for out_file in out_file_names:
        lines = open(out_file, 'r').readlines()
        j = 0
        while j < len(lines):
            if re.match(result_regex, lines[j]):
                line_j_tokens = lines[j].split()
                line_j_tokens[2] = str(i)
                lines[j] = ' '.join(line_j_tokens) + '\n'
                i += 1
                for _ in range(4):
                    final_out_file.write(lines[j])
                    j += 1
            else: j += 1
    final_out_file.close()

if __name__ == '__main__': main()