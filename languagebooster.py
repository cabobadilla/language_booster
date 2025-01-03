import streamlit as st
import openai
import json

# Configuración inicial
app_version = "20250101"
st.set_page_config(page_title=f"Language Booster {app_version}", layout="centered")

# Encabezado de la aplicación
st.title(f"Language Booster {app_version}")
st.markdown(
    """
    ¡Bienvenido a Language Booster! 🌍📚  
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

            # Prompt para generar palabras clave y preguntas
            prompt_vocabulario_y_preguntas = (
                f"Con base en el siguiente texto, selecciona exactamente 5 palabras clave en {idioma.lower()} "
                f"que sean importantes para entender el tema tratado. Después, genera 5 preguntas en {idioma.lower()} que evalúen la comprensión del texto, "
                f"y agrega una sola sugerencia como un concepto clave simple después de cada pregunta. "
                f"Cada sugerencia debe tener un máximo de 3 palabras. "
                f"Devuelve los resultados en formato JSON estructurado con las claves: 'palabras_clave' y 'preguntas'. "
                f"Asegúrate de que el JSON esté correctamente formateado, sin errores de sintaxis. "
                f"Texto: \"{texto_generado}\""
            )

            response_vocabulario_y_preguntas = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un generador de palabras clave y preguntas educativas."},
                    {"role": "user", "content": prompt_vocabulario_y_preguntas},
                ],
                temperature=0.7,
                max_tokens=400,
            )

            # Intentar parsear el JSON generado
            try:
                raw_content = response_vocabulario_y_preguntas['choices'][0]['message']['content'].strip()

                # Sanitizar contenido JSON
                sanitized_content = raw_content.strip()
                if not sanitized_content.startswith('{') or not sanitized_content.endswith('}'):
                    sanitized_content = sanitized_content[sanitized_content.find('{'):sanitized_content.rfind('}') + 1]

                # Parsear JSON
                resultado = json.loads(sanitized_content)
                palabras_clave = resultado.get("palabras_clave", [])
                preguntas = resultado.get("preguntas", [])
            except (json.JSONDecodeError, ValueError) as e:
                st.error(f"Error al procesar el formato JSON. Detalles: {e}")
                st.text_area("Contenido devuelto por OpenAI (para depuración):", raw_content)
                st.stop()

            # Mostrar título y texto
            st.subheader("Título del Texto")
            st.write(f"📖 {texto_generado.splitlines()[0]}")  # Título como primera línea del texto

            st.subheader("Texto Generado")
            st.write("\n".join(texto_generado.splitlines()[1:]))  # El resto es el texto

            # Mostrar palabras clave
            st.subheader("Palabras Clave")
            if palabras_clave:
                st.write("Palabras importantes para comprender el texto:")
                st.write("\n".join([f"- {palabra}" for palabra in palabras_clave]))
            else:
                st.write("No se generaron palabras clave. Intenta nuevamente.")

            # Mostrar preguntas de comprensión
            st.subheader("Preguntas de Comprensión")
            if preguntas:
                for i, pregunta_data in enumerate(preguntas, 1):
                    pregunta_texto = pregunta_data.get('pregunta', 'Pregunta no disponible')
                    sugerencia = pregunta_data.get('sugerencia', '').replace("Focus on ", "").strip()
                    # Reducir sugerencia a máximo 3 palabras
                    sugerencia = " ".join(sugerencia.split()[:3]) if sugerencia else "Sin sugerencia"
                    st.markdown(f"**{i}.- {pregunta_texto}**\n--> {sugerencia}")
            else:
                st.write("No se generaron preguntas. Intenta nuevamente.")

        except Exception as e:
            st.error(f"Hubo un error al generar el contenido: {e}")
