import pymysql
from fastapi import FastAPI

''' Conexion AWS '''
connection = pymysql.connect(
    host='database1.c9chjjynggol.us-east-1.rds.amazonaws.com',
    user='admin',
    password='eustht45tOtk',
    database='pi_mlops',
    port=3306
)

app = FastAPI()

@app.get('/load_data/{id}')
def numero_id(id:int):
    respuesta = 'incorrecto'
    if id == 2:
        respuesta = 'correcto'
    return {'mes':id, 'cantidad':respuesta}


@app.get('/peliculas_mes/{mes}')
def peliculas_mes(mes:str):
    #Se ingresa el mes y la funcion retorna la cantidad de peliculas que se estrenaron ese mes historicamente
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
