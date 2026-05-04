import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

st.set_page_config(layout="wide")

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
left, center, right = st.columns([2, 3, 2])

with center:
    st.image("Images/jfplogo.png", 
             caption="Plataforma de datos de la fuerza joven del pueblo",width=30, 
             use_container_width=True)  


st.header("Reporte de votantes inscritos", divider="green")

data = st.file_uploader("Sube el archivo excel", type=["xlsx"])

if data is not None:
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
        st.metric(label=f"Total de votantes inscritos en el recinto electoral {sel2}", value=total,border=True)
        st.dataframe(df_filter2)

    elif sel:
        total = df_filter["Nombre"].count()
        st.metric(label=f"Total de votantes inscritos en {sel}", value=total,border=True)
        st.dataframe(df_filter)
    else:
        total = df["Nombre"].count()
        st.metric(label="Total de votantes inscritos", value=total,border=True)
        st.dataframe(df)

else:
    st.info("📂 Sube el archivo Excel para ver el reporte")

    
if data is not None:
    df = pd.read_excel(data)

    votantes_terr = df.groupby("Territorio")["Nombre"].count().reset_index().sort_values(by="Nombre", ascending=False)
    fig = px.bar(votantes_terr, x="Territorio", y="Nombre", title="Grafico de votantes inscritos por territorio",color="Nombre", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)
    st.header("Lista de votantes inscritos por territorio", divider="green",text_alignment="center")
    st.dataframe(votantes_terr)