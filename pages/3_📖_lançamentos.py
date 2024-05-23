import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração para que a página sempre fique em tela cheia e os dados mais faceis de serem vistos
st.set_page_config(layout="wide")

# Declaração das variáveis que serão utilizadas
tipo = ["Receita", "Despesa"]

todas_categorias = ["Alimentação","Cuidados Pessoais","Educação",
                    "Lazer","Outras Despesas","Projetos","Saúde",
                    "Telefone","Transportes","Vestuário",
                    "Salário", "Aluguel", "Outras Receitas"]


categoria_gastos = ["Alimentação","Cuidados Pessoais","Educação",
                    "Lazer","Outras Despesas","Projetos","Saúde",
                    "Telefone","Transportes","Vestuário"]

categoria_receitas = ["Salário", "Aluguel", "Outras Receitas"]

instituicoes_financeiras = ["Banco do Brasil", "Bradesco", "Nubank", "Banco Inter"]

formas_pagamento = ["Conta Corrente", "Cartão de Crédito"]

centro_custo = ["João", "Maria"]

# Aqui apenas será feito os lançamentos dos gastos e receitas
st.title("Lançamento de Dados")

col1, col2 = st.columns(2)
data_movimentação = col1.date_input("Data da Movimentação", format="DD/MM/YYYY")
tipo_movimentação = col2.selectbox("Tipo de Movimentação",(tipo))
centro_custo_movimentação = col1.selectbox("A quem pertence?",(centro_custo))
        
if tipo_movimentação == "Receita":
    forma_movimentação = col2.selectbox("Meio de Recebimento",(formas_pagamento))
    categoria_movimentação = col1.selectbox("Categoria",(categoria_receitas))
    instituicao_movimentação = col2.selectbox("Bancos", (instituicoes_financeiras)) 
else:
    forma_movimentação = col2.selectbox("Meio de Pagamento",(formas_pagamento))
    categoria_movimentação = col1.selectbox("Categoria",(categoria_gastos))
    instituicao_movimentação = col2.selectbox("Bancos", (instituicoes_financeiras))

valor_movimentação = col2.number_input("Valor")
descrição_movimentação = col1.text_input("Breve Descrição")

novos_dados = pd.DataFrame(
    [
        {
            'Data': data_movimentação.strftime("%d/%m/%Y"),
            'Tipo': tipo_movimentação,
            'Meio de Pagamento': forma_movimentação,
            'Instituição Bancária': instituicao_movimentação,
            'Centro de Custo': centro_custo_movimentação,
            'Categoria': categoria_movimentação,
            'Descrição': descrição_movimentação,
            'Valor': valor_movimentação
            }
    ]
)
        
# Aqui fazer uma condicional para quando clicar lançar no banco de dados ou tabela, o que for mais funcional.
if st.button("Lançar Gasto"):
    if data_movimentação != "" and valor_movimentação > 0:
        # Estabelecendo uma conexão com a planilha do Google Sheets
        conn = st.connection("gsheets", type=GSheetsConnection)

        # Conectando com a tabela existente e declarando a variável nela
        existing_data = conn.read(worksheet="Pagina", usecols=list(range(8)), ttl=1)
        existing_data = existing_data.dropna(how="all")

        # Adicionando um novo lançamento na tabela
        updated_df = pd.concat([existing_data, novos_dados], ignore_index=True)
        
        # Atualizando na base do Google Sheets
        conn.update(worksheet="Pagina", data=updated_df)
        
        st.success("REGISTRO LANÇADO COM SUCESSO!!!", icon="✅")

        
    else:
        st.warning("CERTIFIQUE-SE DE QUE A DATA ESTÁ PREENCHIDA E O VALOR É DIFERENTE DE R$ 0,00", icon="⚠")