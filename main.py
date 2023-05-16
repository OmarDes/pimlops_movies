import pymysql
from fastapi import FastAPI
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi import Request


''' Conexion AWS  '''
connection = pymysql.connect(
    host='database1.c9chjjynggol.us-east-1.rds.amazonaws.com',
    user='admin',
    password='eustht45tOtk',
    database='pi_mlops',
    port=3306
)

''' Conexion Servidor Local 
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='**********',
    database='pi_mlops',
    port=3306
) '''

app = FastAPI()
templates = Jinja2Templates(directory="templates")


''' Funcion 1: Se ingresa el mes y la funcion retorna la cantidad de peliculas que se estrenaron ese mes historicamente '''
@app.get('/peliculas_mes/{mes}')
def peliculas_mes(mes:str):
    mes_num : int
    if mes == 'enero':
        mes_num = 1
    elif mes == 'febrero':
        mes_num = 2
    elif mes == 'marzo':
        mes_num = 3
    elif mes == 'abril':
        mes_num = 4
    elif mes == 'mayo':
        mes_num = 5
    elif mes == 'junio':
        mes_num = 6
    elif mes == 'julio':
        mes_num = 7
    elif mes == 'agosto':
        mes_num = 8
    elif mes == 'septiembre':
        mes_num = 9
    elif mes == 'octubre':
        mes_num = 10
    elif mes == 'noviembre':
        mes_num = 11
    elif mes == 'diciembre':
        mes_num = 12
    else:
        respuesta = 0
        mes_num = 0
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM movies WHERE MONTH(release_date) = {mes_num}")
        respuesta = cursor.fetchone()
    return {'mes':mes, 'cantidad':respuesta}

''' Funcion 2: Se ingresa el dia y la funcion retorna la cantidad de peliculas que se estrenaron ese dia historicamente '''
@app.get('/peliculas_dia/{dia}')
def peliculas_dia(dia:str):
    day : str
    if dia == 'lunes':
        day = 'monday'
    elif dia == 'martes':
        day = 'tuesday'
    elif dia == 'miercoles':
        day = 'wednesday'
    elif dia == 'jueves':
        day = 'thursday'
    elif dia == 'viernes':
        day = 'friday'
    elif dia == 'sabado':
        day = 'saturday'
    elif dia == 'domingo':
        day = 'sunday'
    else:
        day = ''
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM movies WHERE DAYNAME(release_date) = '{day}'")
        respuesta = cursor.fetchone()
        
    return {'dia':dia, 'cantidad':respuesta}

'''Funcion 3 Se ingresa la franquicia, retornando la cantidad de peliculas, ganancia total y promedio'''
@app.get('/franquicia/{franquicia}')
def franquicia(franquicia: str):
    with connection.cursor() as cursor:
        query = """
            SELECT COUNT(*) AS num_rows, SUM(revenue) AS total_revenue
            FROM movies
            WHERE belongs_to_collection LIKE '%{}%'
        """.format(franquicia)
        cursor.execute(query)
        result = cursor.fetchone()
        num_rows = result[0]
        total_revenue = result[1]
        ganancia_promedio = total_revenue / num_rows if num_rows > 0 else 0
    return {'franquicia': franquicia, 'cantidad': num_rows, 'ganancia_total': total_revenue, 'ganancia_promedio': ganancia_promedio}

''' Funcion 4 Ingresas el pais, retornando la cantidad de peliculas producidas en el mismo'''
@app.get('/peliculas_pais/{pais}')
def peliculas_pais(pais:str):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) AS total_rows FROM movies WHERE production_countries LIKE '%{pais}%';")
        respuesta = cursor.fetchone()
    return {'pais':pais, 'cantidad':respuesta}

'''Funcion 5 Ingresas la productora, retornando la ganancia toal y la cantidad de peliculas que produjeron '''
@app.get('/productoras/{productora}')
def productoras(productora:str):
    with connection.cursor() as cursor:
        query = """
            SELECT COUNT(*) AS total_rows, SUM(revenue) AS total_revenue
            FROM movies
            WHERE production_companies LIKE '%{}%';
        """.format(productora)
        cursor.execute(query)
        result = cursor.fetchone()
        num_movies = result[0]
        total_revenue = result[1]
    return {'productora':productora, 'ganancia_total':total_revenue, 'cantidad':num_movies}

'''Funcion 6 Ingresa la pelicula, retornando la inversion, la ganancia, el retorno y el año en el que se lanzo'''
@app.get('/retorno/{pelicula}')
def retorno(pelicula:str):
    with connection.cursor() as cursor:
        query = """
            SELECT `budget`, `revenue`, `return`, `release_year`
            FROM movies
            WHERE title LIKE '{}';
        """.format(pelicula)
        cursor.execute(query)
        result = cursor.fetchone()
        rep_inversion = result[0]
        rep_ganancia = result[1]
        rep_retorno= result[2]
        rep_anio= result[3]
    return {'pelicula':pelicula, 'inversion':rep_inversion, 'ganacia':rep_ganancia,'retorno':rep_retorno, 'anio':rep_anio}

# ML

'''Ingresas un nombre de pelicula y te recomienda las similares en una lista '''
@app.get('/recomendacion/{titulo}')
def recomendacion(titulo:str):
    
    query = "SELECT title FROM movies" 
    df = pd.read_sql(query, connection) #Carga de datos

    df['preprocessed_text'] = df['title'].fillna('')
    df['preprocessed_text'] = df['preprocessed_text'].str.lower()

    tfidf = TfidfVectorizer(max_features=50)
    feature_vectors = tfidf.fit_transform(df['preprocessed_text']).toarray()

    # Calculate pairwise cosine similarity
    cosine_sim_matrix = cosine_similarity(feature_vectors)
    
    movie_index = df[df['{titulo}'] == titulo].index[0] #encontrar indice de pelicula en df
    
    movie_scores = list(enumerate(cosine_sim_matrix[movie_index]))

    # Sort the movies based on similarity scores
    movie_scores = sorted(movie_scores, key=lambda x: x[1], reverse=True)

    # Get top 5 similar movies (excluding the input movie itself)
    top_movies = movie_scores[1:6]

    # Retrieve the titles of the recommended movies
    recommended_movies = [df.iloc[movie[0]]['{titulo}'] for movie in top_movies]
    
    return {'lista recomendada': recommended_movies}
