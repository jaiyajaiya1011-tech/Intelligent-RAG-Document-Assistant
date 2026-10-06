import streamlit as st
from dotenv import load_dotenv
from rag_engine import RAGEngine

load_dotenv()

st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📚",
    layout="wide"
)

try:
    with open("static/style.css", "r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )
except FileNotFoundError:
    pass


if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = RAGEngine()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "document_processed" not in st.session_state:
    st.session_state.document_processed = False

if "filename" not in st.session_state:
    st.session_state.filename = ""


engine = st.session_state.rag_engine


st.title("📚 DocuMind AI")
st.caption("Intelligent RAG Document Assistant")

st.divider()


with st.sidebar:

    st.header("📄 Upload Document")

    uploaded_file = st.file_uploader(
        "Choose a PDF",
        type=["pdf"]
    )

    if uploaded_file is not None:

        st.write(f"📎 {uploaded_file.name}")

        if st.button(
            "⚙️ Process Document",
            use_container_width=True
        ):

            with st.spinner("Processing your document..."):

                try:

                    result = engine.process_document(
                        uploaded_file
                    )

                    st.session_state.document_processed = True
                    st.session_state.filename = result["filename"]

                    st.success(
                        f"✅ {result['filename']} processed successfully!"
                    )

                    st.info(
                        f"📄 Pages: {result['pages']}\n\n"
                        f"🔹 Chunks: {result['chunks']}"
                    )

                except Exception as e:

                    st.error(
                        f"❌ Processing error: {str(e)}"
                    )


    st.divider()


    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.rerun()


if st.session_state.document_processed:

    st.success(
        f"📚 Ready! Document: {st.session_state.filename}"
    )

else:

    st.info(
        "👈 Upload a PDF and click Process Document to start."
    )


for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):

            with st.expander("📚 Sources"):

                for source in message["sources"]:

                    if isinstance(source, dict):

                        page = source.get(
                            "page",
                            "Unknown"
                        )

                        source_text = source.get(
                            "text",
                            ""
                        )

                        st.write(
                            f"📄 Page {page}"
                        )

                        if source_text:

                            st.caption(
                                source_text[:300]
                            )

                    else:

                        st.write(
                            f"📄 {str(source)[:300]}"
                        )


question = st.chat_input(
    "Ask DocuMind AI about your document..."
)


if question:

    if not st.session_state.document_processed:

        st.warning(
            "⚠️ Please upload and process a PDF first."
        )

        st.stop()


    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    with st.chat_message("user"):

        st.markdown(question)


    with st.chat_message("assistant"):

        with st.spinner(
            "🤖 DocuMind AI is thinking..."
        ):

            try:

                results = engine.search(
                    question,
                    top_k=5
                )


                answer = engine.ask(
                    question,
                    results
                )


                if not isinstance(answer, str):

                    answer = str(answer)


                st.markdown(answer)


                if results:

                    with st.expander("📚 Sources"):

                        for source in results:

                            if isinstance(source, dict):

                                page = source.get(
                                    "page",
                                    "Unknown"
                                )

                                source_text = source.get(
                                    "text",
                                    ""
                                )

                                st.write(
                                    f"📄 Page {page}"
                                )

                                if source_text:

                                    st.caption(
                                        source_text[:300]
                                    )

                            else:

                                st.write(
                                    f"📄 {str(source)[:300]}"
                                )


                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": results
                    }
                )


            except Exception as e:

                error_message = f"❌ Error: {str(e)}"

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                        "sources": []
                    }
                )


st.divider()

st.subheader("💡 Example Questions")

st.write("• What is this document about?")
st.write("• What are the main topics discussed?")
st.write("• Explain the important points in the document.")
st.write("• What is phishing?")