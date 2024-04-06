import spacy
from spellchecker import SpellChecker

nlp = spacy.load('en_core_web_sm')
spell = SpellChecker()

def preprocess_text(text):
    corrected_text = correct_typos(text)
    doc = nlp(corrected_text)
    lemmatized_tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
    preprocessed_text = ' '.join(lemmatized_tokens)
    return preprocessed_text

def correct_typos(text):
    tokens = text.split()
    corrected_tokens = [spell.correction(token) for token in tokens]
    corrected_text = ' '.join(corrected_tokens)
    return corrected_text
