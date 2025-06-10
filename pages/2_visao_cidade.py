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

st.set_page_config (page_title='Visão Cidades', page_icon="🌆", layout='wide')

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
# -----------------------------------------------------------------------------------------
# Definir cores por país:
country_colors ={
"India": 'yellow',
"Australia": 'darkblue',
"Brazil": 'green',
"Canada": 'red',
"Indonesia": 'orange',
"New Zeland": 'purple',
"Philippines": 'brown',
"Qatar": 'gray',
"Singapure": 'lightblue',
"South Africa": 'pink',
"Sri Lanka": 'darkgreen',
"Turkey": 'darkred',
"United Arab Emirates": 'goldenrod',
"England": 'lightgreen',
"United States of America": 'black',
}

  
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
# Esta funcao top10 tem a responsabilidade de fazer um diagrama em barras
#    com Top 10 cidades com mais restaurantes

def top10 (df1):
    cols = ['Country', 'City', 'Restaurant Name']
    df_aux = (df1.loc[:, cols]
              .groupby(['Country', 'City'])['Restaurant Name']
              .count()
              .sort_values(ascending=False)
              .reset_index())

    # Selecionar apenas as 10 primeiras cidades
    df_top10 = df_aux.head(10)

    # Adicionar coluna de cor
    df_top10['Color'] = df_top10['Country'].map(country_colors)
    
    fig =  px.bar(df_top10, 
                  x='City', 
                  y='Restaurant Name', 
                  color='Country',  # Isso cria a legenda automática
                 color_discrete_map=country_colors,
                 labels={
                     'City': 'Cidades', 
                     'Restaurant Name': 'Quantidade de restaurantes',
                     'Country': 'País'
                 },
                  text_auto=True
                )
    return fig
# -------------------------------------------------------------------------------------------------
# Esta funcao top_tab tem a responsabilidade de fazer uma tabela ordenada com as TOP N 
#    cidades com mais restaurantes. O N é definido pelo usuário no sidebar slider e pode 
#    variar de 1 a 100.
def top_tab(df1):
    cols = ['Country', 'City', 'Restaurant Name']

    df_aux = (
        df1.loc[:, cols]
           .groupby(['Country', 'City'])['Restaurant Name']
           .count()
           .reset_index()
           .sort_values('Restaurant Name', ascending=False)
    )

    # Mostrar as N primeiras cidades com mais restaurantes
    df_top = df_aux.head(date_slider)
    
    # Seleciona as N primeiras cidades e cria coluna de ranking
    df_top = df_aux.head(date_slider).reset_index(drop=True)
    df_top.index = df_top.index + 1  # Ranking começa em 1
    df_top.index.name = 'Ranking'       # Nome da coluna índice
    return df_top

# -----------------------------------------------------------------------------------------------------------

def top7_plus4 (df1):
    cols = ['Country', 'City', 'Aggregate rating', 'Restaurant Name']
    # Filtrar apenas restaurantes com nota > 4
    df_filtered = df1[df1['Aggregate rating'] > 4]
    df_aux = (df_filtered
            .groupby(['Country', 'City'])['Restaurant Name']
            .count()
            .reset_index()
            .sort_values(by='Restaurant Name', ascending=False)
            )
      
    # Selecionar apenas as 7 primeiras cidades
    top7_cidades = df_aux.head(7).copy()
    # Adicionar coluna de cor
    top7_cidades['Color'] = top7_cidades['Country'].map(country_colors)

    fig = px.bar(
        top7_cidades,
        x='City',
        y='Restaurant Name',
        color='Country',
        color_discrete_map=country_colors,
        labels={
            'City': 'Cidades',
            'Restaurant Name': 'Quantidade de restaurantes',
            'Country': 'País'
        },
        text_auto=True,
        category_orders={
        'City': top7_cidades.sort_values(by='Restaurant Name', ascending=False)['City']
        }
    )
    return fig
        
 # --------------------------------------------------------------------------------------------------------       

def top7_less25 (df1):
    cols = ['Country', 'City', 'Aggregate rating', 'Restaurant Name']
    # Filtrar apenas restaurantes com nota < 2.5
    df_filtered = df1[df1['Aggregate rating'] <2.5]
    df_aux = (df_filtered
                .groupby(['Country', 'City'])['Restaurant Name']
                .count()
                .reset_index()
                .sort_values(by='Restaurant Name', ascending=False)
                )
           
    # Selecionar apenas as 7 primeiras cidades
    top7_cidades = df_aux.head(7).copy()


    # Adicionar coluna de cor
    top7_cidades['Color'] = top7_cidades['Country'].map(country_colors)

    fig = px.bar(
        top7_cidades,
        x='City',
        y='Restaurant Name',
        color='Country',
        color_discrete_map=country_colors,
        labels={
            'City': 'Cidades',
            'Restaurant Name': 'Quantidade de restaurantes',
            'Country': 'País'
        },
        text_auto=True,
        category_orders={
        'City': top7_cidades.sort_values(by='Restaurant Name', ascending=False)['City']
        }
    )
    return fig

# ---------------------------------------------------------------------------------------------------------

def top10_cuisine (df1):
    cols = ['Country', 'City', 'Cuisines']
    df_aux = (df1.loc[:, cols]
              .groupby(['Country','City'])
              .nunique()
              .sort_values('Cuisines', ascending=False)
              .reset_index())
    
    top10_cuisine = df_aux.head(10)

    # Adicionar coluna de cor
    top10_cuisine['Color'] = top10_cuisine['Country'].map(country_colors)

    fig =  px.bar(top10_cuisine, 
            x='City', 
            y='Cuisines', 
            color='Country',  # Isso cria a legenda automática
            color_discrete_map=country_colors,
            labels={
                'City': 'Cidades', 
                'Cuisines': 'Quantidade de tipos de culinárias únicas',
                'Country': 'País'
            },
            text_auto=True,
            category_orders={
            'City': top10_cuisine.sort_values(by='Cuisines', ascending=False)['City']
        }
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

# Quantidade de tipos que deseja visualizar usando slider
date_slider = st.sidebar.slider(
    "Selecione a quantidade de restaurantes que deseja visualizar",
    min_value=1,
    max_value=100,
    value=10  # valor inicial (pode ajustar se quiser)
)

st.sidebar.markdown("""____""")
st.sidebar.markdown('### Powered by Aline Barreto')


# ===============================================================================================
# Primeira página
# ==============================================================================================
st.markdown('# 🌆 Visão Cidades')

with st.container():
    st.markdown('#### Top 10 cidades com mais restaurantes')
    fig = top10(df1)
    st.plotly_chart(fig, use_container_width=True)

with st.container():
    st.markdown(f'#### Top {date_slider} cidades com mais restaurantes')
    df_top = top_tab(df1) 
    # Exibir no Streamlit como tabela (ou print se for JupyterLab)
    st.dataframe(df_top)

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('### Top 7 Cidades com Restaurantes com média de avaliação acima de 4')
        fig = top7_plus4(df1)
        st.plotly_chart(fig, use_container_width=True)
       
    with col2:
        st.markdown('### Top 7 Cidades com Restaurantes com média de avaliação abaixo de 2.5')
        fig = top7_less25 (df1)
        st.plotly_chart(fig, use_container_width=True)

with st.container():
    st.markdown('#### Top 10 cidades com maior quantidade de tipos de culinária distintas')
    fig = top10_cuisine (df1)
    st.plotly_chart(fig, use_container_width=True)

