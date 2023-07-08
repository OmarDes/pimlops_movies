/* DESARROLLO DE LAS CONSULTAS PARA HACER LAS FUNCIONES PARA LA API */
-- 1.=== Se ingresa un idioma, devuelve la cantidad de peliculas producidas en ese idioma =======
-- La consulta busca sobre la columna 'original_language' el codigo de idioma:
SELECT COUNT(*) FROM movies WHERE original_language = 'hi'; -- 

-- 2.=== Se ingresa el titulo de una pelicula, retorna duracion y anho de estreno ====

SELECT `runtime` , `release_year`
FROM `movies`
WHERE `title` = 'Toy Story 2';

-- 3.=== Se ingresa franquicia. Debe devolver la cantidad de peliculas, ganancia total y promedio
-- 
SELECT COUNT(*) AS num_rows, SUM(revenue) AS total_revenue
FROM movies
WHERE belongs_to_collection LIKE '%Bad Boys Collection%';


-- 4. ===== Ingresa el pais, como respuesta da el numero de peliculas producidas ahi ====

SELECT COUNT(*) AS total_rows
FROM movies
WHERE production_countries LIKE '%Colombia%';

-- 5.==== Se ingresa productora, la funcion retorna la ganancia total y la cantidad de peliculas que se produjeron

SELECT COUNT(*) AS total_peliculas, SUM(revenue) AS total_revenue
FROM movies
WHERE production_companies LIKE '%BBC Films%';


-- 6.=== Se ingresa director, retorna la ganancia total, y cada pelicula que dirige ===
	-- == con fecha de lanzamiento, retorno, costo y ganancia
    
SELECT
    director,
    SUM(`return`) AS total_return,
    GROUP_CONCAT(CONCAT(title, ' (', release_year, ') - Budget: ', budget, ', Revenue: ', revenue, ', Return: ', `return`) SEPARATOR '; ') AS list_movies
FROM movies
WHERE director = 'Steven Spielberg'
GROUP BY director;

SELECT SUM(`return`) AS total_money
FROM movies
WHERE director = 'Steven Spielberg';

SELECT title, release_year, budget, revenue, `return`
FROM movies
WHERE director LIKE '%Steven Spielberg%';

-- ===========