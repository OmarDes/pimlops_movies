DROP DATABASE pi_movies;
CREATE DATABASE IF NOT EXISTS pi_movies;
USE pi_movies;

/* Importacion de la tabla 'movies_dataset.csv' */
DROP TABLE IF EXISTS `movies`;
CREATE TABLE IF NOT EXISTS `movies` (
  `adult` TEXT, -- Se elimina
  `belongs_to_collection` TEXT, -- Se elimina
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
  `production_companies` TEXT, -- Se elimina
  `production_countries` TEXT,	-- Se elimina
  `release_date` TEXT,
  `revenue` FLOAT,
  `runtime` VARCHAR(100), -- Se elimina
  `spoken_languages` TEXT, -- Se elimina
  `status` VARCHAR(250),	-- Se elimina
  `tagline` TEXT,
  `title` VARCHAR(250),
  `video` TEXT, -- Se elimina
  `vote_average` FLOAT,
  `vote_count` FLOAT,
  `actors`	TEXT,
  `director` TEXT,
  `zeros` INT	-- Se elimina
) ENGINE = InnoDB;


LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\movies_dataset.csv' -- LOAD DATA LOCAL INFILE para servidor en nube
INTO TABLE movies
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

/* ================= Transformaciones =================================*/

-- ============== Se elimina las columnas que no son utilizadas: video, imdb_id, adult, original_title, poster_path, homepage ========

ALTER TABLE `movies`
DROP `video`;

ALTER TABLE `movies`
DROP `imdb_id`;

ALTER TABLE `movies`
DROP `adult`;

ALTER TABLE `movies`
DROP `original_title`;

ALTER TABLE `movies`
DROP `poster_path`;

ALTER TABLE `movies`
DROP `homepage`;

-- === Hay otras columna que no se usan en el dataset, y por tanto se eliminan =====

ALTER TABLE `movies`
DROP `belongs_to_collection`;

ALTER TABLE `movies`
DROP `production_companies`;

ALTER TABLE `movies`
DROP `production_countries`;

ALTER TABLE `movies`
DROP `runtime`;

ALTER TABLE `movies`
DROP `spoken_languages`;

ALTER TABLE `movies`
DROP `status`;

ALTER TABLE `movies`
DROP `zeros`;

/* ====== Se eliminan los registros con valores nulos en el campo release_date ================= */
DELETE FROM `movies` 
WHERE `release_date` = '' OR `release_date` = '0';

/* ===== De haber fechas, deberan tener el formato AAAA-mm-dd ====== */
ALTER TABLE `movies` MODIFY `release_date` DATE;
UPDATE `movies` SET `release_date` = STR_TO_DATE(release_date, '%Y-%m-%d');

/* ======= Se crea la culumna `release_year` a donde se extrae el anho de extreno ============= */
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
-- Nota: esos campos no tenian valores nulos

/* ===== Crear la columna con el retorno de la inversion `return` a partir de los campos `revenue`/`budget` ========= */ 
ALTER TABLE `movies` ADD COLUMN `return` FLOAT;

UPDATE `movies` 
SET `return` = CASE WHEN `budget` = 0 THEN 0 ELSE `revenue` / `budget` END;

/*Algunos registros estan repetidos en ambos archivos, antes de unificar en una sola tabla 
	se eliminan esos repetidos.*/
    
SELECT id, COUNT(*) AS count
FROM movies
GROUP BY id
HAVING COUNT(*) > 1
ORDER BY count DESC;


SELECT *
FROM movies
WHERE id = 132641;
-- Algunos registros tienen todos sus campos repetidos, mientras que otros apenas difieren en el campo 'popularity'

-- == Eliminar duplicados para 'movies' de las filas completamente identicas== 
-- create a temporary table with distinct rows
DROP TABLE IF EXISTS `tmp`;
CREATE TEMPORARY TABLE tmp AS
SELECT DISTINCT * FROM movies;

-- truncate the original table
TRUNCATE movies;

-- insert the rows from the temporary table
INSERT INTO movies
SELECT * FROM tmp;

-- == Aun persisten registros duplicados, pero que difieren valores en 'popularity' ==
-- == para esas saco el promedio entre los diferentes valores en 'popularity' ==
-- == y dejo una copia de ese registro con ese nuevo valor en 'popularity'    == 

-- Create a temporary table with all the columns from movies
DROP TABLE IF EXISTS `temp_movies`;
CREATE TEMPORARY TABLE `temp_movies` AS
SELECT * FROM movies;


-- Update the popularity column with the average of duplicate rows
UPDATE temp_movies t
SET popularity = (SELECT AVG(popularity) FROM movies m WHERE m.id = t.id)
WHERE id IN (SELECT id FROM movies GROUP BY id HAVING COUNT(*) > 1);

-- Delete the duplicate rows from the original table
DELETE FROM movies
WHERE id IN (SELECT id FROM temp_movies);

-- Insert the rows with average popularity from the temporary table
INSERT INTO movies
SELECT * FROM temp_movies;

-- Drop the temporary table
DROP TABLE temp_movies;

-- create a temporary table with distinct rows
DROP TABLE IF EXISTS `tmp`;
CREATE TEMPORARY TABLE tmp AS
SELECT DISTINCT * FROM movies;

-- truncate the original table
TRUNCATE movies;

-- insert the rows from the temporary table
INSERT INTO movies
SELECT * FROM tmp;

-- Aun persiste un registro duplicado, por tener la columna 'vote_count' (143 y 144)
SELECT *
FROM movies
WHERE id = 10991;

-- Elimino uno de los registros
DELETE FROM movies
WHERE id = 10991 AND vote_count = 144;

-- Aun persiste un registro duplicado, por tener la columna 'vote_count' (89 y 90)
SELECT *
FROM movies
WHERE id = 15028;

-- Elimino uno de los registros
DELETE FROM movies
WHERE id = 15028 AND vote_count = 90;

SELECT *
FROM movies
WHERE id = 99080;

-- Elimino uno de los registros
DELETE FROM movies
WHERE id = 99080 AND director = 'Varick Frissell, George Melford';
