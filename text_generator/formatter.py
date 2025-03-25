import re
import unicodedata
from string import *

from .allowed import ALLOWED_SYMBOLS


# Useful constants
HARD_VOWELS = 'аоуыэАОУЫЭ'
SOFT_VOWELS = 'яёюиеЯЁЮИЕ'
VOWELS = HARD_VOWELS + SOFT_VOWELS

PAIRED_CONSONANTS = 'бвгдзклмнпрстфхБВГДЗКЛМНПРСТФХ'
ALWAYS_SOFT_CONSONANTS = 'чщйЧЩЙ'
ALWAYS_HARD_CONSONANTS = 'жшцЖШЦ'
CONSONANTS = PAIRED_CONSONANTS + ALWAYS_SOFT_CONSONANTS + ALWAYS_HARD_CONSONANTS

RUSSIAN_ALPHABET = CONSONANTS + VOWELS + 'ьъЬЪ'

COMBINING_ACUTE = '\u0301'
APOSTROPHE = '\u0027'


class TranscriptionFormatter:
    _accentor = None

    def __init__(self):
        if TranscriptionFormatter._accentor is None:
            from tsnorm import Normalizer
            TranscriptionFormatter._accentor = Normalizer(stress_mark=COMBINING_ACUTE, stress_mark_pos="after", stress_yo=True)
        
    def format(self, text: str, add_accents=True, add_pauses=True, add_softness=True, add_yots=True) -> str:        
        if add_accents:
            text = self._add_accents(text)
        if not text:
            return ""

        if add_softness:
            text = self._add_softness(text)
        if add_yots:
            text = self._add_yots(text)

        if add_pauses:
            text = self._add_pauses(text)

        text = ' '.join(text.split())
        return text

    @staticmethod
    def _decompose_acutes(text: str) -> str:
        result = ""
        for char in text:
            decomposed = unicodedata.normalize('NFD', char) 
            if COMBINING_ACUTE in decomposed:
                result += decomposed
            else:
                result += char 
        return result

    @staticmethod
    def _add_accents(text: str) -> str:
        normalized = TranscriptionFormatter._decompose_acutes(text)

        # Filter all non-word symbols
        words = list()
        for word in normalized.split():
            word = ''.join(filter(lambda c: c in ALLOWED_SYMBOLS, word))
            if word:
                words.append(word)

        to_accent = " ".join(words)
        try:
            accent_data = TranscriptionFormatter._accentor(to_accent)
        except:
            return ""
        text = accent_data

        return text

    @staticmethod
    def _add_softness(text: str) -> str:
        result = text[0]
        for i in range(1, len(text)):
            previous, current = text[i-1], text[i]

            if current in SOFT_VOWELS and previous in PAIRED_CONSONANTS:
                result += APOSTROPHE
            result += current

        return result

    @staticmethod
    def _add_pauses(text: str) -> str: 
        short_pauses = text.translate(
            {ord(c): ' / ' for c in ','}
        )
        
        sentences = re.split('[\?\!\.]+ ', short_pauses)
        sentences = [' '.join(sentence.split()) for sentence in sentences]
        sentences = [sentence.capitalize() for sentence in sentences]

        long_pauses = ' // '.join(sentences)
        return long_pauses
        
    @staticmethod
    def _add_yots(text: str) -> str:
        yot_table = {
            'я': 'jа',
            'ё': 'jо',
            'ю': 'jу',
            'и': 'jи',
            'е': 'jе',
        }

        result = text[0]
        for i in range(1, len(text)):
            previous, current = text[i-1], text[i]

            if previous in VOWELS and current in SOFT_VOWELS:
                result += yot_table[current.lower()]
            else:
                result += current
        return result
