from textattack.attacks import AttackResult
from textattack import utils as utils

class FailedAttackResult(AttackResult):
    def __init__(self, original_text, original_label):
        super().__init__(original_text, original_text, original_label, original_label)

    def __data__(self, color_method=None):
        data = (self.result_str(color_method), self.original_text.text)
        return tuple(map(str, data))

    def result_str(self, color_method=None):
        failed_str = utils.color_label('[FAILED]', 'red', color_method)
        return utils.color_label(self.original_label, method=color_method) + '-->' + failed_str 
