/* DESARROLLO DE LAS CONSULTAS PARA HACER LAS FUNCIONES PARA LA API */
-- 1.=== Se ingresa un mes en idioma espanol. Debe devolver la cantidad de peliculas que se estrenaron ese mes =======
-- La consulta busca sobre la columna 'release_date' el mes del anno segun su numero ordinal:
SELECT COUNT(*) FROM movies WHERE MONTH(release_date) = 2; -- 2 = febrero

-- 2.=== Se ingresa el dia en idioma espanol. Debe devolver la cantidad de peliculas que fueron estrenadas ese dia
-- La consulta busca sobre la columna 'release_date' las coincidencias con el dia de la semana
SELECT COUNT(*) FROM movies WHERE DAYNAME(release_date) = 'sunday';

-- 3.=== Se ingresa el titulo de una filmacion, retorna titulo, anho de estreno y el score ====

SELECT `release_year`, `popularity`
FROM `movies`
WHERE `title` = 'Jumanji';

-- 4. ===== Se ingresa el titulo de una filmacion esperando como respuesta el titulo, la cantidad de votos y el promedio de votaciones ====

SELECT `vote_count`, `vote_average`
FROM `movies`
WHERE `title` = 'Jumanji';

SELECT *
FROM movies
WHERE `title` LIKE '%estrategia del caracol%';

-- 5.==== Se ingresa actor, la funcion retorna la ganancia total y la cantidad de peliculas donde actuo ====

-- Replace 'Tom Hanks' with the actor's name you want to search for
SELECT SUM(`return`) AS retorno, COUNT(*) AS number_of_movies
FROM movies
WHERE actors LIKE '%Robin Williams%';



-- 6.=== Se ingresa director, retorna la ganancia total, y cada pelicula que dirige ===
	-- == con nombre, anho de lanzamiento, retorno, costo y ganancia
    
SELECT
    director,
    SUM(`return`) AS total_return,
    GROUP_CONCAT(CONCAT(title, ' (', release_year, ') - Budget: ', budget, ', Revenue: ', revenue, ', Return: ', `return`) SEPARATOR '; ') AS movie_info
FROM movies
WHERE director = 'Sergio Cabrera'
GROUP BY director;

SELECT SUM(`return`) AS total_money
FROM movies
WHERE director = 'Steven Spielberg';

SELECT title, release_year, budget, revenue, `return`
FROM movies
WHERE director LIKE '%Steven Spielberg%';

-- ===========