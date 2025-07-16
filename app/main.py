import os
from fastapi import FastAPI
from pydantic import BaseModel
from .rag import build_email_reply_chain
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


# Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # oder ["*"] für Entwicklung
    allow_credentials=True,
    allow_methods=["*"],  # wichtig: erlaubt auch OPTIONS
    allow_headers=["*"],
)
# Initialize the LangChain QA chain with the OpenAI API key
reply_chain = build_email_reply_chain()

class QueryInput(BaseModel):
    query: str

@app.post("/generate-reply")
def generate_reply(data: QueryInput):
    received_email = data.query
    reply = reply_chain.invoke(received_email)
    return {"reply": reply}
