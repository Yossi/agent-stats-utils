ALTER TABLE `agent_stats`.`stats` 
ADD COLUMN `cassandra-neutralizer` BIGINT(20) UNSIGNED NULL DEFAULT NULL COMMENT '' AFTER `nl-1331-meetups`;

