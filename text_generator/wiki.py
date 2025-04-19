import re
import dataclasses
import unicodedata

import requests
from bs4 import BeautifulSoup, Tag


@dataclasses.dataclass
class Section:
    title: str
    level: int

    paragraphs: list[str] = dataclasses.field(default_factory=list)
    subsections: list['Section'] = dataclasses.field(default_factory=list)

    def get_nested_paragraphs(self):
        paragraphs = self.paragraphs.copy()

        for subsection in self.subsections:
            paragraphs.extend(subsection.get_nested_paragraphs())
        return paragraphs


@dataclasses.dataclass
class Page:
    title: str = ""
    section: Section = Section('Main', 1)
    # sections: list[Section] = dataclasses.field(default_factory=list)

    def get_all_paragraphs(self):
        return self.section.get_nested_paragraphs()


class WikipediaFetcher:
    title_url = 'https://ru.wikipedia.org/w/api.php?origin=*&action=query&format=json&list=random&rnlimit=1&rnnamespace=0'
    article_url = 'https://ru.wikipedia.org/w/api.php?origin=*&action=parse&format=json&page={title}&prop=text'

    def get_article(self, title) -> Page:
        request = requests.post(self.article_url.format(title=title))
        result = request.json()
        html = result['parse']['text']['*']

        page = self._parse_page(html)
        page.title = title
        return page
    
    def get_random_article(self) -> Page:
        title = self._get_random_title()
        return self.get_article(title)
    
    def get_random_text(self) -> str:
        return ' '.join(self.get_random_article().get_all_paragraphs())
    
    def _get_random_title(self) -> str:
        request = requests.post(self.title_url)
        result = request.json()
        title = result['query']['random'][0]['title']

        return title

    def _parse_page(self, html) -> Page:
        bs = BeautifulSoup(html, 'html.parser')

        main_tag: Tag = bs.find()
        content: list[Tag] = main_tag.find_all(
            lambda t: t.name == 'p' or t.name == 'dd' or (t.name == 'div' and 'class' in t.attrs and 'heading' in t['class']) 
        )
        
        page = Page()

        # Get sections
        sections = [page.section]
        for tag in content:
            if tag.name == 'p' or tag.name == 'dd':
                paragraph = tag.get_text()
                paragraph = self._process_paragraph(paragraph)
                sections[-1].paragraphs.append(paragraph)
            else:
                heading_level = int(str(filter(lambda s: s.isdigit(), tag.attrs)))
                sections.append(Section(tag.get_text(), heading_level))
        sections = list(filter(self._filter_section, sections[1:]))
        
        # Create tree structure
        stack = [page.section]
        for section in sections:
            level = section.level

            while stack[-1].level >= level:
                stack.pop()

            parent = stack[-1]
            parent.subsections.append(section)          
            stack.append(section)
        
        return page
    
    @staticmethod
    def _process_paragraph(paragraph) -> str:
        # Uncompress unicode characters
        paragraph = unicodedata.normalize('NFD', paragraph)

        # Remove sources (vile!)
        paragraph = re.sub('\[\d+\]', '', paragraph)

        return paragraph

    @staticmethod
    def _filter_section(section: Section) -> bool:
        return section.title != 'Примечания'
