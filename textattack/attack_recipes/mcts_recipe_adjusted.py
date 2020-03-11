
from textattack.attack_methods import MonteCarloTreeSearch
from textattack.constraints.semantics import WordEmbeddingDistance
from textattack.constraints.semantics.sentence_encoders import UniversalSentenceEncoder, BERT
from textattack.constraints.syntax import PartOfSpeech, LanguageTool
from textattack.transformations import WordSwapEmbedding

def MCTSRecipeAdjusted(model, SE_thresh=0.98, sentence_encoder='bert'):
    #
    # Swap words with their embedding nearest-neighbors. 
    #
    # Embedding: Counter-fitted PARAGRAM-SL999 vectors.
    #
    # 50 nearest-neighbors with a cosine similarity of at least 0.5.
    # (The paper claims 0.7, but analysis of the code and some empirical
    # results show that it's definitely 0.5.)
    #
    transformation = WordSwapEmbedding(max_candidates=50, textfooler_stopwords=True)
    #
    # Minimum word embedding cosine similarity of 0.9.
    #
    constraints = []
    constraints.append(
            WordEmbeddingDistance(min_cos_sim=0.9)
    )
    #
    # Universal Sentence Encoder with a minimum angular similarity of ε = 0.7.
    #
    if sentence_encoder == 'bert':
        se_constraint = BERT(threshold=SE_thresh,
            metric='cosine', compare_with_original=False, window_size=15,
            skip_text_shorter_than_window=False)
    else:
        se_constraint = UniversalSentenceEncoder(threshold=SE_thresh,
            metric='cosine', compare_with_original=False, window_size=15,
            skip_text_shorter_than_window=False)
    constraints.append(se_constraint)
    #
    # Do grammar checking
    #
    constraints.append(
            LanguageTool(0)
    )
    #
    # Greedily swap words with "Word Importance Ranking".
    #
    attack = MonteCarloTreeSearch(model, transformation=transformation,
        constraints=constraints)
    
    return attack
