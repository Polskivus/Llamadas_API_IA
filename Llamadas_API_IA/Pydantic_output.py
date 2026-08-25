from pydantic import BaseModel, Field, EmailStr
from typing import List, Literal, Optional
from datetime import date
from ollama import chat, Client

client = Client(
    host="http://192.168.1.147:1234/"
)

class UserInput(BaseModel):
    name: str
    email: EmailStr
    query: str
    order_id: Optional[int] = Field(
        None,
        description="5-digit order number (cannot start with 0)",
        ge=10000,
        le=99999
    )
    purchase_date: Optional[date] = None

class CustomerQuery(UserInput):
    priority: str = Field(
        ..., description="Priority level: low, medium, high"
    )
    category: Literal[
        'refund_request', 'information_request', 'other'
    ] = Field(..., description="Query category")
    is_complaint: bool = Field(
        ..., description="Whether this is a complaint"
    )
    tags: List[str] = Field(..., description="Relevant keyword tags")

user_input_json = '''{
    "name": "Joe User",
    "email": "joe.user@example.com",
    "query": "I ordered a new computer monitor and it arrived with the screen cracked. This is the second time this has happened. I need a replacement ASAP.",
    "order_id": 12345,
    "purchase_date": "2025-12-31"
}'''

user_input = UserInput.model_validate_json(user_input_json)

prompt = (
    f"Analyze the following customer query {user_input} "
    f"and provide a structured response."
)

def call_llm_output_structured(prompt, data_model, model="qwen2.5-7b-instruct"):
    response = client.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        format=CustomerQuery.model_json_schema()
    )
    return data_model.model_validate_json(response.message.content)

customer_query = call_llm_output_structured(prompt, CustomerQuery)
#print(type(customer_query))
#print(customer_query.model_dump_json(indent=2))

