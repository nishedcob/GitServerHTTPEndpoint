
-- su - postgres -c psql
CREATE USER gitendpointuser WITH PASSWORD 'g1T3Ndp01Nt_$3r';
CREATE DATABASE gitendpointdb WITH OWNER gitendpointuser;

-- su - postgres -c "psql gitendpointdb"
CREATE SCHEMA gitendpointapp AUTHORIZATION gitendpointuser;
ALTER USER gitendpointuser SET SEARCH_PATH TO gitendpointapp;

-- psql gitendpointdb -U gitendpointuser
SELECT current_schema();
