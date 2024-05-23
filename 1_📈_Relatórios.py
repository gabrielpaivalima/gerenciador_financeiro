import pandas as pd
import streamlit as st

import plotly.express as px
import plotly.graph_objects as go

from pages.tabelas import base_dados

# Dicionário com meses em número e palavras:
relacao_meses = {"Janeiro" : 1, "Fevereiro" : 2,  "Março" : 3,  "Abril" : 4,  "Maio" : 5,  "Junho" : 6,  
                 "Julho" : 7,  "Agosto" : 8,  "Setembro" : 9,  "Outubro" : 10,  "Novembro" : 11, "Dezembro" : 12}

st.set_page_config(layout="wide")

# Arquivo com a tabela para ser trabalhado
base_dados = base_dados.tabela()

# Filtrar tabela 
def filtrar_tabela(tabela, mes: int, ano: int, centro_de_custo: list, tipo: str, meio_pgto: list, inst_financeira: list):
    
    # Converti a coluna data para o formato data, assim posso trabalhar com ele
    tabela['Data'] = pd.to_datetime(tabela['Data'], format='%d/%m/%Y')

    # Criação das colunas mês e ano
    tabela['Mês'] = tabela['Data'].dt.month
    tabela['Ano'] = tabela['Data'].dt.year

    # Aqui é o filtro para pegar o que eu quero
    tabela_filtrada = tabela[
        (tabela["Mês"] == mes) & 
        (tabela["Ano"] == ano) &
        (tabela["Tipo"] == tipo)]
    
    filtered_df = tabela_filtrada[tabela_filtrada["Centro de Custo"].isin(centro_de_custo) & tabela_filtrada["Meio de Pagamento"].isin(meio_pgto) & tabela_filtrada["Instituição Bancária"].isin(inst_financeira)]
    
    return filtered_df
    
# Calcular o quanto foi gasto por categoria e o quanto representa do salário
def calc_gastos_por_categoria(tabela, mes: int, ano: int, centro_de_custo: list, meio_pgto: list, inst_financeira: list):
    
    tabela_filtrada = filtrar_tabela(tabela, mes, ano, centro_de_custo, "Despesa", meio_pgto, inst_financeira)

    # Somei por categoria aqui e coloquei da maior à menor, definindo qual categoria é mais influente:
    tabela_filtrada = tabela_filtrada[["Categoria", "Valor"]].groupby("Categoria").sum().sort_values("Valor", ascending=False)

    # Primeiro passo é transformar a tabela em dicionário para que fique mais fácil iterar sobre ela:
    dicionario = tabela_filtrada["Valor"].to_dict()

    # Depois eu crio um dicionário vazio para adicionar os elementos nele para transformar em tabela:
    dict_to_table = {}

    for chaves, valores in dicionario.items():
        valor_para_adicionar = f'{(valores / receita_mensal)*100:.2f}%'
        dict_to_table.update({chaves: valor_para_adicionar})

    # Transformar o dicionário em tabela para adicionar a coluna com a porcentagem no item de cima:
    tb = pd.DataFrame.from_dict(dict_to_table, orient='index', columns=['Percentual'])
    tabela_filtrada['(%)'] = tb['Percentual']
    return tabela_filtrada

# Listar todos os gastos realizados em 2023 para fazer gráficos e outras análises:
def listar_mvto(tabela, ano: int, centro_de_custo: list, tipo: str, meio_pgto: list, inst_financeira: list):
    
    lista_mvto = []

    for i in range (1,13):

        tabela_filtrada = filtrar_tabela(tabela, i, ano, centro_de_custo, tipo, meio_pgto, inst_financeira)

        lista_mvto.append(tabela_filtrada['Valor'].sum())

    return lista_mvto

# Comparar de forma relativa o quanto cada um está comprometendo do orçamento:
def comparar_categoria_relativa(tabela, mes: int, ano: int):
    tabela_filtrada_joao = filtrar_tabela(tabela, mes, ano, ["João"], "Despesa")
    tabela_filtrada_maria = filtrar_tabela(tabela, mes, ano, ["Maria"], "Despesa")
    
    # Filtrei os gastos do João pelo período que eu quero
    # Somei por Categoria filtrando apenas o João pelo período que eu quero - no caso do João
    tabela_filtrada_joao = tabela_filtrada_joao[['Categoria', 'Valor']].groupby("Categoria").sum().sort_values("Valor", ascending=False)
    tabela_filtrada_maria = tabela_filtrada_maria[['Categoria', 'Valor']].groupby("Categoria").sum().sort_values("Valor", ascending=False)

    # Primeiro passo é transformar as tabelas em dicionários para que fique mais fácil iterar sobre ela:
    dicionario_joao = tabela_filtrada_joao["Valor"].to_dict()
    dicionario_maria = tabela_filtrada_maria["Valor"].to_dict()

    # Depois eu crio um dicionário vazio para adicionar os elementos nele para transformar em tabela:
    dict_gastos_joão = {}
    dict_gastos_maria = {}

    # Apurar a receita do João e da Maria:
    receita_apurada = filtrar_tabela(tabela, mes, ano, ["João", "Maria"], "Receita")
    receita_apurada = receita_apurada['Valor'].sum()

    for chaves, valores in dicionario_joao.items():
        valor_para_adicionar = f'{(valores / receita_apurada)*100:.2f}%'
        dict_gastos_joão.update({chaves: valor_para_adicionar})

    for chaves, valores in dicionario_maria.items():
        valor_para_adicionar = f'{(valores / receita_apurada)*100:.2f}%'
        dict_gastos_maria.update({chaves: valor_para_adicionar})

    tb_joao = pd.DataFrame.from_dict(dict_gastos_joão, orient='index', columns=['(%) João'])
    tb_maria = pd.DataFrame.from_dict(dict_gastos_maria, orient='index', columns=['(%) Maria'])

    tb_maria['(%) João'] = tb_joao['(%) João']
    return tb_maria.fillna("0.00%")

# Configuração dos Filtros
with st.expander("Configure aqui os filtros para os itens 1 e 2:"):
    col10, col20, col30, col40, col50 = st.columns(5)
    filtro_centro_custo = col10.multiselect("Selecione um Centro de Custo", base_dados['Centro de Custo'].unique())
    filtro_mes = relacao_meses[col20.selectbox("Selecione o Mês", list(relacao_meses.keys()))]
    filtro_ano = col30.selectbox("Selecione o Ano", list(range(2023,2025)))
    filtro_meio_pgto = col40.multiselect("Meio de Pagamento", list(base_dados['Meio de Pagamento'].unique()))
    filtro_instituicao_financeira = col50.multiselect("Instituição Financeira", list(base_dados['Instituição Bancária'].unique()))

st.divider()

st.header("Item 1 - Metricas Mensais")

col1, col2, col3, col4 = st.columns(4)

# Receita
with col1:
    receita_mensal = filtrar_tabela(base_dados, filtro_mes, filtro_ano, filtro_centro_custo, "Receita", filtro_meio_pgto, filtro_instituicao_financeira)["Valor"].sum()
    st.metric("RECEITA MENSAL", f'R$ {receita_mensal:.2f}')

# Despesa
with col2:
    gasto_mensal = filtrar_tabela(base_dados, filtro_mes, filtro_ano, filtro_centro_custo, "Despesa", filtro_meio_pgto, filtro_instituicao_financeira)["Valor"].sum()
    st.metric("GASTO MENSAL", f'R$ {gasto_mensal:.2f}')

# Despesa em porcentagem
with col3:
    if receita_mensal == 0:
        gasto_mensal_percentual = 0
    else:
        gasto_mensal_percentual = (gasto_mensal/receita_mensal)*100
    st.metric("COMPROMETIMENTO DA RENDA MENSAL", f'{gasto_mensal_percentual:.2f}%')

# Saldo Mensal
with col4:
    saldo_mensal = receita_mensal - gasto_mensal
    if saldo_mensal > 0:
        st.metric("SUPERÁVIT MENSAL",f'R$ {saldo_mensal:.2f}')
    else:
        st.metric("DÉCIFIT MENSAL",f'R$ {saldo_mensal:.2f}')

st.divider()

# Tabela e Gráfico com gastos discriminados por categoria:

st.header(f"Item 2 - Representatividade dos gastos:")

st.subheader("Gastos por Categoria")
if st.toggle("Ilustrar em gráfico",value=False):
    tb_gastos_categoria = calc_gastos_por_categoria(base_dados, filtro_mes, filtro_ano, filtro_centro_custo, filtro_meio_pgto, filtro_instituicao_financeira)
    gf_gasto_categoria = px.bar(tb_gastos_categoria.sort_values("Valor", ascending=True), x='Valor', orientation='h')
    gf_gasto_categoria.update_layout(width = 1200)
    st.plotly_chart(gf_gasto_categoria)
        
else:
    receita_mensal = filtrar_tabela(base_dados, filtro_mes, filtro_ano, filtro_centro_custo, "Receita", filtro_meio_pgto, filtro_instituicao_financeira)["Valor"].sum()

    categoria_df = filtrar_tabela(base_dados, filtro_mes, filtro_ano, filtro_centro_custo, "Despesa", filtro_meio_pgto, filtro_instituicao_financeira)
    categoria = list(categoria_df["Categoria"].unique())

    for c in categoria:
        categoria_df_2 = categoria_df[categoria_df["Categoria"] == c]
        with st.expander(f"{c} // R$ {categoria_df_2["Valor"].sum():.2f} // {(categoria_df_2["Valor"].sum()/receita_mensal)*100:.2f}%"):
            st.dataframe(categoria_df_2)

st.divider()

st.title("Evolução das Entradas e Saídas ao longo dos meses")

# Lista com a evolução das receitas e despesas para serem plotadas em um gráfico de barras:

col101, col102, col103, col104 = st.columns(4)

filtro_centro_custo_2 = col101.multiselect("Filtrar Centro de Custo", base_dados['Centro de Custo'].unique())
filtro_ano_2 = col102.selectbox("Selecionar o Ano", list(range(2023,2025)))
filtro_meio_pgto2 = col103.multiselect("Selecionar Meio de Pagamento", list(base_dados['Meio de Pagamento'].unique()))
filtro_instituicao_financeira2 = col104.multiselect("Selecionar Instituição Financeira", list(base_dados['Instituição Bancária'].unique()))

lista_receita_joao = listar_mvto(base_dados, filtro_ano_2, filtro_centro_custo_2, "Receita", filtro_meio_pgto2, filtro_instituicao_financeira2)
lista_gasto_joao = listar_mvto(base_dados, filtro_ano_2, filtro_centro_custo_2, "Despesa", filtro_meio_pgto2, filtro_instituicao_financeira2)
meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
         "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

def plotar_barras (lista_receita_joao, lista_gasto_joao, meses):
    fig = go.Figure(
        data = [
            go.Bar(x = meses, y=lista_receita_joao, name= "Receita"),
            go.Bar(x = meses, y=lista_gasto_joao, name= "Despesa", marker_color="red")
        ]
    )

    fig.update_layout(
        width=1200, # largura em pixels
        height = 500 # altura em pixels
    )

    return st.plotly_chart(fig)

plotar_barras(lista_receita_joao, lista_gasto_joao, meses)