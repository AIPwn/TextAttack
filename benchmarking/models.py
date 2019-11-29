import argparse
import textattack
import torch
import sys

import textattack.models as models

def _cb(s): return textattack.utils.color_text_terminal(str(s), color='blue')
def _cg(s): return textattack.utils.color_text_terminal(str(s), color='green')
def _cr(s): return textattack.utils.color_text_terminal(str(s), color='red')
def _pb(): print(_cg('-' * 60))

def test_model_on_dataset(model, dataset):
    # TODO do inference in batch.
    succ = 0
    fail = 0
    for label, text in dataset:
        ids = model.convert_text_to_ids(text)
        ids = torch.tensor([ids]).to(textattack.utils.get_device())
        pred_score = model(ids).squeeze()
        pred_label = pred_score.argmax().item()
        if label==pred_label: succ += 1
        else: fail += 1
    perc = float(succ)/(succ+fail)*100.0
    perc = '{:.2f}%'.format(perc)
    print(f'Successes {succ}/{succ+fail} ({_cb(perc)})')
    return perc

def test_all_models(num_examples):
    _pb()
    for model_name in textattack.run_attack.MODEL_CLASS_NAMES:
        model = eval(textattack.run_attack.MODEL_CLASS_NAMES[model_name])()
        dataset = textattack.run_attack.DATASET_BY_MODEL[model_name]()
        print(f'\nTesting {_cr(model_name)} on {_cr(type(dataset))}...')
        test_model_on_dataset(model, dataset)
        _pb()
    # @TODO print the grid of models/dataset names with results in a nice table :)

def test_one_model(model_name, num_examples):
    try:
        model = textattack.run_attack.MODEL_CLASS_NAMES[model_name]()
    except:
        raise ValueError(f'Unknown model {model_name}')
    for dataset_name in textattack.run_attack.MODELS_BY_DATASET:
        if model_name not in textattack.run_attack.MODELS_BY_DATASET[dataset_name]:
            continue
        else:
            dataset = textattack.run_attack.DATASET_CLASS_NAMES[dataset_name](num_examples)
            print(f'\nTesting {_cr(model_name)} on {_cr(dataset_name)}...')
            test_model_on_dataset(model, dataset)
        _pb()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', '--m', default=None, type=str,
        help="model to test (if you dont want to test them all)")
    parser.add_argument('--n', type=int, default=100, 
        help="number of examples to test on")
    return parser.parse_args()

if __name__ == '__main__': 
    args = parse_args()
    if args.model is None or args.model == 'all':
        test_all_models(args.n)
    else:
        test_one_model(args.model, args.n)