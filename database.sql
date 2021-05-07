CREATE SCHEMA safeskiing;

CREATE TABLE stations ( 
	id                   int  NOT NULL  AUTO_INCREMENT  PRIMARY KEY,
	name                 varchar(100)  NOT NULL    ,
	warning_threshold    int  NOT NULL    ,
	danger_threshold     int  NOT NULL    
 ) engine=InnoDB;

CREATE TABLE stations_history ( 
	station_id           int  NOT NULL    ,
	instant              timestamp  NOT NULL    ,
	total_people         int  NOT NULL    ,
	CONSTRAINT pk_stations_history_station_id PRIMARY KEY ( station_id, instant )
 ) engine=InnoDB;

CREATE TABLE lastupdate ( 
	uuid                 varchar(32)  NOT NULL    PRIMARY KEY,
	last_battery         int      ,
	last_update          timestamp      ,
	last_position        int      ,
	last_position_change timestamp      ,
	total_people         int      
 ) engine=InnoDB;

CREATE INDEX fk_lastupdate_stations ON lastupdate ( last_position );

CREATE TABLE skiipass ( 
	uuid                 varchar(32)  NOT NULL    ,
	departure_time       timestamp  NOT NULL    ,
	arrival_time         timestamp      ,
	station_id           int      ,
	total_people         int      ,
	CONSTRAINT idx_skiipass PRIMARY KEY ( uuid, departure_time )
 ) engine=InnoDB;

CREATE INDEX fk_skiipass_stations ON skiipass ( station_id );

ALTER TABLE lastupdate ADD CONSTRAINT fk_lastupdate_stations FOREIGN KEY ( last_position ) REFERENCES stations( id ) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE skiipass ADD CONSTRAINT fk_skiipass_stations FOREIGN KEY ( station_id ) REFERENCES stations( id ) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE stations_history ADD CONSTRAINT fk_stations_history_stations FOREIGN KEY ( station_id ) REFERENCES stations( id ) ON DELETE NO ACTION ON UPDATE NO ACTION;

