-- MySQL dump 10.13  Distrib 5.5.44, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: agent_stats
-- ------------------------------------------------------
-- Server version	5.5.44-0ubuntu0.12.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `agents`
--

DROP TABLE IF EXISTS `agents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `agents` (
  `idagents` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(16) NOT NULL,
  `faction` varchar(3) DEFAULT NULL,
  PRIMARY KEY (`idagents`,`name`),
  UNIQUE KEY `idagents_UNIQUE` (`idagents`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=7629 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups` (
  `idgroups` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `url` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`idgroups`,`name`),
  UNIQUE KEY `name_UNIQUE` (`name`),
  UNIQUE KEY `idgroups_UNIQUE` (`idgroups`),
  UNIQUE KEY `url_UNIQUE` (`url`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `membership`
--

DROP TABLE IF EXISTS `membership`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `membership` (
  `idagents` int(11) NOT NULL,
  `idgroups` int(11) NOT NULL,
  PRIMARY KEY (`idagents`,`idgroups`),
  KEY `FK_groups_idx` (`idgroups`),
  CONSTRAINT `FK_agents` FOREIGN KEY (`idagents`) REFERENCES `agents` (`idagents`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_groups` FOREIGN KEY (`idgroups`) REFERENCES `groups` (`idgroups`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stats`
--

DROP TABLE IF EXISTS `stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
  `flag` int(10) unsigned zerofill DEFAULT NULL,
  PRIMARY KEY (`idagents`,`date`),
  CONSTRAINT `FK_idagents` FOREIGN KEY (`idagents`) REFERENCES `agents` (`idagents`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-10-09 13:01:24
