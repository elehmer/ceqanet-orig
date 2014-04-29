--To replace the location table information, run the next two queries:

--update the locations table
INSERT INTO ceqanet_locations (doc_pk,geom)
SELECT doc_pk,ST_Force_Collection(ST_SetSRID(ST_Point(CAST(coord[1] AS numeric),CAST(coord[2] AS numeric)),4326)) as geom
FROM
(SELECT doc_pk,doc_map_link,regexp_matches(doc_map_link,'(.[0-9]{3}.[0-9]+)&lat=([0-9]{2}.[0-9]+)') as coord
FROM ceqanet_latlongs
) as a

--Generates the points for the big map 4/8/2014
CREATE OR REPLACE VIEW doc_location_points AS
SELECT b.id, b.doc_pk, b.geom::geometry(Point,4326) AS geom, b.geomtype
FROM
(SELECT * from
(SELECT ceqanet_locations.id, ceqanet_locations.doc_pk, (st_dump(ceqanet_locations.geom)).geom AS geom, 
ST_GeometryType(geom), ST_GeometryType((st_dump(ceqanet_locations.geom)).geom) as geomtype
FROM ceqanet_locations) as a
where geomtype = 'ST_Point') as b







--Alex's notes from earlier

--Extract the coordinates
SELECT doc_pk,coord[1],coord[2] 
FROM
(SELECT doc_pk,doc_map_link,regexp_matches(doc_map_link,'(.[0-9]{3}.[0-9]+)&lat=([0-9]{2}.[0-9]+)') as coord
FROM ceqanet_latlongs
LIMIT 10
) as a

--Working
SELECT doc_lat_deg, doc_lat_min, doc_lat_sec, doc_long_deg,doc_long_min, doc_long_sec FROM ceqanet_documents
WHERE char_length(trim(doc_lat_deg)) > 0
LIMIT 5;


SELECT COUNT(doc_pk) FROM ceqanet_documents WHERE char_length(trim(doc_lat_deg)) > 0 ;

SELECT a.doc_lat_deg, a.doc_lat_min, a.doc_lat_sec, a.doc_long_deg,a.doc_long_min, a.doc_long_sec
FROM
(
SELECT doc_lat_deg, doc_lat_min, doc_lat_sec, doc_long_deg,doc_long_min, doc_long_sec 
FROM ceqanet_documents
WHERE char_length(trim(doc_lat_deg)) > 0
) as a


SELECT a.doc_lat_deg, a.doc_lat_min, a.doc_lat_sec, a.doc_long_deg,a.doc_long_min, a.doc_long_sec
FROM
(
SELECT trim(doc_lat_deg) as doc_lat_deg, trim(doc_lat_min) as doc_lat_min, trim(doc_lat_sec) as doc_lat_sec, trim(doc_long_deg) as doc_long_deg, trim(doc_long_min) as doc_long_min, trim(doc_long_sec) as doc_long_sec 
FROM ceqanet_documents
WHERE char_length(trim(doc_lat_deg)) > 0
) as a


SELECT CAST(a.doc_lat_deg AS numeric),CAST(a.doc_lat_min AS numeric), CAST(a.doc_lat_sec AS numeric), CAST(a.doc_long_deg AS numeric),CAST(a.doc_long_min AS numeric), CAST(a.doc_long_sec AS numeric)
FROM
(
SELECT trim(doc_lat_deg) as doc_lat_deg, trim(doc_lat_min) as doc_lat_min, trim(doc_lat_sec) as doc_lat_sec, trim(doc_long_deg) as doc_long_deg, trim(doc_long_min) as doc_long_min, trim(doc_long_sec) as doc_long_sec 
FROM ceqanet_documents
WHERE char_length(trim(doc_lat_deg)) > 0 OR char_length(trim(doc_lat_min)) > 0 OR char_length(trim(doc_lat_sec)) > 0 OR char_length(trim(doc_long_deg)) > 0 OR char_length(trim(doc_lat_min)) > 0 OR char_length(trim(doc_long_sec)) > 0
) as a


--------
-- Filtering geometries
SELECT id,doc_pk,((ST_dump(geom)).geom) as geom FROM ceqanet_locations LIMIT 5;

--Select Points
SELECT id,doc_pk,ST_AsGeoJson(geom) 
FROM (
	SELECT id,doc_pk,((ST_dump(geom)).geom) as geom FROM ceqanet_locations LIMIT 5
) as a
WHERE ST_GeometryType(geom) ='ST_Point';

--A view of points 1000
Drop VIEW doc_location_points1000;
CREATE VIEW doc_location_points1000 AS
SELECT id,doc_pk,geom::geometry(Point,4326) as geom 
FROM (
	SELECT id,doc_pk,((ST_dump(geom)).geom) as geom FROM ceqanet_locations LIMIT 1000
) as a
WHERE ST_GeometryType(geom) ='ST_Point';

--A view of all points, how make gid unique?
Drop VIEW doc_location_points;
CREATE VIEW doc_location_points AS
SELECT id,doc_pk,geom::geometry(Point,4326) as geom 
FROM (
	SELECT id,doc_pk,((ST_dump(geom)).geom) as geom FROM ceqanet_locations
) as a
WHERE ST_GeometryType(geom) ='ST_Point';



--Tilemill
--host=localhost port=5483 user=django password=PegnafGiatsyeGha dbname=ceqanet
