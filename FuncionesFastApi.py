import pymysql
from fastapi import FastAPI

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='PeliNegraBlanca',
    database='pi_mlops'
)

app = FastAPI()

@app.get('/peliculas_mes/{mes}')
def peliculas_mes(mes:str):
    '''Se ingresa el mes y la funcion retorna la cantidad de peliculas que se estrenaron ese mes historicamente'''
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

@app.get('/peliculas_dia/{dia}')
def peliculas_dia(dia:str):
    '''Se ingresa el dia y la funcion retorna la cantidad de peliculas que se estrebaron ese dia historicamente'''
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

@app.get('/franquicia/{franquicia}')
def franquicia(franquicia:str):
    '''Se ingresa la franquicia, retornando la cantidad de peliculas, ganancia total y promedio'''
    return {'franquicia':franquicia, 'cantidad':respuesta, 'ganancia_total':respuesta, 'ganancia_promedio':respuesta}

@app.get('/peliculas_pais/{pais}')
def peliculas_pais(pais:str):
    '''Ingresas el pais, retornando la cantidad de peliculas producidas en el mismo'''
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM movies WHERE JSON_SEARCH(production_countries, 'one', '{pais}', NULL, '$[*].\"name\"') IS NOT NULL")
        respuesta = cursor.fetchone()
    return {'pais':pais, 'cantidad':respuesta}

@app.get('/productoras/{productora}')
def productoras(productora:str):
    '''Ingresas la productora, retornando la ganancia toal y la cantidad de peliculas que produjeron'''
    return {'productora':productora, 'ganancia_total':respuesta, 'cantidad':respuesta}

@app.get('/retorno/{pelicula}')
def retorno(pelicula:str):
    '''Ingresas la pelicula, retornando la inversion, la ganancia, el retorno y el año en el que se lanzo'''
    return {'pelicula':pelicula, 'inversion':respuesta, 'ganacia':respuesta,'retorno':respuesta, 'anio':respuesta}

# ML
@app.get('/recomendacion/{titulo}')
def recomendacion(titulo:str):
    '''Ingresas un nombre de pelicula y te recomienda las similares en una lista'''
    return {'lista recomendada': respuesta}
