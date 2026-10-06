import os
import io

from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()


class RAGEngine:

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Please check your .env file."
            )

        self.client = Groq(api_key=api_key)

        self.model = "openai/gpt-oss-20b"

        self.documents = []
        self.chunks = []
        self.vectorizer = None
        self.chunk_vectors = None
        self.current_filename = ""

    def process_document(self, uploaded_file):

        file_bytes = uploaded_file.getvalue()

        reader = PdfReader(
            io.BytesIO(file_bytes)
        )

        self.documents = []
        self.chunks = []
        self.current_filename = uploaded_file.name

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = page.extract_text()

            if text and text.strip():

                text = self.clean_text(text)

                self.documents.append(
                    {
                        "text": text,
                        "page": page_number,
                        "source": uploaded_file.name
                    }
                )

        if not self.documents:

            raise ValueError(
                "No readable text was found in this PDF."
            )

        self.create_chunks()

        if not self.chunks:

            raise ValueError(
                "Could not create searchable text chunks."
            )

        texts = [
            chunk["text"]
            for chunk in self.chunks
        ]

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000
        )

        self.chunk_vectors = (
            self.vectorizer.fit_transform(texts)
        )

        return {
            "success": True,
            "filename": uploaded_file.name,
            "pages": len(reader.pages),
            "chunks": len(self.chunks)
        }

    def clean_text(self, text):

        text = text.replace("\n", " ")

        text = " ".join(
            text.split()
        )

        return text.strip()

    def create_chunks(
        self,
        chunk_size=1000,
        overlap=200
    ):

        self.chunks = []

        for document in self.documents:

            text = document["text"]
            page = document["page"]
            source = document["source"]

            start = 0

            while start < len(text):

                end = start + chunk_size

                chunk_text = text[
                    start:end
                ].strip()

                if chunk_text:

                    self.chunks.append(
                        {
                            "text": chunk_text,
                            "page": page,
                            "source": source
                        }
                    )

                if end >= len(text):

                    break

                start = end - overlap

    def search(
        self,
        question,
        top_k=5
    ):

        if not self.chunks:

            return []

        if (
            self.vectorizer is None
            or self.chunk_vectors is None
        ):

            return []

        question_vector = (
            self.vectorizer.transform(
                [question]
            )
        )

        similarities = cosine_similarity(
            question_vector,
            self.chunk_vectors
        )[0]

        ranked_indices = (
            similarities.argsort()[::-1]
        )

        results = []

        for index in ranked_indices[:top_k]:

            score = float(
                similarities[index]
            )

            if score <= 0:

                continue

            chunk = self.chunks[index]

            results.append(
                {
                    "text": chunk["text"],
                    "page": chunk["page"],
                    "source": chunk["source"],
                    "score": score
                }
            )

        return results

    def ask(
        self,
        question,
        context=None
    ):

        if context is None:

            context = self.search(
                question,
                top_k=5
            )

        if not context:

            return (
                "I couldn't find relevant "
                "information in the uploaded document."
            )

        context_text = "\n\n".join(
            [
                f"[Page {item['page']}]\n"
                f"{item['text']}"
                for item in context
                if isinstance(item, dict)
            ]
        )

        prompt = f"""
You are DocuMind AI, an intelligent RAG document assistant.

Answer the user's question using ONLY the information
provided in the document context.

If the answer is not available in the context, say:
"I couldn't find that information in the uploaded document."

Do not invent or assume information.

Give a clear and easy-to-understand answer.

Document Context:

{context_text}

User Question:

{question}

Answer:
"""

        try:

            response = (
                self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful document "
                                "question-answering assistant. "
                                "Use only the provided document "
                                "context."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.2,
                    max_tokens=1000
                )
            )

            answer = (
                response
                .choices[0]
                .message
                .content
            )

            if not answer:

                return (
                    "I couldn't generate an answer."
                )

            return answer.strip()

        except Exception as e:

            return f"Groq API error: {str(e)}"

    def get_sources(self, results):

        sources = []

        for result in results:

            if isinstance(result, dict):

                sources.append(
                    {
                        "source": result.get(
                            "source",
                            ""
                        ),
                        "page": result.get(
                            "page",
                            "Unknown"
                        ),
                        "score": result.get(
                            "score",
                            0
                        ),
                        "text": result.get(
                            "text",
                            ""
                        )
                    }
                )

        return sources

    def clear_document(self):

        self.documents = []
        self.chunks = []
        self.vectorizer = None
        self.chunk_vectors = None
        self.current_filename = ""