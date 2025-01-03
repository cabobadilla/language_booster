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
nivel = st.selectbox(
    "Selecciona el nivel CEFR",
    [
        "A1 - Principiante 1",
        "A2 - Principiante 2",
        "B1 - Intermedio 1",
        "B2 - Intermedio 2",
        "C1 - Avanzado 1",
        "C2 - Avanzado 2",
    ],
)
tema = st.selectbox("Selecciona el tema", ["Cultura", "Viajes", "Moda", "Historia"])

# Botón para generar texto y preguntas
if st.button("Generar Texto y Preguntas"):
    with st.spinner("Generando contenido..."):
        try:
            # Configuración de la API
            openai.api_key = st.secrets["openai"]["api_key"]

            # Prompt para generar texto y título
            prompt_texto = (
                f"Escribe un texto en {idioma.lower()} con un nivel de dificultad {nivel.split(' ')[0]} "
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
                f"del texto. Después de la explicación, genera 5 preguntas simples en {idioma.lower()} que evalúen la comprensión, "
                f"incluyendo las respuestas correctas. Devuelve los resultados en formato JSON estructurado "
                f"con las claves: 'explicacion', 'preguntas' (con opciones y respuestas correctas). "
                f"Asegúrate de que el JSON esté correctamente formateado, sin errores de sintaxis. "
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

            # Intentar parsear el JSON generado
            try:
                raw_content = response_explicacion_y_preguntas['choices'][0]['message']['content'].strip()

                # Sanitizar contenido JSON
                sanitized_content = raw_content.strip()
                if not sanitized_content.startswith('{') or not sanitized_content.endswith('}'):
                    sanitized_content = sanitized_content[sanitized_content.find('{'):sanitized_content.rfind('}') + 1]

                # Parsear JSON
                resultado = json.loads(sanitized_content)
                explicacion = resultado.get("explicacion", "No se pudo generar una explicación.")
                preguntas = resultado.get("preguntas", [])
            except (json.JSONDecodeError, ValueError) as e:
                st.error(f"Error al procesar el formato JSON de las preguntas. Detalles: {e}")
                st.text_area("Contenido devuelto por OpenAI (para depuración):", raw_content)
                st.stop()

            # Mostrar título y texto
            st.subheader("Título del Texto")
            st.write(f"📖 {texto_generado.splitlines()[0]}")  # Título como primera línea del texto

            st.subheader("Texto Generado")
            st.write("\n".join(texto_generado.splitlines()[1:]))  # El resto es el texto

            st.subheader("Temas Principales")
            st.write(f"💡 {explicacion}")

            # Mostrar preguntas de comprensión
            st.subheader("Preguntas de Comprensión")
            respuestas_correctas = []
            if preguntas:
                for i, pregunta in enumerate(preguntas, 1):
                    st.markdown(f"**{i}. {pregunta['pregunta']}**")
                    respuestas_correctas.append(pregunta.get("correcta", "No disponible"))
            else:
                st.write("No se generaron preguntas. Intenta nuevamente.")

            # Mostrar respuestas correctas en tamaño pequeño
            st.subheader("Respuestas Correctas")
            for i, respuesta in enumerate(respuestas_correctas, 1):
                st.markdown(
                    f"<p style='font-size:10px; color:gray'>{i}. {respuesta}</p>",
                    unsafe_allow_html=True,
                )

        except Exception as e:
            st.error(f"Hubo un error al generar el contenido: {e}")
