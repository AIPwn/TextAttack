from textattack.utils import get_device

class TokenizedText:
    def __init__(self, text, tokenizer, attack_attrs=dict()):
        """ Initializer stores text and tensor of tokenized text.
        
        Args:
            text (string): The string that this TokenizedText represents
            tokenizer (Tokenizer): an object that can convert text to tokens
                and convert tokens to IDs
        """
         # @TODO just pass a reference to the model since this is getting
         # unwieldy-- also add to README about the methods models need now
        self.text = text
        self.tokenizer = tokenizer
        self.tokens = tokenizer.convert_text_to_tokens(text)
        self.ids = tokenizer.convert_tokens_to_ids(self.tokens)
        self.words = raw_words(text)
        self.attack_attrs = attack_attrs

    def text_window_around_index(self, index, window_size):
        """ The text window of `window_size` words centered around `index`. """
        length = len(self.words)
        half_size = (window_size - 1) // 2
        if index - half_size < 0:
            start = 0
            end = min(window_size, length-1)
        elif index + half_size > length - 1:
            start = max(0, length - window_size)
            end = length - 1
        else:
            start = index - half_size
            end = index + half_size
        text_idx_start = self._text_index_of_word_index(start)
        text_idx_end = self._text_index_of_word_index(end) + len(self.words[end])
        return self.text[text_idx_start:text_idx_end]
         
    def _text_index_of_word_index(self, i):
        """ Returns the index of word `i` in self.text. """
        pre_words = self.words[:i+1]
        lower_text = self.text.lower()
        # Find all words until `i` in string.
        look_after_index = 0
        for word in pre_words:
            look_after_index = lower_text.find(word.lower(), look_after_index)
        return look_after_index 

    def text_until_word_index(self, i):
        """ Returns the text before the beginning of word at index `i`. """
        look_after_index = self._text_index_of_word_index(i)
        return self.text[:look_after_index]
    
    def text_after_word_index(self, i):
        """ Returns the text after the end of word at index `i`. """
        # Get index of beginning of word then jump to end of word.
        look_after_index = self._text_index_of_word_index(i) + len(self.words[i])
        return self.text[look_after_index:]
    
    def first_word_diff(self, other_tokenized_text):
        """ Returns the first word in self.words that differs from 
            other_tokenized_text. Useful for word swap strategies. """
        w1 = self.words
        w2 = other_tokenized_text.words
        for i in range(min(len(w1), len(w2))):
            if w1[i] != w2[i]:
                return w1
        return None
    
    def first_word_diff_index(self, other_tokenized_text):
        """ Returns the index of the first word in self.words that differs
            from other_tokenized_text. Useful for word swap strategies. """
        w1 = self.words
        w2 = other_tokenized_text.words
        for i in range(min(len(w1), len(w2))):
            if w1[i] != w2[i]:
                return i
        return None
   
    def all_words_diff(self, other_tokenized_text):
        """ Returns the set of indices for which this and other_tokenized_text
        have different words. """
        indices = set()
        w1 = self.words
        w2 = other_tokenized_text.words
        for i in range(min(len(w1), len(w2))):
            if w1[i] != w2[i]:
                indices.add(i)
        return indices
        
    def ith_word_diff(self, other_tokenized_text, i):
        """ Returns whether the word at index i differs from other_tokenized_text
        """
        w1 = self.words
        w2 = other_tokenized_text.words
        if len(w1) - 1 < i or len(w2) - 1 < i:
            return True
        return w1[i] != w2[i]

    def replace_words_at_indices(self, indices, new_words):
        """ This code returns a new TokenizedText object where the word at 
            `index` is replaced with a new word."""
        print('replacing /',indices)
        print('\tat/', new_words)
        if len(indices) != len(new_words):
            raise ValueError(f'Cannot replace {len(new_words)} words at {len(indices)} indices.')
        words = self.words[:]
        for i, new_word in zip(indices, new_words):
            words[i] = new_word
        return self._replace_with_new_words(new_words)
    
    def replace_word_at_index(self, index, new_word):
        """ This code returns a new TokenizedText object where the word at 
            `index` is replaced with a new word."""
        self.attack_attrs['modified_word_index'] = index
        return self.replace_words_at_indices([index], [new_word])
    
    def _replace_with_new_words(self, new_words):
        """ This code returns a new TokenizedText object and replaces old list 
            of words with a new list of words, but preserves the punctuation 
            and spacing of the original message.
        """
        final_sentence = ''
        text = self.text
        for input_word, adv_word in zip(self.words, new_words):
            if input_word == '[UNKNOWN]': continue
            word_start = text.index(input_word)
            word_end = word_start + len(input_word)
            final_sentence += text[:word_start]
            final_sentence += adv_word
            text = text[word_end:]
        final_sentence += text # Add all of the ending punctuation.
        return TokenizedText(final_sentence, self.tokenizer, 
            attack_attrs=self.attack_attrs)
    
    def replace_tokens_at_indices(self, indices, new_tokens):
        """ This code returns a new TokenizedText object where the tokens at 
            `index` is replaced with a new word."""
        if len(indices) != len(new_tokens):
            raise ValueError(f'Cannot replace {len(words)} words at {len(indices)} indices.')
        tokens = self.tokens[:]
        for i, token in zip(indices, new_tokens):
            tokens[i] = token
        return self._replace_with_new_tokens(tokens)
    
    def replace_token_at_index(self, index, new_token):
        """ Replaces token at index `index` with `new_token`. """
        self.attack_attrs['modified_token_index'] = index
        return self.replace_tokens_at_indices([index], [new_token])
    
    def _replace_with_new_tokens(self, new_tokens):
        """ This code returns a new TokenizedText object and replaces old list 
            of tokens with a new list of tokens, but preserves the punctuation 
            and spacing of the original message.
        """
        final_sentence = ''
        text = self.text
        for input_token, new_token in zip(self.tokens, new_tokens):
            if input_token != new_token:
                print('old_token', input_token, 'new_token', new_token)
            token_start = text.lower().index(input_token.lower())
            token_end = token_start + len(input_token)
            final_sentence += text[:token_start]
            if input_token == new_token:
                text = text[token_start:]
            else:
                final_sentence += new_token
                text = text[token_end:]
        final_sentence += text # Add all of the ending punctuation.
        return TokenizedText(final_sentence, self.tokenizer, 
            attack_attrs=self.attack_attrs)
        
    def __repr__(self):
        return f'<TokenizedText "{self.text}">'

def raw_words(s):
    """ Lowercases a string, removes all non-alphanumeric characters,
        and splits into words. """
    words = []
    word = ''
    for c in ' '.join(s.split()):
        if c.isalpha():
            word += c
        elif word:
            words.append(word)
            word = ''
    if word: words.append(word)
    return words