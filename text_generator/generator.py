import random

import tqdm

from .wiki import WikipediaFetcher
from .formatter import TranscriptionFormatter
from .paragraph import DialecticParagraphProcessor
from .paragraph.dialectic import Alphabet


class TextGenerator:
    def __init__(self):
        self.fetcher = WikipediaFetcher()
        self.formatter = TranscriptionFormatter()
        self.processor = DialecticParagraphProcessor()

        self.max_retries = 3

    def generate_text_chunks(
        self, amount, max_word_len=40, min_words=2, max_words=4
    ):
        sentences = set()

        progress = tqdm.tqdm(total=amount)
        while len(sentences) < amount:
            sentences_list = []

            retries = self.max_retries
            while retries:
                try:
                    page = self.fetcher.get_random_article()
                    break
                except Exception as e:
                    print(f"Exception: {e}, retries: {retries}")
                    retries -= 1
            else:
                raise RuntimeError(f"Failed to fetch a page from Wikipedia {self.max_retries} times.")

            paragraphs = []
            for p in page.get_all_paragraphs():
                try:
                    processed = self.processor.process(p)
                    paragraphs.append(processed)
                except Exception as e:
                    print(page.title)
                    print(f"Exception: {e}")
                    paragraphs.append(p)
            
            words = []

            start_index, end_index = 0, 0
            while end_index < len(paragraphs):
                text_length = 0

                while (
                    end_index < len(paragraphs) and 
                    (text_length := text_length + len(paragraphs[end_index]) + (end_index - start_index > 0)) < 500_000
                ):
                    end_index += 1
                
                text = ' '.join(paragraphs[start_index:end_index])
                text = self.formatter.format(text)
                words.extend(
                    word for word in text.split(" ") if len(word) < max_word_len
                )
                
                start_index = end_index
            
            while len(words) > max_words:
                sentence_len = random.randint(min_words, max_words)
                sentence = " ".join(words[:max_words])
                words = words[sentence_len:]

                sentence = ''.join(filter(lambda s: s in Alphabet.allowed_symbols, sentence))
                if not sentence:
                    continue
                if not any(
                    symbol in sentence for symbol in Alphabet.dialectic   
                ):
                    continue
                
                sentences_list.append(sentence)

            sentences = sentences | set(sentences_list)
            progress.n = len(sentences)
            progress.refresh()

        progress.close()
        sentences = list(sentences)[:amount]
        return sentences
