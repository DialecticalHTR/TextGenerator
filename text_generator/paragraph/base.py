import abc


class BaseParagraphProcessor(abc.ABC):
    @abc.abstractmethod
    def process(self, paragraph: str) -> str:
        pass
