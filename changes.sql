ALTER TABLE `agent_stats`.`stats` 
ADD COLUMN `lifetime_ap` BIGINT(20) UNSIGNED NULL DEFAULT NULL AFTER `cassandra-neutralizer`,
ADD COLUMN `recursions` BIGINT(20) UNSIGNED NULL AFTER `lifetime_ap`;


