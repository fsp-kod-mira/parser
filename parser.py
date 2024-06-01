from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsNERTagger,
    NewsMorphTagger,
    NewsSyntaxParser,
    NamesExtractor,
    Doc
)
import re

month_to_number = {
    "январь": "01", "февраль": "02", "март": "03", "апрель": "04", "май": "05", "июнь": "06",
    "июль": "07", "август": "08", "сентябрь": "09", "октябрь": "10", "ноябрь": "11", "декабрь": "12",
    "янв": "01", "фев": "02", "мар": "03", "апр": "04", "май": "05", "июн": "06",
    "июл": "07", "авг": "08", "сен": "09", "окт": "10", "ноя": "11", "дек": "12"
}


def convert_month(month):
    return month_to_number.get(month.lower(), month)


class Parser:
    def __init__(self):
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        self.emb = NewsEmbedding()
        self.ner_tagger = NewsNERTagger(self.emb)
        self.names_extractor = NamesExtractor(self.morph_vocab)
        self.syntax_parser = NewsSyntaxParser(self.emb)
        self.morph_tagger = NewsMorphTagger(self.emb)

    async def extract_with_regex(self, pattern, text):
        match = re.search(pattern, text)
        if match:
            return match.group()
        return None

    async def extract_name(self, text):
        matches = self.names_extractor(text)
        for match in matches:
            return f"{match.fact.last} {match.fact.first} {match.fact.middle}"
        return None

    async def extract_phone(self, text):
        pattern = r'\+?\d[\d\-\(\) ]{9,}\d'
        return await self.extract_with_regex(pattern, text)

    async def extract_email(self, text):
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return await self.extract_with_regex(pattern, text)

    async def extract_date_of_birth(self, text):
        pattern = r'\b(\d{1,2})(?:\s|\.)?(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря|\d{1,2})(?:\s|\.)?(\d{4})\b'
        return await self.extract_with_regex(pattern, text)

    async def extract_living(self, text):
        doc = Doc(text)
        doc.segment(self.segmenter)
        doc.tag_morph(self.morph_tagger)
        doc.parse_syntax(self.syntax_parser)
        doc.tag_ner(self.ner_tagger)

        locations = []

        for span in doc.spans:
            if span.type in ['LOC', 'GPE']:
                span.normalize(self.morph_vocab)
                locations.append(span.normal)
        return ",".join(locations)

    async def extract_work(self, text):
        work_pattern = re.compile(
            r'([А-ЯЁа-яё\w\s\"\'\.]+)\s+([а-яё]+\s\d{4})\s+-\s+([а-яё]+\s\d{4}|настоящее время).*?(Санкт-Петербург|Москва|[А-ЯЁа-яё\w\s\"\'\.]+)\s([А-ЯЁа-яё\w\s\-\(\)]+)',
            re.IGNORECASE | re.DOTALL
        )

        work_experiences = []

        for match in work_pattern.finditer(text):
            company = match.group(1).strip()
            start_month, start_year = match.group(2).split()
            start_month = convert_month(start_month)
            end_date = match.group(3).strip()

            if end_date.lower() != "настоящее время":
                end_month, end_year = end_date.split()
                end_month = convert_month(end_month)
                end_date = f"{end_month}.{end_year}"

            position = match.group(5).strip()
            work_experiences.append(
                f"{company} {start_month}.{start_year} - {end_date}, {position}")

        return work_experiences
