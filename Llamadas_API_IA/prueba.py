from ollama import chat

messages = []

formato_salida = "I need you to make a output format JSON" \
                 "with the users question and your replies" \
                 "You need to follow this example" \
                 "json {" \
                 "'pregunta':{" \
                 "'type': 'string'" \
                 "'value': ''}" \
                 "'respuesta':{" \
                 "'type': 'string'" \
                 "'value': ''}" \
                 "'sugerencia':{" \
                 "'type': 'string'}" \
                 "'value': ''}" \
                 "}"

def moderar(texto, rol="user"):
    response = chat(
        model='llama-guard3:1b',
        messages=[{'role': rol, 'content': texto}]
    )
    return response.message.content

while True:
    user_input = input("(Pulsa 0 para salir)Chat with history: ")

    if user_input == "0":
        print("Hasta luego!")
        break

    moderacion = moderar(user_input)
    if "unsafe" in moderacion.lower():
        print("Este mensaje no es apropiado. ¡BLOQUEADO!")
        continue

    response = chat(
        model="llama3.2:3b",
        messages=[{'role': 'system', 'content': formato_salida}
                  ,*messages,
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
    
    print("Duracion del procesamiento en ns: ", ultimo_chunk.total_duration)