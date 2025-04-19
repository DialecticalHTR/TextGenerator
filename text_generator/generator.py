import random

from .wiki import WikipediaFetcher
from .formatter import TranscriptionFormatter
from .paragraph import DialecticParagraphProcessor
from .paragraph.dialectic import Alphabet


class TextGenerator:
    def __init__(self):
        self.fetcher = WikipediaFetcher()
        self.formatter = TranscriptionFormatter()
        self.processor = DialecticParagraphProcessor()

    def generate_text_chunks(
        self, amount, max_word_len=40, min_words=2, max_words=4
    ):
        sentences = set()

        while len(sentences) < amount:
            sentences_list = []

            page = self.fetcher.get_random_article()
            paragraphs = [
                self.processor.process(p) for p in page.get_all_paragraphs()
            ]
            text = ' '.join(paragraphs)
            text = self.formatter.format(text)
            
            words = [word for word in text.split(" ") if len(word) < max_word_len]

            while len(words) > max_words:
                sentence_len = random.randint(min_words, max_words)
                sentence = " ".join(words[:max_words])
                words = words[sentence_len:]

                if not sentence:
                    continue
                if not any(
                    symbol in sentence for symbol in Alphabet.dialectic   
                ):
                    continue
                
                sentences_list.append(sentence)

            sentences = sentences | set(sentences_list)

        sentences = list(sentences)[:amount]
        return sentences
