import pymysql
import pandas as pd
import re
from fastapi import FastAPI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


''' Conexion AWS  '''
connection = pymysql.connect(
    host='database1.c9chjjynggol.us-east-1.rds.amazonaws.com',
    user='admin',
    password='eustht45tOtk',
    database='pi_movies',
    port=3306
)   

''' Conexion Servidor Local     
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='PeliNegraBlanca',
    database='pi_movies',
    port=3306
)   '''

app = FastAPI()


''' Funcion 1: Se ingresa un idioma, devuelve la cantidad de peliculas producidas en ese idioma '''
@app.get('/peliculas_idioma/{idioma}')
def peliculas_idioma(idioma:str):
    with connection.cursor() as cursor: #Consulta a la base de datos
        cursor.execute(f"SELECT COUNT(*) FROM movies WHERE original_language = '{idioma}'")
        respuesta = cursor.fetchone()
    return {'idioma':idioma, 'cantidad':respuesta}

''' Funcion 2: Se ingresa el titulo de una pelicula, retorna duracion y anho de estreno '''
@app.get('/peliculas_duracion/{pelicula}')
def peliculas_duracion(pelicula:str):
    with connection.cursor() as cursor: #Consulta a la base de datos
        cursor.execute(f"SELECT `runtime` , `release_year`FROM `movies` WHERE `title` = '{pelicula}'")
        respuesta = cursor.fetchone()
        duracion = respuesta[0]
        anio = respuesta[1]
    return {'pelicula':pelicula, 'duracion': duracion,'anio':anio}

'''Funcion 3 Se ingresa la franquicia, retornando la cantidad de peliculas, ganancia total y promedio'''
@app.get('/franquicia/{franquicia}')
def franquicia(franquicia: str):
    with connection.cursor() as cursor:
        query = """
            SELECT COUNT(*) , SUM(revenue)
            FROM movies
            WHERE belongs_to_collection LIKE '%{}%'
        """.format(franquicia)
        cursor.execute(query)
        result = cursor.fetchone()
        cant = result[0]
        total_revenue = result[1]
        ganancia_promedio = total_revenue / cant if cant > 0 else 0
    return {'franquicia': franquicia, 'cantidad': cant, 'ganancia_total': total_revenue, 'ganancia_promedio': ganancia_promedio}

''' Funcion 4 Ingresa el pais, como respuesta da el numero de peliculas producidas ahi '''
@app.get('/peliculas_pais/{pais}')
def peliculas_pais(pais:str):
    with connection.cursor() as cursor: #Consulta a la base de datos
        query = """
            SELECT COUNT(*)
            FROM movies
            WHERE production_countries LIKE "%{}%"
        """.format(pais)
        cursor.execute(query)
        cantidad = cursor.fetchone()
    return {'pais':pais, 'cantidad':cantidad}

'''Funcion 5 Se ingresa productora, la funcion retorna la ganancia total y la cantidad de peliculas que se produjeron '''
@app.get('/productoras_exitosas/{productora}')
def productoras_exitosas(productora:str):
    with connection.cursor() as cursor: #Consulta a la base de datos
        query = """
            SELECT COUNT(*) AS total_peliculas, SUM(revenue) AS total_revenue
            FROM movies
            WHERE production_companies LIKE "%{}%";
        """.format(productora)
        cursor.execute(query)
        resultado = cursor.fetchone()
        cantidad = resultado[0]
        revenue_total = resultado[1]
    return {'productora':productora, 'revenue_total':revenue_total, 'cantidad':cantidad}

'''Funcion 6 Ingresa nombre de director, retornando ganancia total, y lista de peliculas con la fecha de lanzamiento, retorno y g'''
@app.get('/get_director/{director}')
def get_director(nombre_director:str):
    with connection.cursor() as cursor: #Consulta a la base de datos
        query1 = """
            SELECT SUM(`return`)
            FROM movies
            WHERE director LIKE "%{}%";
        """.format(nombre_director)
        cursor.execute(query1) #Primero se consulta la ganancia total del Director
        ganancia = cursor.fetchone()
        query2 = """
            SELECT title, release_year, `return`, budget , revenue
            FROM movies
            WHERE director LIKE "%{}%";
        """.format(nombre_director)
        cursor.execute(query2)  #La segunda consulta trae la informacion solicitada de todas las peliculas del director
        movies_data = cursor.fetchall()
        data = {} #Creo diccionario para almacenar los resultados
        data['Director'] = nombre_director
        data['retorno_total_director'] = ganancia[0]
        data['Peliculas'] = []
        for row in movies_data:
            pelicula = {}
            pelicula['Titulo'] = row[0]
            pelicula['Anho'] = row[1]
            pelicula['retorno_pelicula'] = row[2]
            pelicula['budget_pelicula'] = row[3]
            pelicula['revenue_pelicula'] = row[4]
            data['Peliculas'].append(pelicula)
    return data

# Sistema de recomenadcion - Machine Learning

#Esta funcion elimina caracteres especiales que pueden perturbar el analisis de texto
#Se usa posteriormente
def clean_text(text):   
    return re.sub("[^a-zA-Z0-9 ]","", text)

''' Ingresas un nombre de pelicula y te recomienda las similares en una lista    '''
@app.get('/recomendacion/{titulo}')
def recomendacion(titulo:str):
    with connection.cursor() as cursor: #Primero se hace una consulta para saber el genero
        query = """
            SELECT genres
            FROM movies
            WHERE title LIKE "%{}%"
        """.format(titulo)
        cursor.execute(query)
    resultado = cursor.fetchone()

    genre_string = resultado[0]
    # Listado de generos desde el menos frecuente. Se omite 'TV Movie' y 'Foreing' porque dicen poco sobre el contenido
    # y su posible relacion con otras peliculas
    genres_to_check = ['Western', 'War', 'History', 'Music', 'Animation', 'Fantasy', 'Mystery', 'Family', 'Science Fiction', 'Adventure', 'Documentary', 'Crime', 'Horror', 'Action', 'Romance', 'Thriller', 'Comedy', 'Drama']
    # Variable para almacenar el genero
    genre = ''
    # A la primera coincidencia sale
    for genre_to_check in genres_to_check:
        if genre_to_check in genre_string:
            genre = genre_to_check
            break
   
    with connection.cursor() as cursor: #Trae el listado de todas las peliculas del mismo genero de la pelicula
        query = """SELECT title, overview, tagline, actors, director
                FROM movies
                WHERE genres LIKE "%{}%"
                ORDER BY vote_average DESC
                LIMIT 4000
            """.format(genre)   #Hay un limite de 4000 peliculas para no sobrepasar la capacidad de memoria del servicio de Deploy
        cursor.execute(query)
    movies_data = cursor.fetchall()
    # Se crea un objeto dataframe para almacenar y procesar los datos de las peliculas
    movies = pd.DataFrame(movies_data, columns=['title', 'overview','tagline','actors','director'])
    
    movies = movies.fillna('')
    #Se une a un solo texto todas las palabras de los campos consultados 
    movies['description'] = movies['title'] + ' ' + movies['overview'] + ' ' + movies['tagline'] + ' ' + movies['actors'] + ' ' + movies['director']
    # Se llama la funcion 'clean_text' para eliminar caracteres especiales
    movies["clean_description"] = movies["description"].apply(clean_text)
    #Crea un objeto de la clase TfidfVectorizer
    tfidf = TfidfVectorizer()
    
    tfidf_matrix = tfidf.fit_transform(movies['clean_description'])
    # Se calucula la matriz de similitud entre filas del texto
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    #Esta función toma un título de película como entrada y devuelve los títulos
    # de las 5 películas más similares a esa película en función de la similitud de coseno calculada previamente.
    def get_recommendations(title):
        idx = movies[movies['title'] == title].index[0]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_indices = [i[0] for i in sim_scores[1:6]]
        return movies['title'].iloc[sim_indices]
    
    recommended_movies = get_recommendations(titulo)

    recommended_movies = list(recommended_movies)

    return {'lista recomendada': recommended_movies} 
