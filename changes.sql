USE `agent_stats`;

ALTER TABLE `agent_stats`.`stats`
ADD COLUMN `operation_chronos` BIGINT(20) UNSIGNED NULL DEFAULT NULL AFTER `overclocker`;

DROP procedure IF EXISTS `FindAgentByName`;

DELIMITER $$
USE `agent_stats`$$
CREATE DEFINER=`user`@`localhost` PROCEDURE `FindAgentByName`(IN `agentname` varchar(16))
BEGIN
SELECT
  `agents`.`name`,
  `stats`.`date`,
  `stats`.`flag`,
  `stats`.`min-ap`,
  `stats`.`lifetime_ap`,
  `stats`.`recursions`,
  `stats`.`ap`,
  `stats`.`level`,
  `stats`.`explorer`,
  `stats`.`discoverer`,
  `stats`.`seer`,
  `stats`.`recon`,
  `stats`.`scout`,
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
  `stats`.`nl-1331-meetups`,
  `stats`.`cassandra-neutralizer`,
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
  `stats`.`field-master`,
  `stats`.`magnusbuilder`,
  `stats`.`prime_challenge`,
  `stats`.`stealth_ops`,
  `stats`.`opr_live`,
  `stats`.`ocf`,
  `stats`.`intel_ops`,
  `stats`.`urban_ops`,
  `stats`.`ifs`,
  `stats`.`dark_xm_threat`,
  `stats`.`myriad_hack`,
  `stats`.`aurora_glyph`,
  `stats`.`umbra_deploy`,
  `stats`.`didact_field`,
  `stats`.`drone_explorer`,
  `stats`.`drone_distance`,
  `stats`.`drone_recalls`,
  `stats`.`drone_sender`,
  `stats`.`maverick`,
  `stats`.`scout_controller`,
  `stats`.`crafter`,
  `stats`.`bb_combatant`,
  `stats`.`red-disruptor`,
  `stats`.`red-purifier`,
  `stats`.`red-neutralizer`,
  `stats`.`reclaimer`,
  `stats`.`hack_the_world202104`,
  `stats`.`epoch`,
  `stats`.`matryoshka_links`,
  `stats`.`operation_sentinel`,
  `stats`.`second_sunday`,
  `stats`.`eos_imprint`,
  `stats`.`overclocker`,
  `stats`.`operation_chronos`
FROM `stats`, `agents`
WHERE `stats`.`idagents` = `agents`.`idagents` AND `agents`.`name` = `agentname`;
END$$

DELIMITER ;