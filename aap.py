import streamlit as st
import pandas as pd
import pydeck as pdk
from datetime import datetime
import os

# Carrega o CSV
df = pd.read_csv("dados.csv")

# Título
st.title("📍 Mapa de Inspeção")

# Simula um "rerun" após validação
if "refrescar" in st.session_state and st.session_state.refrescar:
    st.session_state.refrescar = False
    st.rerun()

# Seleção de ID
id_selecionado = st.selectbox("Selecione um CIL :", df["id"])

# Dados do ponto selecionado
ponto_focus = df[df["id"] == id_selecionado].iloc[0]
lat, long = ponto_focus["lat"], ponto_focus["long"]
contador = ponto_focus["contador"]
leitura = ponto_focus["leitura"]
MatContador = ponto_focus["MatContador"]
MedFat = ponto_focus["MedFat"]

st.markdown(f"**Contador:** `{contador}` &nbsp;&nbsp;&nbsp; **Leitura:** `{leitura}` &nbsp;&nbsp;&nbsp; **MatContador:** `{MatContador}` &nbsp;&nbsp;&nbsp; **MedFat:** `{MedFat}`")

# Link para Google Maps
url_google_maps = f"https://www.google.com/maps?q={lat},{long}"
st.markdown(f"[🔍 Abrir no Google Maps]({url_google_maps})", unsafe_allow_html=True)

# Camadas do mapa
layer_todos = pdk.Layer(
    "ScatterplotLayer",
    data=df[df["id"] != id_selecionado],
    get_position="[long, lat]",
    get_fill_color="[0, 153, 255, 160]",
    get_radius=50,
    pickable=True,
)

layer_selecionado = pdk.Layer(
    "ScatterplotLayer",
    data=pd.DataFrame([ponto_focus]),
    get_position="[long, lat]",
    get_fill_color="[255, 0, 0, 200]",
    get_radius=50,
    pickable=True,
)

view_state = pdk.ViewState(
    latitude=lat,
    longitude=long,
    zoom=16,
    pitch=0,
)

st.pydeck_chart(
    pdk.Deck(
        map_style="mapbox://styles/mapbox/satellite-streets-v11",
        initial_view_state=view_state,
        layers=[layer_todos, layer_selecionado],
        tooltip={"text": "ID: {id}\nContador: {contador}"}
    ),
    height=250
)

# Inicializa session_state
for campo, valor_padrao in {
    "contador": "",
    "leitura": "",
    "carga": "",
    "status": "fraud",
    "lat": 0.0,
    "lon": 0.0,
    "refrescar": False
}.items():
    if campo not in st.session_state:
        st.session_state[campo] = valor_padrao

# Formulário
st.session_state.contador = st.text_input("🏠 Contador", value=st.session_state.contador)
st.session_state.leitura = st.text_input("🏠 Leitura", value=st.session_state.leitura)
st.session_state.carga = st.text_input("🏠 Carga A", value=st.session_state.carga)
st.session_state.status = st.selectbox("📌 Status", ["fraud", "Normal", "Sem acesso"], index=["fraud", "Normal", "Sem acesso"].index(st.session_state.status))
st.session_state.lat = st.number_input("🌐 Latitude", format="%.6f", value=st.session_state.lat)
st.session_state.lon = st.number_input("🌐 Longitude", format="%.6f", value=st.session_state.lon)

# Caminho do CSV
caminho_csv = os.path.join(os.path.dirname(__file__), "client.csv")

# Botão de validação
if st.button("Validar Inspeçao"):
    if st.session_state.lat and st.session_state.lon and st.session_state.carga:
        data_status = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linha = f"{st.session_state.contador},{st.session_state.leitura},{st.session_state.carga},{st.session_state.status},{st.session_state.lat},{st.session_state.lon},{data_status}\n"

        with open(caminho_csv, "a", encoding="utf8") as arquivo:
            arquivo.write(linha)

        st.success("✅ Inspeção validada com sucesso!")

        # Limpa os campos e ativa flag de "refresh"
        st.session_state.contador = ""
        st.session_state.leitura = ""
        st.session_state.carga = ""
        st.session_state.status = "fraud"
        st.session_state.lat = 0.0
        st.session_state.lon = 0.0
        st.session_state.refrescar = True
        st.rerun()
    else:
        st.warning("⚠️ Por favor, preencha os campos obrigatórios.")
