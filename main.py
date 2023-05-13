from fastapi import FastAPI


app = FastAPI()

@app.get('/peliculas_mes/{mes}')
def peliculas_mes(mes:str):
    '''Se ingresa el mes y la funcion retorna la cantidad de peliculas que se estrenaron ese mes historicamente'''
    respuesta = 'hola mundo'
    return {'mes':mes, 'cantidad':respuesta}