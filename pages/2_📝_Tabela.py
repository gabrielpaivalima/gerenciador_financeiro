import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

from pages.tabelas import base_dados

existing_data = base_dados.tabela()
existing_data["Valor"] = existing_data["Valor"].apply(lambda x: f'R$ {x:,.2f}'.replace(",",";").replace(".",",").replace(";","."))

# Titulo e Descrição
st.title("Tabela de Visualização")
st.markdown("Apenas para verificar se está tudo bem com a tabela")

# Definir quantas linhas serão exibidas
linhas_a_exibir = st.selectbox("Quer ver quantas linhas na tabela?",([5,10,50,100,200]))

# Tabela a ser exibida:
if st.toggle("Editar dados", value=False) == False:
    st.dataframe(existing_data.head(linhas_a_exibir).set_index("Data"), width=5000)
else:
    st.data_editor(existing_data.set_index("Data"), width=5000)