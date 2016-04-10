DROP TABLE IF EXISTS `stats`;
DROP TABLE IF EXISTS `membership`;
DROP TABLE IF EXISTS `groups`;
DROP TABLE IF EXISTS `agents`;

CREATE TABLE `agents` (
  `idagents` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(16) NOT NULL,
  `faction` varchar(3) DEFAULT NULL,
  `apdiff` bigint(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`idagents`,`name`),
  UNIQUE KEY `idagents_UNIQUE` (`idagents`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=latin1;

CREATE TABLE `groups` (
  `idgroups` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `url` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`idgroups`,`name`),
  UNIQUE KEY `name_UNIQUE` (`name`),
  UNIQUE KEY `idgroups_UNIQUE` (`idgroups`),
  UNIQUE KEY `url_UNIQUE` (`url`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=latin1;
INSERT INTO `groups` VALUES (1,'all',NULL),(2,'smurfs',NULL),(3,'frogs',NULL);

CREATE TABLE `membership` (
  `idagents` int(11) NOT NULL,
  `idgroups` int(11) NOT NULL,
  PRIMARY KEY (`idagents`,`idgroups`),
  KEY `FK_groups_idx` (`idgroups`),
  CONSTRAINT `FK_agents` FOREIGN KEY (`idagents`) REFERENCES `agents` (`idagents`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_groups` FOREIGN KEY (`idgroups`) REFERENCES `groups` (`idgroups`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `stats` (
  `idagents` int(11) NOT NULL,
  `date` date NOT NULL,
  `level` bigint(20) unsigned DEFAULT NULL,
  `ap` bigint(20) unsigned DEFAULT NULL,
  `explorer` bigint(20) unsigned DEFAULT NULL,
  `seer` bigint(20) unsigned DEFAULT NULL,
  `trekker` bigint(20) unsigned DEFAULT NULL,
  `builder` bigint(20) unsigned DEFAULT NULL,
  `connector` bigint(20) unsigned DEFAULT NULL,
  `mind-controller` bigint(20) unsigned DEFAULT NULL,
  `illuminator` bigint(20) unsigned DEFAULT NULL,
  `recharger` bigint(20) unsigned DEFAULT NULL,
  `liberator` bigint(20) unsigned DEFAULT NULL,
  `pioneer` bigint(20) unsigned DEFAULT NULL,
  `engineer` bigint(20) unsigned DEFAULT NULL,
  `purifier` bigint(20) unsigned DEFAULT NULL,
  `guardian` bigint(20) unsigned DEFAULT NULL,
  `specops` bigint(20) unsigned DEFAULT NULL,
  `missionday` bigint(20) unsigned DEFAULT NULL,
  `hacker` bigint(20) unsigned DEFAULT NULL,
  `translator` bigint(20) unsigned DEFAULT NULL,
  `sojourner` bigint(20) unsigned DEFAULT NULL,
  `recruiter` bigint(20) unsigned DEFAULT NULL,
  `collector` bigint(20) unsigned DEFAULT NULL,
  `binder` bigint(20) unsigned DEFAULT NULL,
  `country-master` bigint(20) unsigned DEFAULT NULL,
  `neutralizer` bigint(20) unsigned DEFAULT NULL,
  `disruptor` bigint(20) unsigned DEFAULT NULL,
  `salvator` bigint(20) unsigned DEFAULT NULL,
  `smuggler` bigint(20) unsigned DEFAULT NULL,
  `link-master` bigint(20) unsigned DEFAULT NULL,
  `controller` bigint(20) unsigned DEFAULT NULL,
  `field-master` bigint(20) unsigned DEFAULT NULL,
  `flag` int(1) unsigned DEFAULT NULL,
  `min-ap` bigint(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`idagents`,`date`),
  CONSTRAINT `FK_idagents` FOREIGN KEY (`idagents`) REFERENCES `agents` (`idagents`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DELIMITER $$
CREATE PROCEDURE `FindAgentByName`(IN `agentname` varchar(16))
BEGIN
SELECT
  `agents`.`name`, 
  `stats`.`date`, 
  `stats`.`flag`, 
  `stats`.`min-ap`, 
  `stats`.`ap`,
  `stats`.`level`,
  `stats`.`explorer`,
  `stats`.`seer`,
  `stats`.`trekker`,
  `stats`.`builder`,
  `stats`.`connector`,
  `stats`.`mind-controller`,
  `stats`.`illuminator`,
  `stats`.`recharger`,
  `stats`.`liberator`,
  `stats`.`pioneer`,
  `stats`.`engineer`,
  `stats`.`purifier`,
  `stats`.`guardian`,
  `stats`.`specops`,
  `stats`.`missionday`,
  `stats`.`hacker`,
  `stats`.`translator`,
  `stats`.`sojourner`,
  `stats`.`recruiter`,
  `stats`.`collector`,
  `stats`.`binder`,
  `stats`.`country-master`,
  `stats`.`neutralizer`,
  `stats`.`disruptor`,
  `stats`.`salvator`,
  `stats`.`smuggler`,
  `stats`.`link-master`,
  `stats`.`controller`,
  `stats`.`field-master`
FROM `stats`, `agents`
WHERE `stats`.`idagents` = `agents`.`idagents` AND `agents`.`name` = `agentname`;
END$$
DELIMITER ;
