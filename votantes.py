import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path
import google.generativeai as genai

# 1. Safe API Secret Handling (Prevents local script crashes)
if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.1-flash-lite")
else:
    model = None  # Soft fallback if secrets are not ready yet

st.set_page_config(layout="wide")

# CSS Injection
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
left, center, right = st.columns([2, 3, 2])

with center:
    st.image("Images/jfplogo.png", 
             caption="Plataforma de datos de la fuerza joven del pueblo", width=30, 
             use_container_width=True)  

st.header("Reporte de votantes inscritos", divider="green", text_alignment="center")

data = st.file_uploader("Sube el archivo excel", type=["xlsx"])

if data is not None:
    # Read the data ONCE globally for this block
    df = pd.read_excel(data)
    prov = df["Territorio"].unique()
    df["Recinto"] = df["Recinto"].str.strip().str.title()
   
    recinto = df["Recinto"].unique()
    sel = st.selectbox(
        "Filtrar por territorio",
        options=prov,
        index=None,
        placeholder="Buscar un territorio"
    )
    if sel:
        recintos = df[df["Territorio"] == sel]["Recinto"].unique()
    else:
        recintos = df["Recinto"].unique()

    sel2 = st.selectbox(
        "Filtrar por recinto",
        options=recintos,
        index=None,
        placeholder="Buscar un recinto electoral"
    )
    
    df_filter = df[(df["Territorio"] == sel)]
    df_filter2 = df[df["Recinto"] == sel2]
   
    if sel2:
        total = df_filter2["Nombre"].count()
        st.metric(label=f"Total de votantes inscritos en el recinto electoral {sel2}", value=total, border=True)
        st.dataframe(df_filter2)
    elif sel:
        total = df_filter["Nombre"].count()
        st.metric(label=f"Total de votantes inscritos en {sel}", value=total, border=True)
        st.dataframe(df_filter)
    else:
        total = df["Nombre"].count()
        st.metric(label="Total de votantes inscritos", value=total, border=True)
        st.dataframe(df)
    
    # Chart generation (Using the already loaded df)
    votantes_terr = df.groupby("Territorio")["Nombre"].count().reset_index().sort_values(by="Nombre", ascending=False)
    fig = px.bar(votantes_terr, x="Territorio", y="Nombre", title="Grafico de votantes inscritos por territorio", color_discrete_sequence=["lime"], text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

    # --- Chatbot Section ---
    st.header(" 👨‍💼 Chat bot asistente de campaña", divider="green", text_alignment="center")
    st.info("💬 ¡Hola! Soy tu asistente de campaña. Estoy aquí para ayudarte a responder preguntas sobre los votantes inscritos. Puedes preguntarme cosas como: \n\n- ¿Cuántos votantes hay en el territorio X? \n- ¿Cuántos votantes hay en el recinto Y? \n- ¿Cuál es el total de votantes inscritos? \n\n¡Adelante, hazme una pregunta!")
    
    datosbot = df.head(50)
    context = datosbot.to_markdown(index=False)
    pregunta = st.chat_input("Escribe tu pregunta aquí...")

    if pregunta:
        if model is not None:
            with st.spinner("Procesando tu pregunta..."):
                full_prompt = f"""
                Eres un asistente de campaña experto. Utiliza la siguiente información estructurada extraída de un archivo de Excel para responder la pregunta del usuario de forma precisa.

                CONTEXTO DE LA CAMPAÑA (DATOS DE EXCEL):
                {context}

                PREGUNTA DEL USUARIO:
                {pregunta}

                RESPUESTA:
                """
                try:
                    # Executing everything inside the exact question environment safely
                    respuesta = model.generate_content(full_prompt)
                    st.chat_message("assistant").write(respuesta.text)
                except Exception as e:
                    if "429" in str(e):
                        st.warning("⚠️ El bot está un poco ocupado procesando otras preguntas. Espera 10 segundos e intenta de nuevo.")
                    else:
                        st.error(f"Error de la API: {e}")
        else:
            st.error("⚠️ Error: La API Key no está configurada en los secretos de Streamlit Cloud.")
