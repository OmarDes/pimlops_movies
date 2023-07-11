<p align=center><img src=https://d31uz8lwfmyn8g.cloudfront.net/Assets/logo-henry-white-lg.png><p>

# <h1 align=center> **PROYECTO INDIVIDUAL Nº1** </h1>

# <h1 align=center>**`Machine Learning Operations (MLOps)`**</h1>

<p align="center">
<img src="https://user-images.githubusercontent.com/67664604/217914153-1eb00e25-ac08-4dfa-aaf8-53c09038f082.png"  height=300>
</p>

**Omar Giovanni Russi**

<hr>  

# **Descripción del problema**
Se requiere construir un sistema de recomendación de películas.

La base de su construcción es un dataset con alrededor de 45 mil registros de películas, de varios orígenes y épocas. La información está dividida en dos archivos. 'movies_dataset.csv' contiene información como fecha de estreno, origen, presupuesto, productoras, etc. El archivo 'credits.csv' tiene información sobre todo el personal que participó en la producción de la película.

# **Desarrolo del Proyecto**

## **EDA**
Primero el dataset es explorado con MS VS studio:
+ Se determinan las dimensiones de ambos dataset, y sus respectivos campos.

+ Se corrigen filas que no permiten su carga en MySQL WorkBench.

+ Se extraen los datos sobre actores y directores de 'credits.csv' y se unen a 'movies_dataset.csv' como columnas adiionales.

+ El archivo donde se desarrolla el proceso es: EDA.ipynb

## **ETL**
Se carga dataset en una base de datos local MySQL, con las instrucciones desarrolladas en el arhchivo 'ETL_MLOps.sql'.

En ese mismo archivo se realizan las transformaciones sugeridas.

Se hacen transformaciones adicionales como eliminar columnas no requeridas para las consultas o eliminar registros duplicados.

Finalmente se carga el dataset depurado a una base de datos MySQL alojada en el servicio de Amazon(AWS).

## **API**

Primero desarrollo las consultas a la base de datos para poder responder a la informacion requeridad por los 6 endpoints que se consumen por la API. Las describo en el archivo 'Consultas_API.sql'.

En el archivo 'main.py' esta el desarrollo de las API, incluida la funcion de ML

La API se desarrolla con el framework FASTAPI. Esta se deploya en el servicio gratuito de render. En el siguiente enlace se puede acceder a la API deployada:

https://mlops-omardes.onrender.com 

Este es el esquema del deployment:

<p align="center">
<img src="https://github.com/OmarDes/pimlops_movies/blob/main/src/EsquemaDeployment.PNG"  height=300>
</p>

## **Modelo de Recomendacion**

Se utiliza el algoritmo de similitud del coseno por su sencillez y baja demanda de recursos computacionales.

Sin embargo no se puede evaluar todos los registros para hallar la recomendacion a un titulo en concreto, por eso antes de aplicar el algoritmo hago una consulta para saber a que genero pertenece la pelicula, luego hago la consulta con todas las peliculas de ese genero con un limite de 4000 registros.

Para el desarrollo de la matriz de similitud empleo las columnas 'title', 'overview' , 'tagline', 'actors' y 'director'
