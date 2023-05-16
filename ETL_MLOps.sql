DROP DATABASE pi_mlops;
CREATE DATABASE IF NOT EXISTS pi_mlops;
USE pi_mlops;

/*Importacion de la tabla*/
DROP TABLE IF EXISTS `movies`;
CREATE TABLE IF NOT EXISTS `movies` (
  `adult` TEXT, -- Se elimina
  `belongs_to_collection` TEXT,
  `budget` FLOAT,
  `genres` TEXT,
  `homepage` TEXT, -- Se elimina
  `id` INTEGER,
  `imdb_id` TEXT, -- Se elimina
  `original_language` TEXT,
  `original_title` TEXT, -- Se elimina
  `overview` TEXT,
  `popularity` FLOAT,
  `poster_path` TEXT, -- Se elimina
  `production_companies` TEXT,
  `production_countries` TEXT,
  `release_date` TEXT,
  `revenue` FLOAT,
  `runtime` VARCHAR(100), -- DEFAULT 'NaN',
  `spoken_languages` TEXT,
  `status` VARCHAR(250), -- DEFAULT 'NaN',
  `tagline` TEXT,
  `title` VARCHAR(250), -- DEFAULT 'NaN',
  `video` TEXT, -- Se elimina
  `vote_average` FLOAT,
  `vote_count` FLOAT -- Se elimina
) ENGINE = InnoDB;


LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\movies_dataset.csv' -- LOAD DATA LOCAL INFILE para servidor en nube
INTO TABLE movies
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;


/* ================= Transformaciones =================================*/
-- ============== Se elimina las columnas que no son utilizadas: video, imdb_id, adult, original_title, vote_count, poster_path, homepage ========

ALTER TABLE `movies`
DROP `video`;

ALTER TABLE `movies`
DROP `imdb_id`;

ALTER TABLE `movies`
DROP `adult`;

ALTER TABLE `movies`
DROP `original_title`;

ALTER TABLE `movies`
DROP `vote_count`;

ALTER TABLE `movies`
DROP `poster_path`;

ALTER TABLE `movies`
DROP `homepage`;

/* ====== Se eliminan los registros con valores nulos en el campo release_date ================= */
DELETE FROM `movies` 
WHERE `release_date` = '' OR `release_date` = '0';

/* ===== De haber fechas, deberan tener el formato AAAA-mm-dd ====== */
ALTER TABLE `movies` MODIFY `release_date` DATE;
UPDATE `movies` SET `release_date` = STR_TO_DATE(release_date, '%Y-%m-%d');

/* ======= Se crea la culumna `release_year` a donde se extrae la fecha de extreno ============= */
ALTER TABLE `movies`
ADD COLUMN `release_year` INT AFTER `release_date`;

UPDATE `movies`
SET `release_year` = YEAR(release_date);

/* ===== Los valores nulos de los campos `revenue` y `budget` deben ser rellenados por el numero 0 ============== */
UPDATE `movies`
SET `budget` = 0
WHERE `budget` IS NULL;


UPDATE `movies`
SET `revenue` = 0
WHERE `revenue` IS NULL;

/* ===== Crear la columna con el retorno de la inversion `return` a partir de los campos `revenue`/`budget` ========= */ 
ALTER TABLE `movies` ADD COLUMN `return` FLOAT;

UPDATE `movies` 
SET `return` = CASE WHEN `budget` = 0 THEN 0 ELSE `revenue` / `budget` END;

/* DESARROLLO DE LAS CONSULTAS PARA HACER LAS FUNCIONES PARA LA API */
-- 1.=== Se ingresa el mes y la funcion retorna la cantidad de peliculas que se estrenaron ese mes =======
-- La consulta busca sobre la columna 'release_date' el mes del anno segun su numero ordinal:
SELECT COUNT(*) FROM movies WHERE MONTH(release_date) = 2; -- 2 = febrero

-- 2.=== Se ingresa el dia y la funcion retrona la cantidad de peliculas que se estrenaron ese dia
-- La consulta busca sobre la columna 'release_date' las coincidencias con el dia de la semana
SELECT COUNT(*) FROM movies WHERE DAYNAME(release_date) = 'sunday'; 

-- 3.=== Se ingresa la franquicia, y se retorna la cantidad de peliculas, ganancia total y promedio ====
UPDATE movies -- Para evitar que /nan de un resultado por todas las peliculas que no pertenecen a una franquicia
SET belongs_to_collection = IF(belongs_to_collection='nan', '{}', belongs_to_collection);

SELECT COUNT(*) AS num_rows, SUM(revenue) AS total_revenue
FROM movies
WHERE belongs_to_collection LIKE '%Bad Boys Collection%';


-- 4. ===== Ingresa el pais, como respuesta da el numero de peliculas producidas ahi ====

SELECT COUNT(*) AS total_rows
FROM movies
WHERE production_countries LIKE '%United States of America%';


-- 5.==== Se ingresa productora, la funcion retorna la ganancia total y la cantidad de peliculas que se produjeron

SELECT COUNT(*) AS total_rows, SUM(revenue) AS total_revenue
FROM movies
WHERE production_companies LIKE '%BBC Films%';


-- 6.=== Se ingresa la pelicula, retorna la inversion, la ganancia, el retorno y el anho que se lanzo ===

SELECT `budget`, `revenue`, `return`, `release_year`
FROM movies
WHERE title LIKE 'Toy Story';

-- ===========

SELECT *
FROM movies
WHERE tagline IS NULL OR tagline = '';

SELECT *
FROM movies
WHERE tagline IS NULL OR overview = '';

SELECT *
FROM movies
WHERE tagline IS NULL OR title = '';

UPDATE movies
SET tagline = title
WHERE tagline IS NULL OR tagline = '';

UPDATE movies
SET overview = title
WHERE overview IS NULL OR overview = '';

SELECT title, tagline, overview
FROM movies;
