from textattack.attack_methods import MonteCarloTreeSearch
from textattack.constraints.semantics import WordEmbeddingDistance
from textattack.constraints.semantics.sentence_encoders import UniversalSentenceEncoder
from textattack.constraints.syntax import PartOfSpeech
from textattack.transformations import WordSwapEmbedding

def MCTSRecipe(model):
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
    # Minimum word embedding cosine similarity of 0.5.
    #
    constraints = []
    constraints.append(
            WordEmbeddingDistance(min_cos_sim=0.5)
    )
    #
    # Only replace words with the same part of speech (or nouns with verbs)
    #
    constraints.append(
            PartOfSpeech(allow_verb_noun_swap=True)
    )
    #
    # Universal Sentence Encoder with a minimum angular similarity of ε = 0.7.
    #
    # In the TextFooler code, they forget to divide the angle between the two
    # embeddings by pi. So if the original threshold was that 1 - sim >= 0.7, the 
    # new threshold is 1 - (0.3) / pi = 0.90445
    #
    use_constraint = UniversalSentenceEncoder(threshold=0.904458599,
        metric='angular', compare_with_original=False, window_size=15,
        skip_text_shorter_than_window=True)
    constraints.append(use_constraint)
    #
    # Greedily swap words with "Word Importance Ranking".
    #
    attack = MCTS(model, transformation=transformation,
        constraints=constraints)
    
    return attack
