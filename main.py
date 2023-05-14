import pymysql
from fastapi import FastAPI

connection = pymysql.connect(
    host='containers-us-west-102.railway.app',
    user='root',
    password='1c6v9fKryhZk0mnpJQq6',
    database='railway'
)

app = FastAPI()

@app.get('/numero_id/{id}')
def numero_id(id:int):
    '''Se ingresa el id y la funcion retorna la fila'''
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM prueba2 WHERE id = {id}")
        respuesta = cursor.fetchone()
    return {'mes':id, 'cantidad':respuesta}

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