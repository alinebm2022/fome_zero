# bibliotecas necessárias
import pandas as pd
from haversine import haversine
import folium
import plotly.express as px
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import streamlit as st
from PIL import Image
from datetime import datetime

st.set_page_config (page_title='Visão Países', page_icon="🌎", layout='wide')

# ================================================================================================
# Baixando o arquivo
# ================================================================================================

# lendo o arquivo importado
df = pd.read_csv('zomato.csv')
print (df.head())

# Guardar o DF num DF auxiliar df1
df1 = df.copy()

# ================================================================================================
# Funções:
# ================================================================================================

# Limpeza de dados:
def clean_code(df1):
    """ Esta funcao tem a responsabilidade de limpar o dataframe
        
        Tipos de limpeza:
        1. Remover a coluna Switch to order menu pois tem o mesmo valor em todas as linhas
        2. Remover as linhas duplicadas
        3. Remover as NaNs de todas as observações que possuem NaN em alguma variável
        
        Input: Dataframe
        Output: Dataframe
    """
    # 1. Remover a coluna Switch to order menu pois tem o mesmo valor em todas as linhas
    df1 = df1.drop('Switch to order menu', axis=1)

    # 2. Remover as linhas duplicadas
    df1 = df1.drop_duplicates()
    
    # 3. Remover as NaNs de todas as observações que possuem NaN em alguma variável
    df1 = df1.dropna()
    
    return df1


# Preenchimento do nome dos países
COUNTRIES = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",
}
def country_name(country_id):
  return COUNTRIES[country_id]

# --------------------------------------------------------------------------------------
# Criação do Tipo de Categoria de Comida
def create_price_tye(price_range):
  if price_range == 1:
    return "cheap"
  elif price_range == 2:
    return "normal"
  elif price_range == 3:
    return "expensive"
  else:
    return "gourmet"
    
# --------------------------------------------------------------------------------------
# Renomear as colunas do DataFrame
def rename_columns(dataframe):
  df = dataframe.copy()
  title = lambda x: inflection.titleize(x)
  snakecase = lambda x: inflection.underscore(x)
  spaces = lambda x: x.replace(" ", "")
  cols_old = list(df.columns)
  cols_old = list(map(title, cols_old))
  cols_old = list(map(spaces, cols_old))
  cols_new = list(map(snakecase, cols_old))
  df.columns = cols_new

  return df
# --------------------------------------------------------------------------------------

def bar_pais (df1, agrup, nome):
    cols = ['Country', agrup]
    df_aux = df1.loc[:, cols].groupby('Country').nunique().sort_values(agrup, ascending=False).reset_index()
    fig =  px.bar(df_aux, 
                  x='Country', 
                  y=agrup, 
                  labels={'Country': 'Países', agrup: nome},
                  text_auto=True
                )
    return fig

# -----------------------------------------------------------------------------------------------------------------

def media_pais (df1, agrup, nome):
    cols = ['Country', agrup]
    df_aux = (df1.loc[:, cols]
                 .groupby('Country')
                 .mean()
                 .sort_values(agrup, ascending=False)
                 .reset_index())
        # Formatando os valores com 2 casas decimais
    df_aux[agrup] = df_aux[agrup].map('{:.2f}'.format)
    fig =  px.bar(df_aux, 
            x='Country', 
            y=agrup, 
            labels={'Country': 'Países', agrup: nome},
            text_auto=True
        )
    return fig
# =========================================================================================================
# ---------------------------------------- Inicio da estrutura lógica do código ---------------------------
# =========================================================================================================

# Import dataset
df = pd.read_csv('zomato.csv')

# Limpando os dados
df1 = clean_code (df)

# Categorizar os restaurantes somente por um tipo de culinária:
df1["Cuisines"] = df1.loc[:, "Cuisines"].apply(lambda x: x.split(",")[0])

# Criar uma nova coluna com os nomes dos países
df1["Country"] = df1["Country Code"].apply(country_name)



# =================================================================================================
# Barra Lateral
# =================================================================================================

image_path = 'comida.jpg'
image = Image.open('comida.jpg')
st.sidebar.image(image, width = 120)

st.sidebar.markdown('# Fome Zero')
st.sidebar.markdown("""____""")

st.sidebar.markdown('## Filtros')


# Lista de países disponíveis
country_options = list(COUNTRIES.values())

# Países selecionados
default_countries = ['Brazil', 'England', 'Qatar', 'South Africa', 'Canada', 'Australia']

# Seleção do usuário
selected_countries = st.sidebar.multiselect(
    "Escolha os países que deseja visualizar os restaurantes",
    country_options,
    default=default_countries # deixa só os países selecionados
)

# Filtrar dataframe com base na seleção
df1 = df1[df1["Country"].isin(selected_countries)]

st.sidebar.markdown("""____""")
st.sidebar.markdown('### Powered by Aline Barreto')


# ===============================================================================================
# Primeira página
# ==============================================================================================

st.markdown('# 🌎 Visão País')
with st.container():
    st.markdown('### Quantidade de restaurantes por País')
    fig = bar_pais(df1, agrup = 'Restaurant Name', nome='Quantidade de restaurantes')
    st.plotly_chart(fig, use_container_width=True)

with st.container():
    st.markdown('### Quantidade de cidades registradas por País')
    fig = bar_pais(df1, agrup = 'City', nome='Quantidade de Cidades')
    st.plotly_chart(fig, use_container_width=True)

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('### Média de avaliação por país')
        fig = media_pais(df1, agrup = 'Votes', nome = 'Quantidade de Avaliações')
        st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown('### Média de preço de um prato para duas pessoas por país')
            fig = media_pais(df1, agrup = 'Average Cost for two', nome = 'Preço de prato para duas pessoas')
            st.plotly_chart(fig, use_container_width=True)
