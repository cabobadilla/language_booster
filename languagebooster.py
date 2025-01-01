import streamlit as st
from openai import OpenAIAPI
import random

# Configuración inicial
st.set_page_config(page_title="Aprende Idiomas", layout="centered")

# Encabezado de la aplicación
st.title("Aprende Idiomas")
st.markdown(
    "Selecciona un idioma, nivel y tema para practicar tu comprensión lectora. "
    "La aplicación generará un texto y preguntas de comprensión para ayudarte a mejorar."
)

# Selección de parámetros
idioma = st.selectbox("Selecciona el idioma", ["Inglés", "Italiano"])
nivel = st.selectbox("Selecciona el nivel CEFR", ["A1", "A2", "B1", "B2", "C1", "C2"])
tema = st.selectbox("Selecciona el tema", ["Viajes", "Historia", "Cultura General"])

# Botón para generar texto
if st.button("Generar Texto y Preguntas"):
    with st.spinner("Generando texto y preguntas..."):
        # Llamada a OpenAI para generar el texto
        # Nota: Sustituye 'your_api_key' con una referencia segura en tu implementación final
        try:
            import openai
            openai.api_key = st.secrets["openai_api_key"]

            # Promp para generar texto
            prompt = (
                f"Genera un texto en {idioma.lower()} con un nivel de dificultad {nivel} "
                f"sobre el tema {tema}. El texto debe tener entre 150 y 200 palabras y ser interesante, "
                "real y con hechos relevantes."
            )

            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=200,
                temperature=0.7,
            )
            texto_generado = response.choices[0].text.strip()

            # Mostrar texto generado
            st.subheader("Texto Generado")
            st.write(texto_generado)

            # Generar preguntas de comprensión
            prompt_preguntas = (
                f"A partir del siguiente texto, genera 5 preguntas de selección múltiple con 4 opciones "
                f"y una sola respuesta correcta. El texto es: \"{texto_generado}\". Devuelve las preguntas "
                f"y opciones en un formato estructurado en JSON."
            )

            response_preguntas = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt_preguntas,
                max_tokens=300,
                temperature=0.7,
            )
            preguntas_json = eval(response_preguntas.choices[0].text.strip())
            preguntas = preguntas_json["preguntas"]

            st.subheader("Preguntas de Comprensión")
            respuestas_usuario = []

            for i, pregunta in enumerate(preguntas):
                st.write(f"**{i + 1}. {pregunta['pregunta']}**")
                opciones = pregunta["opciones"]
                respuesta_usuario = st.radio(
                    f"Selecciona una respuesta para la pregunta {i + 1}",
                    opciones,
                    key=f"pregunta_{i}",
                )
                respuestas_usuario.append((respuesta_usuario, pregunta["correcta"]))

            if st.button("Evaluar Respuestas"):
                total_correctas = 0
                for i, (respuesta, correcta) in enumerate(respuestas_usuario):
                    if respuesta == correcta:
                        st.success(f"Pregunta {i + 1}: Correcta ✅")
                        total_correctas += 1
                    else:
                        st.error(f"Pregunta {i + 1}: Incorrecta ❌ (Respuesta correcta: {correcta})")

                st.subheader("Resultados")
                st.write(f"Respuestas correctas: {total_correctas}/{len(preguntas)}")
        except Exception as e:
            st.error(f"Hubo un error al generar el contenido: {e}")
