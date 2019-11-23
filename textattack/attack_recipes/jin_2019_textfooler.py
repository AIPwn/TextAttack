'''
    Jin, D., Jin, Z., Zhou, J.T., & Szolovits, P. (2019). 
    
    Is BERT Really Robust? Natural Language Attack on Text Classification and 
        Entailment. 
    
    ArXiv, abs/1907.11932.
    
'''

from textattack.attacks.blackbox import GreedyWordSwapWIR
from textattack.constraints.semantics import UniversalSentenceEncoder
from textattack.transformations import WordSwapEmbedding

def Jin2019TextFooler(model):
    #
    # Swap words with their embedding nearest-neighbors. 
    #
    # Embedding: Counter-fitted Paragram Embeddings.
    #
    # 50 nearest-neighbors with a cosine similarity of at least 0.5.
    # (The paper cites 0.7, but analysis of the code and some empirical
    # results show that it's definitely 0.5.)
    #
    transformation = WordSwapEmbedding(max_candidates=50, min_cos_sim=0.5, 
        check_pos=True)
    #
    # Greedily swap words with "Word Importance Ranking".
    #
    attack = GreedyWordSwapWIR(model, transformations=[transformation])
    #
    # Universal Sentence Encoder with ε = 0.7.
    #
    attack.add_constraint(UniversalSentenceEncoder(threshold=0.7, 
        metric='cosine', compare_with_original=False, window_size=15))
    
    return attack