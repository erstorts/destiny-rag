from fastapi import FastAPI, HTTPException
from llm import prompt_llm, response_llm
from search import search
import segment.analytics as analytics
import os
import json
from pydantic import BaseModel

analytics.write_key = os.getenv("SEGMENT_API_KEY")
app = FastAPI()

class LLMRequest(BaseModel):
    user_input: str
    num_results: int
    message_counter: int
    input_messages: list


@app.get("/llm")
def read(llm_request: LLMRequest):
    search_results = search(llm_request.user_input, llm_request.num_results, llm_request.message_counter)
    prompt = prompt_llm(search_results, llm_request.user_input, llm_request.num_results)
    input_messages = llm_request.input_messages + [{"role": "user", "content": prompt}]
    response = response_llm(input_messages, llm_request.message_counter)
    return response
