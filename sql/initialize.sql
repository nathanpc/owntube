-- initialize.sql
-- Initializes the database creating the basic tables for our project.
--
-- Author: Nathan Campos <nathan@innoveworkshop.com>

CREATE DATABASE IF NOT EXISTS owntube
	CHARACTER SET utf8mb4
	COLLATE utf8mb4_unicode_ci;

USE owntube;

CREATE TABLE channels(
	cid			VARCHAR(30)		CHARACTER SET 'ascii' COLLATE 'ascii_bin' NOT NULL PRIMARY KEY,
	name		VARCHAR(100)	NOT NULL UNIQUE,
	description	TEXT			NULL
);

CREATE TABLE videos(
	vid				VARCHAR(11)		CHARACTER SET 'ascii' COLLATE 'ascii_bin' NOT NULL PRIMARY KEY,
	channel_cid		VARCHAR(30)		CHARACTER SET 'ascii' COLLATE 'ascii_bin' NOT NULL,
	title			VARCHAR(255)	NOT NULL,
	description		TEXT			NULL,
	published_date	DATETIME		NOT NULL,
	duration		INT				NULL,
	width			SMALLINT		NULL,
	height			SMALLINT		NULL,
	fps				TINYINT			NULL,
	chapters		JSON			NULL,

	INDEX (title),
	FULLTEXT KEY (description),

	FOREIGN KEY (channel_cid) REFERENCES channels (cid)
		ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE downloaded_videos(
	id			BIGINT			NOT NULL AUTO_INCREMENT PRIMARY KEY,
	vid			VARCHAR(11)		CHARACTER SET 'ascii' COLLATE 'ascii_bin' NOT NULL,
	width		SMALLINT		NOT NULL,
	height		SMALLINT		NOT NULL,
	fps			TINYINT			NOT NULL,
	filesize	BIGINT			NULL,
	extension	VARCHAR(4)		NOT NULL,

	FOREIGN KEY (vid) REFERENCES videos (vid)
		ON DELETE CASCADE ON UPDATE CASCADE
);
