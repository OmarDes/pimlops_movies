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


LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\movies_dataset.csv'
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
SET GLOBAL log_bin_trust_function_creators =1;

-- === Se ingresa el mes y la funcion retorna la cantidad de peliculas que se estrenaron ese mes =======
-- Function that takes a month as a parameter and returns the number of movies released in that month:
DELIMITER //
CREATE FUNCTION count_movies_by_month(month INT) RETURNS INT
BEGIN
    DECLARE num_movies INT;
    SELECT COUNT(*) INTO num_movies FROM movies WHERE MONTH(release_date) = month;
    RETURN num_movies;
END //
DELIMITER ;

SELECT count_movies_by_month(2); -- returns the number of movies released in January



-- === Se ingresa el dia y la funcion retrona la cantidad de peliculas que se estrenaron ese dia
DELIMITER //
CREATE FUNCTION count_movies_by_day_of_week(day VARCHAR(10)) RETURNS INT
BEGIN
    DECLARE count INT;
    SELECT COUNT(*) INTO count FROM movies WHERE DAYNAME(release_date) = day;
    RETURN count;
END //
DELIMITER ;

SELECT count_movies_by_day_of_week('tuesday');


-- ===  ====
UPDATE movies
SET belongs_to_collection = IF(belongs_to_collection='', '{}', belongs_to_collection);

UPDATE `movies` 
SET `belongs_to_collection` = REPLACE(`belongs_to_collection`, 'None', '"None"') 
WHERE `belongs_to_collection` LIKE '%None%';


UPDATE `movies`
SET `belongs_to_collection` = REPLACE(`belongs_to_collection`, "'", "\"");

/* UPDATE `movies`
SET `belongs_to_collection` = JSON_SET(`belongs_to_collection`, '$.name', REPLACE(JSON_EXTRACT(`belongs_to_collection`, '$.name'), "'", "\""))
WHERE `belongs_to_collection` LIKE '%''%'; */


/* UPDATE `movies`
SET `belongs_to_collection` = JSON_REPLACE(`belongs_to_collection`, '$**', REPLACE(JSON_EXTRACT(`belongs_to_collection`, '$**'), "'", "\""))
WHERE `belongs_to_collection` LIKE '%''%'; */

UPDATE `movies`
SET `belongs_to_collection` = REPLACE(`belongs_to_collection`, "'", "''"); 

UPDATE `movies`  -- FUNCIONA!!!!!!!!!
SET `belongs_to_collection` = REPLACE(`belongs_to_collection`, '"id":', 'id:')
  , `belongs_to_collection` = REPLACE(`belongs_to_collection`, '"name":', 'name:')
  , `belongs_to_collection` = REPLACE(`belongs_to_collection`, '"poster_path":', 'poster_path:')
  , `belongs_to_collection` = REPLACE(`belongs_to_collection`, '"backdrop_path":', 'backdrop_path:')
  , `belongs_to_collection` = REPLACE(`belongs_to_collection`, "'", "\"");

UPDATE `movies`
SET `belongs_to_collection` = JSON_REPLACE(`belongs_to_collection`, REPLACE(`belongs_to_collection`, '\'', '\"'), REPLACE(`belongs_to_collection`, '\'', '\"'))
WHERE NOT JSON_VALID(`belongs_to_collection`);




SELECT * FROM `movies`
WHERE JSON_VALID(belongs_to_collection) = 0;

ALTER TABLE `movies` MODIFY `belongs_to_collection` JSON;



-- ===== Ingresa el pais, como respuesta da el numero de peliculas producidas ahi ====
UPDATE `movies`
SET `production_countries` = REPLACE(`production_countries`, "'", "\"");

UPDATE `movies`
SET `production_countries` = REPLACE(production_countries, 'Lao People"s', 'Lao People\'s');

UPDATE `movies`
SET `production_countries` = REPLACE(production_countries, 'Cote D"Ivoire', 'Cote D\'Ivoire');

SELECT * FROM `movies`
WHERE JSON_VALID(production_countries) = 0;

ALTER TABLE `movies` MODIFY `production_countries` JSON;

DELIMITER //
CREATE FUNCTION count_movies_by_country(country_name VARCHAR(100))
RETURNS INT
BEGIN
  DECLARE count INT;
  SELECT COUNT(*) INTO count
  FROM movies
  WHERE JSON_SEARCH(production_countries, 'one', country_name, NULL, '$[*]."name"') IS NOT NULL;
  RETURN count;
END //
DELIMITER ;

SELECT count_movies_by_country('Chile');

-- ==== Se ingresa productora, la funcion retorna la ganancia total y la cantidad de peliculas que se produjeron
UPDATE `movies`
SET `production_companies` = REPLACE(`production_companies`, "'", "\"");

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Club d"Investissement Média', 'Club d\'Investissement Média');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'D"Pelicula', 'D\'Pelicula');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Workin" Man Films', 'Workin\' Man Films');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Butcher"s Run Films', 'Butcher\'s Run Films');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Les Films de l"Astre', 'Les Films de l\'Astre');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Hell"s Kitchen Films', 'Hell\'s Kitchen Films');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Po" Boy Productions', 'Po\' Boy Productions');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Fonds Eurimages du Conseil de l"Europe', 'Fonds Eurimages du Conseil de l\'Europe');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Centre du Cinéma et de l"Audiovisuel de la Fédération Wallonie-Bruxelles', 'Centre du Cinéma et de l\'Audiovisuel de la Fédération Wallonie-Bruxelles');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Sol"oeil Films', 'Sol\'oeil Films');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Loew"s', 'Loew\'s');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Conseil Général de l"Aveyron', 'Conseil Général de l\'Aveyron');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Zespól Filmowy "Tor"', 'Zespól Filmowy \'Tor\'');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Eric"s Boy', 'Eric\'s Boy');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Giv"en Films', 'Giv\'en Films');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Mel"s Cite du Cinema', 'Mel\'s Cite du Cinema');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Butcher"s Run Productions', 'Butcher\'s Run Productions');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Fonds de télévision et de câblodistribution pour la production d"émissions canadiennes', 'Fonds de télévision et de câblodistribution pour la production d\'émissions canadiennes');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'D"Antoni Productions', 'D\'Antoni Productions');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Val D"Oro Entertainment', 'Val D\'Oro Entertainment');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Institut National de l"Audiovisuel (INA)', 'Institut National de l\'Audiovisuel (INA)');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Win"s Entertainment Ltd.', 'Win\'s Entertainment Ltd.');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Cinema "84/Greenberg Brothers Partnership', 'Cinema \'84/Greenberg Brothers Partnership');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Children"s Television Workshop', 'Children\'s Television Workshop');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'La Générale d"Images', 'La Générale d\'Images');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Xi"an Film Studio', 'Xi\'an Film Studio');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Pikachu Project "98', 'Pikachu Project \'98');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Réalisation d"Art Cinématographique', 'Réalisation d\'Art Cinématographique');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Donners" Company', 'Donners\' Company');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Hawk"s Nest Productions', 'Hawk\'s Nest Productions');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Greaser"s Palace Ltd.', 'Greaser\'s Palace Ltd.');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Double "A" Pictures', 'Double \'A\' Pictures');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Say It Isn"t So Productions', 'Say It Isn\'t So Productions');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Kids" WB', 'Kids\' WB');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Les Films de L"Observatoire', 'Les Films de L\'Observatoire');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'D"Artagnan Productions Limited', 'D\'Artagnan Productions Limited');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Jack"s Camp', 'Jack\'s Camp');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Man"s Films', 'Man\'s Films');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'The Centre du Cinema et de l"Audiovisuel de la Communauté Française de Belgique', 'The Centre du Cinema et de l\'Audiovisuel de la Communauté Française de Belgique');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Boyd"s Company', 'Boyd\'s Company');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'Kwan"s Creation Workshop', 'Kwan\'s Creation Workshop');

UPDATE `movies`
SET `production_companies` = REPLACE(production_companies, 'A.N.P.A. (Agence Nationale de Promotion de l"Audiovisuel)', 'A.N.P.A. (Agence Nationale de Promotion de l\'Audiovisuel)');

SELECT * FROM `movies`
WHERE JSON_VALID(production_companies) = 0;



-- Drop the temporary table
DROP TEMPORARY TABLE temp_avg_ratings;

DROP TABLE IF EXISTS `avg_ratings`;
CREATE TABLE IF NOT EXISTS `avg_ratings` (
  	`movieID`		VARCHAR(8),
  	`avg_rating`		DECIMAL(7,5)
);

INSERT INTO `avg_ratings`
SELECT * FROM `temp_avg_ratings`;

SELECT * FROM avg_ratings
WHERE avg_rating = 3.58;

SELECT * FROM avg_ratings
WHERE movieId = 'ns2072';

SELECT * FROM show_streaming
WHERE id = 'ns2072';

UPDATE avg_ratings
SET movieId = REPLACE(movieId, '\r', '');

-- ---------------------------------------------------------------------------------------

-- -----------------------------------------------------------------------------------------

/* Desarrollo consultas API */
-- 1. Consulta Pelicula con mayor duracion segun anho, plataforma y tipo de duracion
SELECT `title`
FROM `show_streaming`
WHERE type = 'movie' -- Only movies
AND release_year = '2018' -- Release year parameter
AND (id LIKE 'a%') -- Streaming service platform parameter id LIKE 'a%' OR id LIKE 'd%' OR id LIKE 'h%' OR id LIKE 'n%'
AND duration_type = 'min' -- season
ORDER BY duration_int DESC -- Sort by duration_int in descending order
LIMIT 1; -- Limit to one result (the movie with the longest duration)

SET GLOBAL log_bin_trust_function_creators =1;

DELIMITER //
CREATE FUNCTION get_longest_movie_duration(
  p_release_year INT,
  p_streaming_service CHAR(1),
  p_duration_type VARCHAR(20)
)
RETURNS VARCHAR(150)
BEGIN
  DECLARE v_title VARCHAR(150);
  
  SELECT title INTO v_title
  FROM show_streaming
  WHERE type = 'movie'
    AND release_year = p_release_year
    AND id LIKE CONCAT(p_streaming_service, '%')
    AND duration_type = p_duration_type
  ORDER BY duration_int DESC
  LIMIT 1;
  
  RETURN v_title;
END //
DELIMITER ;

SELECT get_longest_movie_duration(2018, 'a', 'min');


-- 2. Cantidad de peliculas(solo estas) segun plataforma, con un puntaje mayor a XX
DELIMITER //
CREATE FUNCTION count_movies_above_score(score DECIMAL(7,5), platform CHAR(1), release_year INT)
RETURNS INT
BEGIN
    DECLARE num_movies INT;
    
    SELECT COUNT(*) INTO num_movies
    FROM show_streaming
    WHERE type = 'movie'
    AND avg_score > score
    AND (
        (LEFT(id, 1) = platform AND release_year = release_year)
    );
    
    RETURN num_movies;
END;
//
DELIMITER ;

SELECT count_movies_above_score(3.6, 'n', 2021); -- Returns the number of movies with score above 3.5 for Amazon with release year = 2021

-- 3. Cantidad de peliculas segun plataforma
DELIMITER //
CREATE FUNCTION count_movies_platform(platform CHAR(1))
RETURNS INT
BEGIN
    DECLARE num_movies INT;
    
    SELECT COUNT(*) INTO num_movies
    FROM show_streaming
    WHERE type = 'movie'
    AND LEFT(id, 1) = platform;
    
    RETURN num_movies;
END;
//
DELIMITER ;

SELECT count_movies_platform('d');

-- 4. Consultar cual es en actor mas repetido segun anho y plataforma

UPDATE show_streaming
SET cast = ''
WHERE cast = 'NULL';


DROP FUNCTION IF EXISTS `find_most_repeated_name`;

DELIMITER //
CREATE FUNCTION find_most_repeated_name(p_release_year INT, p_platform CHAR(1))
RETURNS VARCHAR(255)
BEGIN
  DECLARE v_most_repeated_name VARCHAR(255);
  
  -- Create temporary table to store extracted names
  DROP TEMPORARY TABLE IF EXISTS tmp_names;
  CREATE TEMPORARY TABLE tmp_names (name VARCHAR(255));
  
  -- Insert extracted names into temporary table
  INSERT INTO tmp_names (name)
  SELECT TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(cast, ',', n), ',', -1)) AS name
  FROM show_streaming
  CROSS JOIN
  (
    SELECT 1 + (LENGTH(cast) - LENGTH(REPLACE(cast, ',', ''))) AS n
    FROM show_streaming
  ) AS nums
  WHERE TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(cast, ',', n), ',', -1)) <> ''
    AND release_year = p_release_year
    AND id LIKE CONCAT(p_platform, '%');
  
  -- Find most repeated name
  SELECT name INTO v_most_repeated_name
  FROM tmp_names
  GROUP BY name
  ORDER BY COUNT(*) DESC
  LIMIT 1;
  
  -- Drop temporary table
  DROP TEMPORARY TABLE IF EXISTS tmp_names;
  
  RETURN v_most_repeated_name;
END;
//
DELIMITER ;



SELECT find_most_repeated_name(1936, 'a');

-- 5. Cantidad de contenidos/productos que es publico por anho y por pais. 
SELECT DISTINCT type
FROM show_streaming;

DROP FUNCTION IF EXISTS `get_count_by_release_year_and_country`;

DELIMITER //
CREATE FUNCTION get_count_by_release_year_and_country(p_type VARCHAR(50), p_country VARCHAR(150), p_release_year INT)
RETURNS JSON
BEGIN
  DECLARE v_count INT;
  DECLARE v_result JSON;
  
  -- Get count of movies or TV shows based on type, country, and release year
  IF p_type = 'movie' THEN
    SELECT COUNT(*) INTO v_count
    FROM show_streaming
    WHERE type = 'Movie' AND country = p_country AND release_year = p_release_year;
  ELSEIF p_type = 'tv show' THEN
    SELECT COUNT(*) INTO v_count
    FROM show_streaming
    WHERE type = 'TV Show' AND country = p_country AND release_year = p_release_year;
  ELSE
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid type parameter. Must be either "movie" or "tv show".';
  END IF;
  
  -- Create JSON result
  SET v_result = JSON_OBJECT('type', p_type, 'country', p_country, 'release_year', p_release_year, 'count', v_count);
  
  RETURN v_result;
END;
//
DELIMITER ;

SELECT get_count_by_release_year_and_country('movie', 'france',2020);

-- 6. La cantidad total de contenidos/productos segun el rating de la audiencia

SELECT DISTINCT rating
FROM show_streaming;

DROP FUNCTION IF EXISTS `count_rows_by_rating`;

DELIMITER //
CREATE FUNCTION count_rows_by_rating(p_rating VARCHAR(10))
RETURNS INT
BEGIN
  DECLARE v_count INT;
  
  SELECT COUNT(*) INTO v_count FROM show_streaming WHERE rating = p_rating;
  -- Check if the input rating is 'all'
  /*IF p_rating = 'all' THEN
    SELECT COUNT(*) INTO v_count FROM show_streaming;
  ELSE
    -- Count rows based on the given rating
    SELECT COUNT(*) INTO v_count FROM show_streaming WHERE rating = p_rating;
  END IF; */
  
  RETURN v_count;
END;
//
DELIMITER ;

SELECT count_rows_by_rating('16+');