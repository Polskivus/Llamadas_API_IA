from openai import OpenAI
from pydantic import BaseModel, Field, EmailStr
from typing import List, Literal, Optional
from datetime import date

client = OpenAI(
    base_url="http://192.168.1.147:1234/v1",
    api_key="xxxxxxx"
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

response = client.beta.chat.completions.parse(
    model="qwen2.5-7b-instruct",
    messages=[{"role": "user", "content": prompt}],
    response_format=CustomerQuery
)

response_content = response.choices[0].message.content
#print(type(response_content))
#print(response_content)

valid_data = CustomerQuery.model_validate_json(response_content)
#print(type(valid_data))
#print(valid_data.model_dump_json(indent=2))

""" response2 = client.responses.parse(
    model="qwen2.5-7b-instruct",
    input=[{"role": "user", "content": prompt}],
    text_format=CustomerQuery
)

print(type(response2)) """

def print_class_inheritance(llm_response):
    for cls in type(llm_response).mro():
        print(f"{cls.__module__}.{cls.__name__}")

print_class_inheritance(response)

print(type(response.output_parsed))
print(response.output_parsed.model_dump_json(indent=2))