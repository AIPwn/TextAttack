from textattack.attacks import Attack

class WhiteBoxAttack(Attack):
    """ An abstract class that defines a white-box attack. 
    
        
        A white-box attack can information about the model, so it stores the entire
            model as the field `self.model`. 
        
        Arg:
            model (nn.Module): The model to attack.
            constraints (list(Constraint)): The list of constraints
                for the model's transformations.
    
    """
    def __init__(self, model, constraints=[]):
        self.model = model
        self.text_to_tokens_converter = model.convert_text_to_tokens
        self.tokens_to_ids_converter = model.convert_tokens_to_ids
        super().__init__(constraints=constraints)