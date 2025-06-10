import streamlit as st
from PIL import Image
import pandas as pd
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import folium
from streamlit_folium import folium_static


st.set_page_config (
    page_title="Home",
    page_icon="🎲",
     layout='wide'
)
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


# --------------------------------------------------------------------------------------------------
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

# Criar uma nova coluna com os nomes dos países
df1["Country"] = df1["Country Code"].apply(country_name)


def country_maps(df1):
    cols = ['Restaurant Name', 'City', 'Latitude', 'Longitude', 'Average Cost for two', 'Cuisines', 'Aggregate rating']
    df_aux = df1[cols].dropna(subset=['Latitude', 'Longitude'])

    # Cria o mapa centralizado
    map = folium.Map(location=[df_aux['Latitude'].mean(), df_aux['Longitude'].mean()], zoom_start=2)
    marker_cluster = MarkerCluster().add_to(map)

    # Adiciona marcadores detalhados
    for index, row in df_aux.iterrows():
        name = row['Restaurant Name']
        city = row['City']
        cost = row['Average Cost for two']
        cuisine = row['Cuisines']
        rating = row['Aggregate rating']

        popup_text = (
            f"<b>{name}</b><br>"
            f"City: {city}<br>"
            f"Price: {cost:.2f} (Dollar$) para dois<br>"
            f"Type: {cuisine}<br>"
            f"Aggregate Rating: {rating:.1f}/5.0"
        )

        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=popup_text,
            icon=folium.Icon(color="green", icon="cutlery", prefix='fa')
        ).add_to(marker_cluster)

    folium_static(map, width=1024, height=600)



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
df_full = df1.copy()
df1 = df1[df1["Country"].isin(selected_countries)]

st.sidebar.markdown("""____""")
st.sidebar.markdown('### Dados Tratados')
# Botão de download dos dados tratados
csv = df1.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📅 Baixar CSV",
    data=csv,
    file_name='dados_tratados.csv',
    mime='text/csv'
)
# ===============================================================================================
# Home
# ===============================================================================================
st.markdown('# Fome Zero!')
st.markdown('## O melhor lugar para encontrar seu mais novo restaurante favorito!')

with st.container():
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown('#### Restaurantes cadastrados')
        df_aux = df_full['Restaurant ID'].nunique()
        st.markdown(f"#### {df_aux}")
    with col2:
        st.markdown('#### Países cadastrados')
        df_aux = df_full['Country'].nunique()
        st.markdown(f"#### {df_aux}")
    with col3:
        st.markdown('#### Cidades cadastradas')
        df_aux = df_full['City'].nunique()
        st.markdown(f"#### {df_aux}")
    with col4:
        st.markdown('#### Avaliações feitas na plataforma')
        df_aux = df_full['Votes'].sum()
        st.markdown(f"#### {df_aux:,.0f}".replace(",", "."))

with st.container():
    st.markdown('# Country Maps')
    country_maps (df1)
    

