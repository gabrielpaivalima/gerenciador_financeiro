import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

def tabela ():
    # Estabelecendo uma conexão com a planilha do Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Exibindo os dados que já estão lá:
    existing_data = conn.read(worksheet="Pagina", usecols=list(range(8)), ttl=1)
    existing_data = existing_data.dropna(how="all")
    return existing_data

# depois quando o webapp estiver pronto ver se eu consigo usar essa parte do código com POO
def incluir_dado (tb_reg_novo):
    # Estabelecendo uma conexão com a planilha do Google Sheets:
    conn = st.connection("gsheets", type=GSheetsConnection)

    tb_reg_existente = tabela()

    # Lançando um novo registro na tabela do Google Sheets:
    updated_df = pd.concat([tb_reg_existente, tb_reg_novo], ignore_index=False)

    # Atualizando na base do Google Sheets:
    conn.update(worksheet="Pagina", data = updated_df)


