import os
import sys
from functools import wraps

import torch

sys.path.append("src")
from dotenv import load_dotenv

load_dotenv()
from flask import Flask, jsonify, request
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from polish_kg_langchain import InstructionStripper

# === Config ===
API_TOKEN = os.environ.get("API_TOKEN")  # Set securely in env
MODEL_NAME = "CYFRAGOVPL/Llama-PLLuM-8B-instruct"  # Replace with your actual model


# === Auth Decorator ===
def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if token != f"Bearer {API_TOKEN}":
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)

    return decorated


# === Hugging Face + LangChain Chat Wrapper ===
def create_chat_huggingface(llm, tokenizer, **kwargs) -> ChatHuggingFace:
    args = {
        "model": llm,
        "tokenizer": tokenizer,
        "device": "cuda",
        "max_new_tokens": 1000,
        "do_sample": True,
        "temperature": 0.8,
    }
    args.update(kwargs)

    text_gen_pipeline = pipeline("text-generation", **args)

    langchain_pipe = HuggingFacePipeline(pipeline=text_gen_pipeline)
    chat = ChatHuggingFace(llm=langchain_pipe, callbacks=[InstructionStripper()])

    return chat


# === Model Load ===
print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
print("Tokenizer loaded. Loading model...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME, torch_dtype=torch.float16
).cuda()
chat_model = create_chat_huggingface(model, tokenizer)
print("Model loaded.")

# === Flask App ===
app = Flask(__name__)


@app.route("/chat", methods=["POST"])
@require_token
def chat_endpoint():
    data = request.get_json()
    if not data or "messages" not in data:
        return jsonify({"error": "Missing 'messages' field"}), 400

    messages = data["messages"]
    if not isinstance(messages, list) or not all(
        isinstance(m, list) and len(m) == 2 for m in messages
    ):
        return (
            jsonify({"error": "'messages' must be a list of [role, content] pairs"}),
            400,
        )

    try:
        # Convert to list of tuples
        messages_tuples = [tuple(m) for m in messages]

        # Generate prompt using LangChain
        prompt = ChatPromptTemplate.from_messages(messages_tuples)
        formatted_messages = prompt.format_messages()

        # Run inference
        response = chat_model.invoke(formatted_messages)
    except Exception as e:
        return jsonify({"error": f"Model generation failed: {str(e)}"}), 500

    return jsonify({"response": response.content})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
