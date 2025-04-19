from .base import BaseParagraphProcessor


class DoNothingParagraphProcessor(BaseParagraphProcessor):
    def process(self, paragraph: str) -> str:
        return paragraph
