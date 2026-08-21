from ollama import chat

messages = []

def moderar(texto, rol="user"):
    response = chat(
        model='llama-guard3:1b',
        messages=[{'role': rol, 'content': texto}]
    )
    return response.message.content

while True:
    user_input = input("Chat with history: ")

    moderacion = moderar(user_input)
    if "unsafe" in moderacion.lower():
        print("Este mensaje no es apropiado. ¡BLOQUEADO!")
        continue

    response = chat(
        model="llama3.2:3b",
        messages=[*messages,
                  {'role': 'user', 'content': user_input}],
        options={'num_predict': 200}
    )

    moderacion_respuesta = moderar(response.message.content, rol="assistant")
    if "unsafe" in moderacion_respuesta.lower():
        print("Hemos bloqueado la respuesta por no ser apropiada")
        continue

    messages += [
        {'role': 'user', 'content': user_input},
        {'role': 'assistant', 'content': response.message.content},
    ]

    tokens_entrada = response.get('prompt_eval_count', 0)
    tokens_salida = response.get('eval_count', 0)
    total = tokens_entrada + tokens_salida

    print(response.message.content + '\n')
    print(f"Contexto usado: {total}/ 131072 tokens"
          f"Entrada: {tokens_entrada}, salida: {tokens_salida}")
    print("Duracion del procesamiento en ns: ", response["total_duration"])