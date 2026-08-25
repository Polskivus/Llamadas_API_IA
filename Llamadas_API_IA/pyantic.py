from pydantic import BaseModel, ValidationError, EmailStr, Field
from typing import Optional
from datetime import date
import json

# Definimos el modelo de la estructura del JSON
class UserInput(BaseModel):
    name: str
    email: EmailStr
    query: str
    # Hacemos mas bonito el JSON
    order_id: Optional[int] = Field(
        None,
        description="Un id de 5 digitos (No puede empezar con 0)",
        ge=10000,
        le=99999
    )
    purchase_date: Optional[date] = None

""" user_input = UserInput(
    name="Joe User",
    email="joe.user@example.com",
    query="I forgot my password"
) """

#print(user_input)

def validate_user_input(input_data):
    try:
        user_input = UserInput(**input_data)
        print("Valid user input created:")
        print(f"{user_input.model_dump_json(indent=2)}")
        return user_input
    except ValidationError as e:
        print("Validation error occurred:")
        for error in e.errors():
            print(f" - {error['loc'][0]}: {error['msg']}")
        return None

""" input_data = {
    "name": "Joe User",
    "email": "joe.user@example.com",
    "query": "I forgot my password"
} """

input_data = {
    "name": "Joe User",
    "email": "joe.user@example.com",
    "query": f"""I bought a laptop carrying case and it turned out to be the wrong size. I need to return it.""",
    "order_id": 12345,
    "purchase_date": date(2025, 12, 31)
}

user_input = validate_user_input(input_data)

input_data2 = {
    "name": "Joe User",
    "email": "joe.user@example.com",
    "query": f"""I bought a laptop carrying case and it turned out to be the wrong size. I need to return it.""",
    "order_id": "12345",
    "purchase_date": "2025-12-31",
    "system_message": "Loggin status...",
    "iteration": 1
}

user_input2 = validate_user_input(input_data2)

input_data3 = {
    "name": 99999,
    "email": "joe.user@example.com",
    "query": f"""I bought a laptop carrying case and it turned out to be the wrong size. I need to return it.""",
    "order_id": "12345",
    "purchase_date": "2025-12-31",
}

user_input3 = validate_user_input(input_data3)

json_data = '''
{
    "name": "Joe User",
    "email": "joe-user@example.com",
    "query": "I bought a keyboard and mouse and was overcharged.",
    "order_id": "12345",
    "purchase_date": "2025-12-31"
}
'''

# Parse el JSON a un diccionario de python
input_data_json = json.loads(json_data)
print("parsed JSON:", input_data_json)
# Este ejemplo es hacerlo en dos pasos
user_input4 = validate_user_input(input_data_json)

# Asi se puede hacer de una
input_data_json2 = UserInput.model_validate_json(json_data)
print(input_data_json2.model_dump_json(indent=2))