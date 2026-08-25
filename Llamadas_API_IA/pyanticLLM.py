from ollama import chat
from pydantic import BaseModel, ValidationError, Field, EmailStr
from typing import List, Literal, Optional
import json
from datetime import date

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

user_input_json = """
{
    "name": "Joe User",
    "email": "joe.user@example.com",
    "query": "I forgot my password.",
    "order_number": null,
    "purchase_date": null
}
"""

user_input = UserInput.model_validate_json(user_input_json) # Validamos el input del user y lo pasamos al JSON bueno

example_response_structure = f"""{{
    name="Example User",
    email="user@example.com",
    query="I ordered a new computer monitor and it arrived with the screen cracked. I need to exchange it for a new one.",
    order_id=12345,
    purchase_date="2025-12-31",
    priority="medium",
    category="refund_request",
    is_complaint=True,
    tags=["monitor", "support", "exchange"] 
}}"""

# Prompt para el modelo, para que nos de el JSON como deseariamos que nos devuelva
prompt = f"""
Please analyze this user query\n {user_input.model_dump_json(indent=2)}:

Return your analysis as a JSON object matching this exact structure 
and data types:
{example_response_structure}

Respond ONLY with valid JSON. Do not include any explanations or 
other text or formatting before or after the JSON object.
"""

def call_llm(prompt, model="llama3.2:3b"):
    response = chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.message.content

# response_content = call_llm(prompt)

# Intentar parsear la respuesta del LLM al CustomerQuery

#valid_data = CustomerQuery.model_validate_json(response_content) Esto da error por que no esta bien validado

def validate_with_model(data_model, llm_response):
    try:
        validated_data = data_model.model_validate_json(llm_response)
        print("data validation successful!")
        print(validated_data.model_dump_json(indent=2))
        return validated_data, None
    except ValidationError as e:
        print(f"error validating data: {e}")
        error_message = (
            f"This response generated a validation error: {e}."
        )
        return None, error_message

""" validated_data, validation_error = validate_with_model(
    CustomerQuery, response_content
) """

# Vamos a hacer una funcion para que el LLM itere hasta conseguir la respuesta correcta
def create_retry_promt(original_prompt, original_response, error_message):
    retry_prompt = f"""
This is a request to fix an error in the structure of an llm_response.
Here is the original request:
<original_prompt>
{original_prompt}
</original_prompt>

Here is the original llm_response:
<llm_response>
{original_response}
</llm_response>

This response generated an error: 
<error_message>
{error_message}
</error_message>

Compare the error message and the llm_response and identify what 
needs to be fixed or removed
in the llm_response to resolve this error. 

Respond ONLY with valid JSON. Do not include any explanations or 
other text or formatting before or after the JSON string.
"""
    return retry_prompt

""" validation_rety_promt = create_retry_promt(
    original_prompt=prompt,
    original_response=response_content,
    error_message=validation_error
)

validation_rety_response = call_llm(validation_rety_promt)
# print(validation_rety_response)

validated_data, validation_error = validate_with_model(
    CustomerQuery, validation_rety_response
)

second_validation_rety_promt = create_retry_promt(
    original_prompt=validation_rety_promt,
    original_response=validation_rety_response,
    error_message=validation_error
)

# print(second_validation_rety_promt)

second_validation_rety_response = call_llm(
    second_validation_rety_promt
)
print(second_validation_rety_response) """

# Vamos a hacer todo lo comentado en una funcion, para poder repetir las veces que haga falta

def validate_llm_response(prompt, data_model ,n_rentry=5, model="llama3.2:3b"):
    response_content = call_llm(prompt, model=model)
    current_prompt = prompt

    for attempt in range(n_rentry +1):

        validated_data, validation_error = validate_with_model(data_model, response_content)

        if validation_error:
            if attempt < n_rentry:
                if attempt < n_rentry:
                    print(f"retry {attempt} of {n_rentry} failed, trying again...")
                else:
                    print(f"Max retries reached. Last error: {validation_error}")
                    return None, (f"Max retries reached. Last error: {validation_error}"
                )
            validation_rentry_prompt = create_retry_promt(
                original_prompt=current_prompt,
                original_response=response_content,
                error_message=validation_error
            )
            response_content = call_llm(
                validation_rentry_prompt, model=model
            )
            current_prompt = validation_rentry_prompt
            continue

        return validated_data, None

validated_data, error = validate_llm_response(prompt, CustomerQuery)

data_model_schema = json.dumps(
    CustomerQuery.model_json_schema(), indent=2
)
print(data_model_schema)

prompt2 = f"""
Please analyze this user query\n {user_input.model_dump_json(indent=2)}:

Return your analysis as a JSON object matching the following schema:
{data_model_schema}

Respond ONLY with valid JSON. Do not include any explanations or 
other text or formatting before or after the JSON object.
"""

final_analysis, error = validate_llm_response(
    prompt2, CustomerQuery
)