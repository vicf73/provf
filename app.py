import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ⚙️ Configuração da página
st.set_page_config(
    page_title="Mapa de Inspeção",
    layout="centered",  # Ideal para telemóvel
    initial_sidebar_state="collapsed"
)

# Título
st.title("📍 Mapa de Inspeção")

# 📝 Campos do formulário
# Se o valor não existir em session_state, cria-se um valor padrão
if "nome" not in st.session_state:
    st.session_state.nome = ""
if "endereco" not in st.session_state:
    st.session_state.endereco = ""
if "dt_nsc" not in st.session_state:
    st.session_state.dt_nsc = datetime.today().date()  # Garantindo que seja uma data válida
if "status" not in st.session_state:
    st.session_state.status = "fraud"
if "lat" not in st.session_state:
    st.session_state.lat = 0.0
if "lon" not in st.session_state:
    st.session_state.lon = 0.0

# Exibição dos campos de entrada, usando session_state
st.session_state.nome = st.text_input("👤 Nome do cliente", value=st.session_state.nome)
st.session_state.endereco = st.text_input("🏠 Endereço", value=st.session_state.endereco)

# Garantindo que o valor de data seja do tipo correto
st.session_state.dt_nsc = st.date_input("📅 Data de nascimento", value=st.session_state.dt_nsc)

st.session_state.status = st.selectbox("📌 Status", ["fraud", "executado", "Sem acesso"], index=["fraud", "executado", "Sem acesso"].index(st.session_state.status))
st.session_state.lat = st.number_input("🌐 Latitude", format="%.6f", value=st.session_state.lat)
st.session_state.lon = st.number_input("🌐 Longitude", format="%.6f", value=st.session_state.lon)

# 📂 Caminho do CSV (relativo ao arquivo atual)
caminho_csv = os.path.join(os.path.dirname(__file__), "client.csv")

# ✅ Botão para cadastrar
if st.button("Cadastrar cliente"):
    if st.session_state.nome and st.session_state.endereco:
        data_status = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linha = f"{st.session_state.nome},{st.session_state.endereco},{st.session_state.dt_nsc},{st.session_state.status},{st.session_state.lat},{st.session_state.lon},{data_status}\n"

        # Escreve no arquivo CSV
        with open(caminho_csv, "a", encoding="utf8") as arquivo:
            arquivo.write(linha)

        st.success("✅ Cliente cadastrado com sucesso!")

        # Mostra o ponto no mapa
        st.map(pd.DataFrame([[st.session_state.lat, st.session_state.lon]], columns=["lat", "lon"]), use_container_width=True)

        # Limpar os campos (setando valores padrões novamente no session_state)
        st.session_state.nome = ""
        st.session_state.endereco = ""
        st.session_state.dt_nsc = datetime.today().date()  # Resetando para a data atual
        st.session_state.status = "fraud"
        st.session_state.lat = 0.0
        st.session_state.lon = 0.0
    else:
        st.warning("⚠️ Por favor, preencha nome e endereço.")

# 📋 Exibição de clientes cadastrados
if os.path.exists(caminho_csv):
    try:
        df = pd.read_csv(caminho_csv, names=[
            "Nome", "Endereço", "Nascimento", "Status", "Lat", "Long", "Data_Status"
        ], on_bad_lines="skip")

        st.markdown("### 🧾 Registros")
        st.dataframe(df, use_container_width=True)

        # Mapa com todos os pontos cadastrados
        st.markdown("### 🗺️ Localizações")
        df_mapa = df[["Lat", "Long"]].dropna()
        df_mapa.columns = ["lat", "lon"]
        st.map(df_mapa, use_container_width=True)

        # 📁 Botão para baixar como Excel
        st.markdown("### ⬇️ Baixar Excel")
        excel_path = os.path.join(os.path.dirname(__file__), "clientes.xlsx")
        df.to_excel(excel_path, index=False, engine="openpyxl")

        with open(excel_path, "rb") as f:
            st.download_button("📥 Baixar Excel", f, file_name="clientes.xlsx")

        # 📧 Enviar por email
        st.markdown("### 📤 Enviar por E-mail")
        destinatario = st.text_input("Digite o e-mail de destino")
        enviar = st.button("Enviar E-mail")

        if enviar:
            if destinatario:
                import smtplib
                from email.message import EmailMessage

                msg = EmailMessage()
                msg["Subject"] = "Registros de Clientes"
                msg["From"] = "seuemail@gmail.com"  # Substitua
                msg["To"] = destinatario
                msg.set_content("Segue em anexo a planilha com os dados dos clientes cadastrados.")

                with open(excel_path, "rb") as f:
                    msg.add_attachment(f.read(), maintype="application", subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename="clientes.xlsx")

                try:
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                        smtp.login("seuemail@gmail.com", "sua_senha_de_app")  # Use senha de app
                        smtp.send_message(msg)
                    st.success("📤 E-mail enviado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao enviar e-mail: {e}")
            else:
                st.warning("⚠️ Insira um e-mail válido.")

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")

