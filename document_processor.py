import re

from pypdf import PdfReader


class DocumentProcessor:

    def __init__(self):
        self.chunks = []

    def process_pdf(self, uploaded_file):

        self.chunks = []

        reader = PdfReader(uploaded_file)

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = page.extract_text()

            if not text:
                continue

            text = self.clean_text(text)

            chunks = self.create_chunks(
                text,
                page_number
            )

            self.chunks.extend(chunks)

        return self.chunks

    def clean_text(self, text):

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    def create_chunks(
        self,
        text,
        page,
        chunk_size=800,
        overlap=150
    ):

        chunks = []

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk = text[start:end]

            if chunk.strip():

                chunks.append({
                    "text": chunk,
                    "page": page
                })

            start += chunk_size - overlap

        return chunks

    def search(self, query, top_k=5):

        if not self.chunks:
            return []

        query_words = set(
            self.tokenize(query)
        )

        scored_chunks = []

        for chunk in self.chunks:

            words = set(
                self.tokenize(chunk["text"])
            )

            score = len(
                query_words.intersection(words)
            )

            scored_chunks.append(
                (score, chunk)
            )

        scored_chunks.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return [
            item[1]
            for item in scored_chunks[:top_k]
        ]

    def tokenize(self, text):

        return re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower()
        )