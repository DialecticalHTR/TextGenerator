# Is this solution over-complicated? Mayhaps. But what I know is that 
# it is better than pointlessly trying different regex combinations for hours
# in hopes of good result. This has structure and keeps my mind sane. 

import abc

from enum import Enum, auto
from typing import Callable, Any, TypeAlias, Union

from .base import BaseParagraphProcessor 


class Alphabet:
    lowercase = "абвгдеёжзийклмнопрстуфхцчшщьъыэюя"
    uppercase = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЪЫЭЮЯ"
    numbers = "0123456789"
    ending_punctuation = ".!?"
    punctuation = "[]\"'‿/%(),-:;«»" + ending_punctuation
    dialectic = "\u0301\u0302\u0306\u0304\u0311'"
    separators = " "

    allowed_symbols = set(
        lowercase + uppercase + numbers + punctuation + dialectic + separators
    )


# ===== Tokenizer ===== #
class TokenType(Enum):
    EOF = auto()

    WORD = auto()
    PUNCTUATION = auto()
    ENDING_PUNCTUATION = auto()

    OPEN_PARENT = auto()
    CLOSE_PARENT = auto()
    
    OPEN_QUOTE = auto()
    CLOSE_QUOTE = auto()
    QUOTE = auto()

    SPACE = auto()


class Token:
    def __init__(self, _type, position, literal):
        self.type: TokenType = _type
        self.position: int = position
        self.literal: str = literal
    
    def __repr__(self):
        return f"{self.type.name} ({self.literal}) at {self.position}"


class Tokenizer:
    def __init__(self):
        self.position: int = 0
        self.paragraph: str = None
    
    def _init(self, paragraph):
        self.position = 0
        self.paragraph = paragraph
    
    def peek(self):
        return self.paragraph[self.position]
    
    def peek_next(self):
        if (next_pos := self.position + 1) >= len(self.paragraph):
            return ""
        return self.paragraph[next_pos]

    def advance(self):
        self.position += 1

    def isEOF(self):
        return self.position >= len(self.paragraph)

    def tokenise(self, paragraph):
        self._init(paragraph)

        tokens = []

        while not self.isEOF():
            char = self.peek()
            token: Token = None

            match char:
                case "(" | "[": 
                    token = Token(TokenType.OPEN_PARENT, self.position, char)
                    self.advance()
                case ")" | "]": 
                    token = Token(TokenType.CLOSE_PARENT, self.position, char)
                    self.advance()
                case "\"" | "'":
                    token = Token(TokenType.QUOTE, self.position, char)
                    self.advance()
                case "«":
                    token = Token(TokenType.OPEN_QUOTE, self.position, char)
                    self.advance()
                case "»":
                    token = Token(TokenType.CLOSE_QUOTE, self.position, char)
                    self.advance()
                case "." | "!" | "?":
                    token = Token(TokenType.ENDING_PUNCTUATION, self.position, char)
                    self.advance()
                case "," | ";" | ":" | "/" | "-":
                    token = Token(TokenType.PUNCTUATION, self.position, char)
                    self.advance()
                case " ":
                    # token = Token(TokenType.SPACE, self.position, char)
                    self.advance()
                case _:
                    if char == " ":
                        self.advance()
                        continue
                
                    word = char
                    start = self.position

                    # TODO: seems dumb, figure out a better way to -
                    while (
                        (symbol := self.peek_next()) not in Alphabet.punctuation 
                        and symbol not in Alphabet.separators 
                        or symbol == '-'
                    ):
                        word += symbol
                        self.advance()
                    
                    token = Token(TokenType.WORD, start, word)
                    self.advance()
            
            if token:
                tokens.append(token)

        tokens.append(Token(TokenType.EOF, self.position, None))
        return tokens


# ===== Parsing entities ===== #
class Filterable(abc.ABC):
    @abc.abstractmethod    
    def filter(self, _filter: Callable[[Any], bool]):
        pass

    @abc.abstractmethod    
    def empty(self) -> bool:
        pass


class Entity(Filterable):
    def __init__(self, literal):
        self.literal: str = literal

    def filter(self, _filter: Callable):
        self.literal = ''.join(filter(_filter, self.literal))

    def empty(self) -> bool:
        return len(self.literal) == 0

    def __str__(self):
        return f"{self.literal}"
    
    def __repr__(self):
        return f"({self.__class__.__name__}, {self.literal})"


class Punctuation(Entity):
    pass


class Word(Entity):
    pass


ContentElement: TypeAlias = Union["Sentence", "Punctuation", "SubText"]
class Sentence(Filterable):
    def __init__(self, content, ending):
        self.content: list[ContentElement] = content
        self.ending: list[Punctuation] = ending
    
    def empty(self) -> bool:
        return len(self.content) == 0
    
    def filter(self, _filter: Callable):
        for c in self.content:
            c.filter(_filter)

        elements_to_remove = []
        for i in range(len(self.content)):
            if self.content[i].empty():
                if i > 0 and isinstance(self.content[i-1], Punctuation):
                    elements_to_remove.append(i-1)
                elements_to_remove.append(i)
        
        for i in elements_to_remove[::-1]:
            self.content.pop(i)
        # self.content = list(filter(
        #     lambda c: not c.empty(), self.content
        # ))

        while self.content and isinstance(self.content[-1], Punctuation):
            self.content.pop()
    
    def __str__(self):
        r = ""
        for i, c in enumerate(self.content):
            if i > 0 and (isinstance(c, Word) or isinstance(c, SubText) or (isinstance(c, Punctuation) and c.literal == '-')):
                r += ' '
            r += str(c)
        r += ''.join(str(e) for e in self.ending)
        return r
        
    def __repr__(self):
        return f"({self.__class__.__name__}, ending={self.ending}, content={self.content}"
    
    @staticmethod
    def _add_space_before(element: ContentElement) -> bool:
        pass
    

class Text(Filterable):
    def __init__(self, sentences=None):
        self.sentences: list[Sentence] = sentences or []

    def empty(self) -> bool:
        return len(self.sentences) == 0
    
    def filter(self, _filter):
        for s in self.sentences:
            s.filter(_filter)
        self.sentences = list(filter(
            lambda s: not s.empty(), self.sentences
        ))

    def __str__(self):
        return " ".join(str(c) for c in self.sentences)
    
    def __repr__(self):
        return f"({self.__class__.__name__}, sentences={self.sentences})"


class SubText(Text):
    def __init__(self, sentences=None, before="", after=""):
        super().__init__(sentences)

        self.before: str = before
        self.after: str = after

    def __str__(self):
        return self.before + super().__str__() + self.after
        

# ===== Parser ===== #
class Parser:
    def __init__(self):
        self.position: int = 0
        self.tokens: list[Token] = None

        self.quoted: bool = False

    def _init(self, tokens):
        self.position = 0
        self.tokens = tokens

        self.quoted = False

    def advance(self):
        self.position += 1
    
    @property
    def current(self):
        return self.tokens[self.position]

    @property
    def previous(self):
        return self.tokens[self.position - 1]
    
    def consume(self, _type: TokenType):
        if self.current.type == _type:
            self.advance()
        else:
            raise TypeError()
    
    def match(self, types: list[TokenType]) -> bool:
        for _type in types:
            if self.current.type == _type:
                self.advance()
                return True
        return False
    
    def parse(self, tokens) -> Text:
        self._init(tokens)
        return self.text()
    
    def text(self) -> Text:
        text = Text()

        while not self.match([TokenType.EOF, TokenType.CLOSE_PARENT, TokenType.CLOSE_QUOTE, TokenType.QUOTE]):
            sentence = self.sentence()
            text.sentences.append(sentence)
        
        self.position -= 1
        return text
    
    def sentence(self) -> Sentence:
        content = self.content()

        ending = []
        while self.match([TokenType.ENDING_PUNCTUATION]):
            ending.append(Punctuation(self.previous.literal))
        
        return Sentence(content, ending)
    
    def content(self) -> list[Word, Punctuation, Text]:
        content = []

        while (
            self.match([TokenType.WORD, TokenType.PUNCTUATION, TokenType.OPEN_PARENT, TokenType.OPEN_QUOTE]) or 
            (not self.quoted and self.match([TokenType.QUOTE]))
        ):
            prev = self.previous

            match prev.type:
                case TokenType.OPEN_PARENT:
                    before = prev.literal
                    text = self.text()
                    after = self.current.literal

                    self.consume(TokenType.CLOSE_PARENT)
                    content.append(SubText(text.sentences, before, after))
                case TokenType.OPEN_QUOTE:
                    before = prev.literal
                    text = self.text()
                    after = self.current.literal
                    
                    self.consume(TokenType.CLOSE_QUOTE)
                    content.append(SubText(text.sentences, before, after))
                case TokenType.QUOTE:
                    self.quoted = True

                    before = prev.literal
                    text = self.text()
                    after = self.current.literal
                    
                    self.consume(TokenType.QUOTE)
                    content.append(SubText(text.sentences, before, after))

                    self.quoted = False
                case TokenType.WORD:
                    word = Word(prev.literal)
                    content.append(word)
                case TokenType.PUNCTUATION | TokenType.QUOTE:
                    punct = Punctuation(prev.literal)
                    content.append(punct)
        
        return content


# ===== Processor ===== #
class DialecticParagraphProcessor(BaseParagraphProcessor):
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.parser = Parser()

    def process(self, paragraph: str) -> str:
        paragraph = self._preprocess(paragraph)
        tokens = self.tokenizer.tokenise(paragraph)
        text = self.parser.parse(tokens)
        text.filter(lambda s: s in Alphabet.allowed_symbols)

        return str(text)
    
    def _preprocess(self, paragraph: str) -> str:
        paragraph = paragraph.strip()
        if not paragraph.endswith(tuple(Alphabet.ending_punctuation)):
            paragraph += '.'

        # Replace symbols with a common alternatives
        translation = {
            ord('—'): ord('-'),
            ord('–'): ord('-'),
            160: ord(' ')
        }
        paragraph = paragraph.translate(translation)
    
        return paragraph
    
