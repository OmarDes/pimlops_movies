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
    database='pi_mlops',
    port=3306
)   

''' Conexion Servidor Local     
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='pi_movies',
    port=3306
)   '''

app = FastAPI()


''' Funcion 1: Se ingresa el mes y la funcion retorna la cantidad de peliculas que se estrenaron ese mes historicamente '''
@app.get('/cantidad_filmaciones_mes/{mes}')
def cantidad_filmaciones_mes(mes:str):
    mes_num : int
    if mes == 'enero':  #El nombre de mes ingresado en espanhol es contrastado para asignar un valor a la variable 'mes_num'
        mes_num = 1     #La query para el la base de datos usa un numero para identificar cada mes
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
    with connection.cursor() as cursor: #Consulta a la base de datos
        cursor.execute(f"SELECT COUNT(*) FROM movies WHERE MONTH(release_date) = {mes_num}")
        respuesta = cursor.fetchone()
    return {'mes':mes, 'cantidad':respuesta}

''' Funcion 2: Se ingresa el dia y la funcion retorna la cantidad de peliculas que se estrenaron ese dia historicamente '''
@app.get('/cantidad_filmaciones_dia/{dia}')
def cantidad_filmaciones_dia(dia:str):
    day : str
    if dia == 'lunes':  #El parametro de la consulta a la base de datos es el nombre del dia en ingles
        day = 'monday'  #Se traduce del espanhol al ingles y se almacena en la variable 'day'
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
    with connection.cursor() as cursor: #Consulta a la base de datos
        cursor.execute(f"SELECT COUNT(*) FROM movies WHERE DAYNAME(release_date) = '{day}'")
        respuesta = cursor.fetchone()
        
    return {'dia':dia, 'cantidad':respuesta}

'''Funcion 3 Se ingresa titulo filmacion, retornando titulo, anho de estreno y score'''
@app.get('/score_titulo/{titulo}')
def score_titulo(titulo: str):
    with connection.cursor() as cursor: #Consulta a la base de datos
        query = """
            SELECT `release_year`, `popularity`
            FROM `movies`
            WHERE title = "{}"
        """.format(titulo)
        cursor.execute(query)
        result = cursor.fetchone()
        anho = result[0]
        score = result[1]
    return {'Titulo': titulo, 'Anho': anho, 'Popularidad': score}

''' Funcion 4 Ingresa titulo, retorna el titulo, la cantidad de votos y el promedio de votaciones'''
@app.get('/votos_titulo/{titulo}')
def votos_titulo(titulo:str):
    with connection.cursor() as cursor: #Consulta a la base de datos
        query = """
            SELECT `release_year`, `vote_count`, `vote_average` 
            FROM `movies`
            WHERE `title` LIKE "%{}%"
        """.format(titulo)
        cursor.execute(query)
        respuesta = cursor.fetchone()
    anho = respuesta[0]
    num_votos = respuesta[1]
    prom_votos = respuesta[2]
    if num_votos < 2000:    #Se evalua la condicion de tener no tener menos de 2000 votos
        return {'Tiene menos de 2000 votos'}
    return {'Titulo':titulo, 'Anho de Estreno':anho, 'Numero de Votos':num_votos , 'Promedio de votos':prom_votos}

'''Funcion 5 Ingresa nombre de actor, retornando la ganancia toal y la cantidad de peliculas y promedio ganancia '''
@app.get('/get_actor/{actor}')
def get_actor(actor:str):
    with connection.cursor() as cursor: #Consulta a la base de datos
        query = """
            SELECT SUM(`return`), COUNT(*)
            FROM movies
            WHERE actors LIKE "%{}%";
        """.format(actor)
        cursor.execute(query)
        resultado = cursor.fetchone()
        ganancia = resultado[0]
        num_peliculas = resultado[1]
        prom_ganancia = ganancia/num_peliculas  #Calculo promedio de la ganancia con el resultado de la consulta
    return {'Actor':actor, 'Numero de Peliculas':num_peliculas, 'Ganancia Total':ganancia, 'Ganancia Promedio':prom_ganancia}

'''Funcion 6 Ingresa nombre de director, retornando ganancia total, y lista de peliculas con la fecha de lanzamiento, retorno y g'''
@app.get('/get_director/{director}')
def get_director(director:str):
    with connection.cursor() as cursor: #Consulta a la base de datos
        query1 = """
            SELECT SUM(`return`)
            FROM movies
            WHERE director LIKE "%{}%";
        """.format(director)
        cursor.execute(query1) #Primero se consulta la ganancia total del Director
        ganancia = cursor.fetchone()
        query2 = """
            SELECT title, release_year, budget, revenue, `return`
            FROM movies
            WHERE director LIKE "%{}%";
        """.format(director)
        cursor.execute(query2)  #La segunda consulta trae la informacion solicitada de todas las peliculas del director
        movies_data = cursor.fetchall()
        data = {} #Creo diccionario para almacenar los resultados
        data['Director'] = director
        data['Ganancia Total'] = ganancia[0]
        data['Peliculas'] = []
        for row in movies_data:
            pelicula = {}
            pelicula['Titulo'] = row[0]
            pelicula['Anho de lanzamiento'] = row[1]
            pelicula['Presupuesto'] = row[2]
            pelicula['Ganancia'] = row[3]
            pelicula['Retorno'] = row[4]
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

    return {'lista recomendada': recommended_movies} 
