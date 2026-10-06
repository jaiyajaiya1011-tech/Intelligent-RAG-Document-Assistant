# 📚 DocuMind AI – Intelligent RAG Document Assistant

DocuMind AI is an intelligent document assistant that allows users to upload PDF documents and ask questions about their content.

The application uses Retrieval-Augmented Generation (RAG) to retrieve relevant information from the uploaded document and generate clear answers using the Groq API.

## 🚀 Features

- 📄 Upload PDF documents
- 🔍 Search relevant document content
- 🤖 AI-powered question answering
- 📚 Page-based source references
- 💬 Interactive chat interface
- ⚡ Fast responses using Groq
- 🌐 Streamlit web application

## 🛠️ Technologies Used

- Python
- Streamlit
- Groq API
- Retrieval-Augmented Generation (RAG)
- TF-IDF
- Cosine Similarity
- PyPDF
- Scikit-learn

## 📂 Project Structure

```text
Intelligent-RAG-Document-Assistant/
│
├── app.py
├── rag_engine.py
├── document_processor.py
├── requirements.txt
├── .gitignore
│
└── static/
    └── style.css
⚙️ How It Works
Upload a PDF document.

The document text is extracted and divided into smaller chunks.

TF-IDF is used to identify relevant document content.

The user's question is matched with relevant chunks.

The retrieved content is provided to the AI model.

DocuMind AI generates an answer based on the retrieved document content.

Relevant page sources are displayed to the user.

🔐 API Key Setup
Create a .env file locally and add:

GROQ_API_KEY=your_groq_api_key
For Streamlit deployment, add the API key through Streamlit Secrets.

Do not upload the .env file or expose your API key publicly.

▶️ Run Locally
Install the required packages:

pip install -r requirements.txt
Run the application:

streamlit run app.py
🌐 Deployment
The application can be deployed using Streamlit Community Cloud.

🎯 Project Objective
The goal of DocuMind AI is to make document-based information retrieval easier by allowing users to interact with their PDF documents through a simple conversational interface.

👩‍💻 Developed By
Jaiya Dharshini RS
