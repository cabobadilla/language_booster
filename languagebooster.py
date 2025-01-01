import streamlit as st
import openai  # Usar el cliente OpenAI correctamente
import random
import json  # Para manejar JSON de forma segura

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
    with st.spinner("Generando texto y preguntas..."):
        try:
            # Usar la clave API almacenada en secretos
            openai.api_key = st.secrets["openai"]["api_key"]

            # Prompt para generar texto
            prompt_texto = (
                f"Escribe un texto en {idioma.lower()} con un nivel de dificultad {nivel} "
                f"sobre el tema {tema}. El texto debe tener entre 150 y 200 palabras, ser interesante, "
                "real y con hechos relevantes."
            )

            response_texto = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto en generar textos educativos."},
                    {"role": "user", "content": prompt_texto},
                ],
                temperature=0.7,
                max_tokens=200,
            )
            texto_generado = response_texto['choices'][0]['message']['content'].strip()

            # Mostrar texto generado
            st.subheader("Texto Generado")
            st.write(texto_generado)

            # Generar preguntas de comprensión
            prompt_preguntas = (
                f"A partir del siguiente texto, genera 5 preguntas de selección múltiple con 4 opciones "
                f"y una sola respuesta correcta. El texto es: \"{texto_generado}\". "
                "Devuelve las preguntas en formato JSON. Ejemplo: "
                '{"preguntas": [{"pregunta": "Pregunta 1", "opciones": ["A", "B", "C", "D"], "correcta": "A"}]}'
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

            # Parsear respuesta JSON
            try:
                preguntas_json = json.loads(response_preguntas['choices'][0]['message']['content'].strip())
                preguntas = preguntas_json["preguntas"]
            except json.JSONDecodeError:
                st.error("Hubo un error al procesar las preguntas. Intenta nuevamente.")
                st.stop()

            # Mostrar preguntas de comprensión
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
