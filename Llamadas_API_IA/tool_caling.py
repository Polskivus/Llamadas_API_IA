from pydantic_ai import Agent
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Literal, List, Optional
from datetime import date, datetime
import json
from openai import OpenAI

client = OpenAI(
    base_url="http://192.168.1.147:1234/v1",
    api_key="xxxxxxx"
)

class UserInput(BaseModel):
    name: str = Field(..., description="User's name")
    email: EmailStr = Field(..., description="User's email address")
    query: str = Field(..., description="User's query")
    order_id: Optional[str] = Field(
        None,
        description="Order ID if available (format: ABC-12345)"
    )
    # Validate order_id format (e.g., ABC-12345)
    @field_validator("order_id")
    def validate_order_id(cls, order_id):
        import re
        if order_id is None:
            return order_id
        pattern = r"^[A-Z]{3}-\d{5}$"
        if not re.match(pattern, order_id):
            raise ValueError(
                "order_id must be in format ABC-12345 "
                "(3 uppercase letters, dash, 5 digits)"
            )
        return order_id
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

def validate_user_input(user_json: str):
    try:
        user_input = (
            UserInput.model_validate_json(user_json)
        )
        print("User input validated...")
        return user_input
    except Exception as e:
        print(f" Unexpected error: {e}")
        return None

def create_customer_query(valid_user_json: str) -> CustomerQuery:
    customer_query_agent = Agent(
        model="qwen2.5-7b-instruct",
        output_type=CustomerQuery,
    )
    response = customer_query_agent.run_sync(valid_user_json)
    print("CustomerQuery generated...")
    return response.output

user_input_json = '''
{
    "name": "Joe User",
    "email": "joe@example.com",
    "query": "When can I expect delivery of the headphones I ordered?",
    "order_id": "ABC-12345",
    "purchase_date": "2025-12-01"
}
'''

valid_data = validate_user_input(user_input_json).model_dump_json()
customer_query = create_customer_query(valid_data)
print(type(customer_query))
print(customer_query.model_dump_json(indent=2))