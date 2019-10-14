CREATE TABLE `clients` (
  `time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ip` int(10) UNSIGNED NOT NULL,
  `version` int(1) NOT NULL
) ENGINE=MEMORY DEFAULT CHARSET=latin1;
ALTER TABLE `clients`
  ADD UNIQUE KEY `ip` (`ip`),
  ADD KEY `time` (`time`),
  ADD KEY `version` (`version`);
