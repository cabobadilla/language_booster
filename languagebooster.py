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

            # Prompt para generar explicación y preguntas
            prompt_explicacion_y_preguntas = (
                f"Con base en el siguiente texto, escribe una breve explicación en {idioma.lower()} "
                f"acerca de los principales puntos o temas que el lector debería haber entendido o aprendido "
                f"del texto. Después de la explicación, genera 5 preguntas simples en {idioma.lower()} que evalúen la comprensión. "
                f"Devuelve los resultados en formato JSON estructurado con las claves: 'explicacion' y 'preguntas'. "
                f"Texto: \"{texto_generado}\""
            )

            response_explicacion_y_preguntas = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un generador de explicaciones y preguntas educativas."},
                    {"role": "user", "content": prompt_explicacion_y_preguntas},
                ],
                temperature=0.7,
                max_tokens=400,
            )

            # Parsear el JSON generado
            try:
                resultado = json.loads(response_explicacion_y_preguntas['choices'][0]['message']['content'].strip())
                explicacion = resultado.get("explicacion", "No se pudo generar una explicación.")
                preguntas = resultado.get("preguntas", [])
            except json.JSONDecodeError:
                st.error("Error al procesar el formato JSON de las preguntas. Intenta nuevamente.")
                st.stop()

            # Mostrar título, texto, explicación y preguntas
            st.subheader("Título del Texto")
            st.write(f"📖 {texto_generado.splitlines()[0]}")  # Título como primera línea del texto

            st.subheader("Texto Generado")
            st.write("\n".join(texto_generado.splitlines()[1:]))  # El resto es el texto

            st.subheader("Temas Principales")
            st.write(explicacion)

            st.subheader("Preguntas de Comprensión")
            if preguntas:
                for i, pregunta in enumerate(preguntas, 1):
                    st.markdown(f"**{i}. {pregunta}**")
            else:
                st.write("No se generaron preguntas. Intenta nuevamente.")

        except Exception as e:
            st.error(f"Hubo un error al generar el contenido: {e}")
