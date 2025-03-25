from .wiki import WikipediaFetcher
from .formatter import TranscriptionFormatter

import random


ALLOWED_SYMBOLS = set(
    " АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯабвгдежзийклмнопрстуфхцчшщьыъэюя0123456789[].!\"'‿/j%(),-?:;"
    + "\u0301\u0302\u0306\u0304\u0311"
)


def generate_text_chunks(
    amount, max_word_len=40, min_words=2, max_words=4
):
    sentences = set()
    text_generator = WikipediaFetcher()
    formatter = TranscriptionFormatter()

    while len(sentences) < amount:
        sentences_list = []
        text = text_generator.get_random_text()
        text = formatter.format(text)
        words = [word for word in text.split(" ") if len(word) < max_word_len]

        while len(words) > max_words:
            sentence_len = random.randint(min_words, max_words)
            sentence = " ".join(words[:max_words])
            words = words[sentence_len:]

            sentence = ''.join(filter(lambda s: s in ALLOWED_SYMBOLS, sentence))
            if not sentence:
                continue
            if '\u0301' not in sentence:
                continue
            
            sentences_list.append(sentence)

        sentences = sentences | set(sentences_list)

    sentences = list(sentences)[:amount]
    return sentences
