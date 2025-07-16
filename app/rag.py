from langchain_community.llms import OpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.chat_models import init_chat_model

from sentence_transformers import SentenceTransformer
import numpy as np

import getpass
import os
from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
DATA_PATH=os.getenv("DATA_PATH")


# Custom embeddings class
class SentenceTransformersEmbeddings:
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list) -> np.ndarray:
        return self.model.encode(texts, convert_to_numpy=True)

    def embed_query(self, query: str) -> np.ndarray:
        return self.model.encode([query], convert_to_numpy=True)[0]

def build_email_reply_chain():
    # Load your own sent emails as documents for grounding
    embeddings = SentenceTransformersEmbeddings('all-MiniLM-L6-v2')  # Local model
    vector_store = InMemoryVectorStore(embeddings)

    loader = TextLoader(DATA_PATH)
    documents = loader.load()
    # Set up OpenAI LLM
    llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

    # New prompt — NOT a Q&A prompt
    prompt_template = """
    You are a helpful assistant that writes email replies.

    Use the writing style and tone from the following documents (examples of previous emails):

    {context}

    Here's a new email the user received:
    ---
    {question}
    ---

    Write a coherent and thoughtful reply that reflects the user's past style. Stay polite, smart, and human.

    Your reply:
    """

    prompt = PromptTemplate(
        input_variables=["question", "context"],
        template=prompt_template.strip()
    )

    # RAG-style chain that injects style context into the reply
    reply_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vector_store.as_retriever(),
        chain_type="stuff",
        return_source_documents=False,
        chain_type_kwargs={"prompt": prompt}
    )

    return reply_chain
