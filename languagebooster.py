import streamlit as st
import openai
import json

# Configuración inicial
st.set_page_config(page_title="Your Language Booster", layout="centered")

# Encabezado de la aplicación
st.title("Your Language Booster")
st.markdown(
    """
    ¡Bienvenido a Your Language Booster! 🌍📚  
    Selecciona un idioma, nivel y tema para practicar tu comprensión lectora. 
    La aplicación generará un texto y preguntas para ayudarte a mejorar.
    """
)

# Selección de parámetros
idioma = st.selectbox("Selecciona el idioma", ["Inglés", "Italiano"])
nivel = st.selectbox("Selecciona el nivel CEFR", ["A1", "A2", "B1", "B2", "C1", "C2"])
tema = st.selectbox("Selecciona el tema", ["Viajes", "Historia", "Cultura General"])

# Botón para generar texto y preguntas
if st.button("Generar Texto y Preguntas"):
    with st.spinner("Generando contenido..."):
        try:
            # Configuración de la API
            openai.api_key = st.secrets["openai"]["api_key"]

            # Prompt para generar texto y título
            prompt_texto = (
                f"Escribe un texto en {idioma.lower()} con un nivel de dificultad {nivel} "
                f"sobre el tema {tema}. El texto debe tener entre 150 y 200 palabras, ser interesante, "
                "real y con hechos relevantes. También proporciona un título breve y relevante para el texto."
            )

            response_texto = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto en generar textos educativos."},
                    {"role": "user", "content": prompt_texto},
                ],
                temperature=0.7,
                max_tokens=300,
            )
            texto_generado = response_texto['choices'][0]['message']['content'].strip()

            # Prompt para generar preguntas
            prompt_preguntas = (
                f"Basándote en el siguiente texto, genera 5 preguntas simples de opción múltiple "
                f"que evalúen la comprensión del texto. No incluyas respuestas correctas ni formato JSON. "
                f"Texto: \"{texto_generado}\""
            )

            response_preguntas = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un generador de preguntas educativas."},
                    {"role": "user", "content": prompt_preguntas},
                ],
                temperature=0.7,
                max_tokens=300,
            )
            preguntas_generadas = response_preguntas['choices'][0]['message']['content'].strip()

            # Mostrar título, texto y preguntas
            st.subheader("Título del Texto")
            st.write(f"📖 {texto_generado.splitlines()[0]}")  # Supongamos que el título está en la primera línea

            st.subheader("Texto Generado")
            st.write("\n".join(texto_generado.splitlines()[1:]))  # El resto es el texto

            st.subheader("Preguntas de Comprensión")
            st.markdown(preguntas_generadas)

        except Exception as e:
            st.error(f"Hubo un error al generar el contenido: {e}")
