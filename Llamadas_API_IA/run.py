import os
from dotenv import load_dotenv

load_dotenv()

#client = OpenAI(
#    base_url="https://api.groq.com/openai/v1",
#    api_key=os.environ.get("GROQ_API_KEY"),
#)

def get_completion(prompt, model="groq/compound-mini"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


prompt = ""
respuesta = get_completion(prompt)
print(respuesta)
