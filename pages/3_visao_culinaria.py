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

st.set_page_config (page_title='Visão Culinária', page_icon="🍽️", layout='wide')

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


# -----------------------------------------------------------------------------------------
# Criação do nome das Cores

COLORS = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
"FFBA00": "red",
"CBCBC8": "darkred",
"FF7800": "darkred",
}
def color_name(color_code):
  return COLORS[color_code]
    
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

def melhores_restaurantes_por_culinaria(df, culinarias=None):
    # Lista padrão de culinárias se nenhuma for passada
    if culinarias is None:
        culinarias = ['Italian', 'Japanese', 'Brazilian', 'Arabian', 'American']

    colunas = st.columns(len(culinarias))  # cria o número de colunas com base na lista

    for culinaria, col in zip(culinarias, colunas):
        with col:
            df_aux = (df[df['Cuisines'] == culinaria]
                      .sort_values('Aggregate rating', ascending=False)
                      .reset_index(drop=True))

            st.markdown(f"#### {culinaria}")

            if not df_aux.empty:
                restaurante = df_aux.iloc[0]

                nome = restaurante['Restaurant Name']
                nota = restaurante['Aggregate rating']
                pais = restaurante['Country']
                cidade = restaurante['City']
                custo = restaurante['Average Cost for two']

                tooltip = f"País: {pais}\nCidade: {cidade}\nMédia prato para dois: {custo}"

                st.button(f"{nome} - {nota:.1f}/5.0", help=tooltip)
            else:
                st.markdown("Nenhum restaurante encontrado.")
# ----------------------------------------------------------------------------------------------------------
def top_tab (df1):
    cols = ['Restaurant Name', 'Country', 'City','Cuisines', 'Average Cost for two','Aggregate rating', 'Votes']

    df_aux = (
        df1.loc[:, cols]
           .groupby('Restaurant Name')
           .agg({
               'Country': 'first',
               'City': 'first',
               'Cuisines': 'first',
               'Average Cost for two': 'mean',
               'Aggregate rating': 'mean',
               'Votes': 'sum'
           })
           .sort_values('Aggregate rating', ascending=False)
           .reset_index()
    )

    # Selecionar os Top N com base no slider
    df_top = df_aux.head(date_slider)
    df_top.index = df_top.index + 1  # começa do 1
    df_top.index.name = 'Posição'      # (opcional) nome do índice
    return df_top

# ----------------------------------------------------------------------------------------------------------
def top_cuisine (df1, top_asc):
    cols = ['Aggregate rating', 'Cuisines']
    df_aux = (df_full.loc[:, cols]
            .groupby('Cuisines')['Aggregate rating']
            .mean()
            .sort_values(ascending = top_asc)
            .reset_index())
    df_aux['Aggregate rating'] = df_aux['Aggregate rating'].round(2)

    # Selecionar os Top N com base no slider
    df_top_n = df_aux.head(date_slider)

    fig = px.bar(
        df_top_n,
        x='Cuisines',
        y='Aggregate rating',
        labels={
            'Cuisines': 'Tipo de Culinária',
            'Aggregate rating': 'Méida da Avaliação Média',
            },
            text_auto=True,
            category_orders={
            'Cuisines': df_top_n.sort_values(by = 'Aggregate rating', ascending=top_asc)['Cuisines']
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

df_full = df1.copy()

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
    default = default_countries # deixa só os países selecionados
    # default=[]  # Não deixa nenhum país selecionado
   # default=country_options  # Mantém todos selecionados por padrão
)

# Quantidade de tipos que deseja visualizar
date_slider = st.sidebar.slider(
    "Selecione a quantidade de restaurantes que deseja visualizar",
    min_value=1,
    max_value=20,
    value=10  # valor inicial (pode ajustar se quiser)
)

# Lista única e ordenada dos tipos de culinária
unique_cuisines = sorted(df1["Cuisines"].dropna().unique())

# Culinárias que você quer deixar selecionadas por padrão
default_cuisines = ['Italian', 'Japanese', 'Arabian', 'Brazilian', 'Home-made', 'American']

# Seleção do usuário
selected_cuisines = st.sidebar.multiselect(
    "Escolha os Tipos de Culinária",
    options=unique_cuisines,
    default=default_cuisines  # Não deixa nenhuma culinária selecionada
)

# Filtrar dataframe com base na seleção

df1 = df1[df1["Country"].isin(selected_countries)]
df1 = df1[df1["Cuisines"].isin(selected_cuisines)]

st.sidebar.markdown("""____""")
st.sidebar.markdown('### Powered by Aline Barreto')


# ===============================================================================================
# Primeira página
# ==============================================================================================
st.markdown('# 🍽️ Visão Culinária')

with st.container():
    st.markdown('## Melhores Restaurantes dos Principais tipos Culinários')
    melhores_restaurantes_por_culinaria(df1)
    
with st.container():
    st.markdown(f'## Top {date_slider} Restaurantes')
    df_top = top_tab(df1) 
    # Exibir no Streamlit como tabela (ou print se for JupyterLab)
    st.dataframe(df_top)
   
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'## Top {date_slider} Melhores Tipos de Culinária')
        fig = top_cuisine (df1, top_asc=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f'## Top {date_slider} Piores Tipos de Culinária')
        fig = top_cuisine (df1, top_asc=True)
        st.plotly_chart(fig, use_container_width=True)