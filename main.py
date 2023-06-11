import pymysql
import pandas as pd
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
    password='PeliNegraBlanca',
    database='pi_movies',
    port=3306
)   '''

app = FastAPI()


''' Funcion 1: Se ingresa el mes y la funcion retorna la cantidad de peliculas que se estrenaron ese mes historicamente '''
@app.get('/cantidad_filmaciones_mes/{mes}')
def cantidad_filmaciones_mes(mes:str):
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
@app.get('/cantidad_filmaciones_dia/{dia}')
def cantidad_filmaciones_dia(dia:str):
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

'''Funcion 3 Se ingresa titulo filmacion, retornando titulo, anho de estreno y score'''
@app.get('/score_titulo/{titulo}')
def score_titulo(titulo: str):
    with connection.cursor() as cursor:
        query = """
            SELECT `release_year`, `popularity`
            FROM `movies`
            WHERE title = '{}'
        """.format(titulo)
        cursor.execute(query)
        result = cursor.fetchone()
        anho = result[0]
        score = result[1]
    return {'Titulo': titulo, 'Anho': anho, 'Popularidad': score}

''' Funcion 4 Ingresa titulo, retorna el titulo, la cantidad de votos y el promedio de votaciones'''
@app.get('/votos_titulo/{titulo}')
def votos_titulo(titulo:str):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT `release_year`, `vote_count`, `vote_average` FROM `movies` WHERE `title` LIKE '%{titulo}%';")
        respuesta = cursor.fetchone()
    anho = respuesta[0]
    num_votos = respuesta[1]
    prom_votos = respuesta[2]
    if num_votos < 2000:
        return {'Tiene menos de 2000 votos'}
    return {'Titulo':titulo, 'Anho de Estreno':anho, 'Numero de Votos':num_votos , 'Promedio de votos':prom_votos}

'''Funcion 5 Ingresa nombre de actor, retornando la ganancia toal y la cantidad de peliculas y promedio ganancia '''
@app.get('/get_actor/{actor}')
def get_actor(actor:str):
    with connection.cursor() as cursor:
        query = """
            SELECT SUM(`return`), COUNT(*)
            FROM movies
            WHERE actors LIKE '%{}%';
        """.format(actor)
        cursor.execute(query)
        resultado = cursor.fetchone()
        ganancia = resultado[0]
        num_peliculas = resultado[1]
        prom_ganancia = ganancia/num_peliculas
    return {'Actor':actor, 'Numero de Peliculas':num_peliculas, 'Ganancia Total':ganancia, 'Ganancia Promedio':prom_ganancia}

'''Funcion 6 Ingresa nombre de director, retornando ganancia total, y lista de peliculas con la fecha de lanzamiento, retorno y g'''
@app.get('/get_director/{director}')
def get_director(director:str):
    with connection.cursor() as cursor:
        query1 = """
            SELECT SUM(`return`)
            FROM movies
            WHERE director LIKE '%{}%';
        """.format(director)
        cursor.execute(query1)
        ganancia = cursor.fetchone()
        query2 = """
            SELECT title, release_year, budget, revenue, `return`
            FROM movies
            WHERE director LIKE '%{}%';
        """.format(director)
        cursor.execute(query2)
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

# ML


''' Ingresas un nombre de pelicula y te recomienda las similares en una lista    '''
@app.get('/recomendacion/{titulo}')
def recomendacion(titulo:str):
    
    cursor = connection.cursor()
    query = f"SELECT genres, original_language FROM movies WHERE title LIKE '%{titulo}%'"
    cursor.execute(query)
    resultado = cursor.fetchone()

    # Extracting the genre string from the response (assuming it's the first and only element)
    genre_string = resultado[0]
    # List of genres to check for in the given order
    genres_to_check = ['TV Movie', 'Western', 'War', 'History', 'Music', 'Animation', 'Fantasy', 'Mystery', 'Family', 'Science Fiction', 'Adventure', 'Documentary', 'Crime', 'Horror', 'Action', 'Romance', 'Thriller', 'Comedy', 'Drama']
    # Variable to store the matching genre
    genre = None
    # Iterate through the genres to check
    for genre_to_check in genres_to_check:
        if genre_to_check in genre_string:
            genre = genre_to_check
            break
    idioma = resultado[1]

    movies = pd.read_sql(f"SELECT title FROM movies WHERE genres LIKE '%{genre}%' AND original_language LIKE '%{idioma}%'", con=connection)

    query = f"SELECT title FROM movies WHERE genres LIKE '%{genre}%' AND original_language LIKE '%{idioma}%'"
    cursor.execute(query)
    movies_data = cursor.fetchall()

    if not movies_data:
        return {'error': 'No se encontraron peliculas'}
    
    movies = pd.DataFrame(movies_data, columns=['title'])

    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(movies["title"])

    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    def get_recommendations(title):
        # Get the index of the movie that matches the title
        idx = movies[movies['title'] == title].index[0]
        # Get the pairwise similarity scores of all movies with that movie
        sim_scores = list(enumerate(cosine_sim[idx]))
        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        # Get the indices of the 10 most similar movies
        sim_indices = [i[0] for i in sim_scores[1:11]]
        # Return the titles of the 10 most similar movies
        return movies['title'].iloc[sim_indices]
    
    recommended_movies = get_recommendations(titulo)

    return {'lista recomendada': recommended_movies} 
