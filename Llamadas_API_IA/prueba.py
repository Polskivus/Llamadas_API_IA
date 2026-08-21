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
        options={'num_predict': 200},
        stream=True
    )

    texto_completo= ""
    ultimo_chunk = None
    for chunks in response:
        print(chunks.message.content, end="", flush=True)
        texto_completo += chunks.message.content
        ultimo_chunk = chunks
    print()

    moderacion_respuesta = moderar(texto_completo, rol="assistant")
    if "unsafe" in moderacion_respuesta.lower():
        print("Hemos bloqueado la respuesta por no ser apropiada")
        continue

    messages += [
        {'role': 'user', 'content': user_input},
        {'role': 'assistant', 'content': texto_completo},
    ]

    tokens_entrada = ultimo_chunk.prompt_eval_count or 0
    tokens_salida = ultimo_chunk.eval_count or 0
    total = tokens_entrada + tokens_salida

    print(f"Contexto usado: {total}/131072 tokens, "
          f"Entrada: {tokens_entrada}, salida: {tokens_salida}")
    print("Duracion del procesamiento en ns: ", ultimo_chunk.total_duration)