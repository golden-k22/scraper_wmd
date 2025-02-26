-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Erstellungszeit: 23. Feb 2025 um 10:11
-- Server-Version: 10.4.32-MariaDB
-- PHP-Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Datenbank: `scrapelistdb`
--

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `tbl_url_list`
--

CREATE TABLE `tbl_url_list` (
  `id` int(11) NOT NULL,
  `url` text DEFAULT NULL,
  `type` int(11) DEFAULT NULL,
  `type_text` varchar(255) DEFAULT NULL,
  `prod_scrape_time` varchar(255) DEFAULT NULL,
  `stop_count` varchar(255) DEFAULT NULL,
  `item` int(11) DEFAULT NULL,
  `item_text` varchar(255) DEFAULT NULL,
  `products` int(11) DEFAULT NULL,
  `products_text` varchar(255) DEFAULT NULL,
  `inktype` int(11) DEFAULT NULL,
  `inktype_text` varchar(255) DEFAULT NULL,
  `densitytype` int(11) DEFAULT NULL,
  `densitytype_text` varchar(255) DEFAULT NULL,
  `prod_db_time` int(11) DEFAULT NULL,
  `prod_db_time_text` varchar(255) DEFAULT NULL,
  `workday` varchar(255) DEFAULT NULL,
  `coeff` varchar(255) DEFAULT NULL,
  `last_scrape` varchar(255) DEFAULT NULL,
  `last_export` varchar(255) DEFAULT NULL,
  `extra_limit` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=DYNAMIC;

--
-- Daten für Tabelle `tbl_url_list`
--

INSERT INTO `tbl_url_list` (`id`, `url`, `type`, `type_text`, `prod_scrape_time`, `stop_count`, `item`, `item_text`, `products`, `products_text`, `inktype`, `inktype_text`, `densitytype`, `densitytype_text`, `prod_db_time`, `prod_db_time_text`, `workday`, `coeff`, `last_scrape`, `last_export`, `extra_limit`) VALUES
(592, 'https://www.wir-machen-druck.de/flyer-din-lang-105-cm-x-210-cm-topseller-beidseitig-bedruckt.html', 189732, '90g hochwertiger Qualitätsdruck matt', 'STANDARD_PRODUCTION', '100000', 34, 'Postaktuell DIN-L Flyer', 72, 'Flyer & Falzflyer, DIN-L', 102, '2-Seiter, ungefalzt', 145, '90g Bilderdruck, matt', 1, 'Standard', '5', '1', NULL, NULL, 0),
(593, 'https://www.wir-machen-druck.de/flyer-din-lang-105-cm-x-210-cm-topseller-beidseitig-bedruckt.html', 189732, '90g hochwertiger Qualitätsdruck matt', 'STANDARD_PRODUCTION', '100000', 34, 'Postaktuell DIN-L Flyer', 72, 'Flyer & Falzflyer, DIN-L', 102, '2-Seiter, ungefalzt', 146, '90g Bilderdruck, glänzend', 1, 'Standard', '5', '1', NULL, NULL, 0),
(594, 'https://www.wir-machen-druck.de/flyer-din-lang-105-cm-x-210-cm-topseller-beidseitig-bedruckt.html', 189737, '135g hochwertiger Qualitätsdruck matt', 'STANDARD_PRODUCTION', '100000', 34, 'Postaktuell DIN-L Flyer', 72, 'Flyer & Falzflyer, DIN-L', 102, '2-Seiter, ungefalzt', 147, '135g Bilderdruck, matt', 1, 'Standard', '5', '1', NULL, NULL, 0),
(595, 'https://www.wir-machen-druck.de/flyer-din-lang-105-cm-x-210-cm-topseller-beidseitig-bedruckt.html', 189737, '135g hochwertiger Qualitätsdruck matt', 'STANDARD_PRODUCTION', '100000', 34, 'Postaktuell DIN-L Flyer', 72, 'Flyer & Falzflyer, DIN-L', 102, '2-Seiter, ungefalzt', 148, '135g Bilderdruck, glänzend', 1, 'Standard', '5', '1', NULL, NULL, 0),
(596, 'https://www.wir-machen-druck.de/flyer-din-lang-105-cm-x-210-cm-topseller-beidseitig-bedruckt.html', 189740, '170g hochwertiger Qualitätsdruck matt', 'STANDARD_PRODUCTION', '100000', 34, 'Postaktuell DIN-L Flyer', 72, 'Flyer & Falzflyer, DIN-L', 102, '2-Seiter, ungefalzt', 149, '170g Bilderdruck, matt', 1, 'Standard', '5', '1', NULL, NULL, 0),
(597, 'https://www.wir-machen-druck.de/flyer-din-lang-105-cm-x-210-cm-topseller-beidseitig-bedruckt.html', 189741, '170g hochwertiger Qualitätsdruck glänzend', 'STANDARD_PRODUCTION', '100000', 34, 'Postaktuell DIN-L Flyer', 72, 'Flyer & Falzflyer, DIN-L', 102, '2-Seiter, ungefalzt', 150, '170g Bilderdruck, gänzend', 1, 'Standard', '5', '1', NULL, NULL, 0),
(598, 'https://www.wir-machen-druck.de/flyer-din-lang-105-cm-x-210-cm-topseller-beidseitig-bedruckt.html', 189742, '250g hochwertiger Qualitätsdruck matt', 'STANDARD_PRODUCTION', '100000', 34, 'Postaktuell DIN-L Flyer', 72, 'Flyer & Falzflyer, DIN-L', 102, '2-Seiter, ungefalzt', 151, '250g Bilderdruck, matt', 1, 'Standard', '5', '1', NULL, NULL, 0),
(599, 'https://www.wir-machen-druck.de/flyer-din-lang-105-cm-x-210-cm-topseller-beidseitig-bedruckt.html', 189743, '250g hochwertiger Qualitätsdruck glänzend', 'STANDARD_PRODUCTION', '100000', 34, 'Postaktuell DIN-L Flyer', 72, 'Flyer & Falzflyer, DIN-L', 102, '2-Seiter, ungefalzt', 152, '250g Bilderdruck, glänzend', 1, 'Standard', '5', '1', NULL, NULL, 0),
(600, 'https://www.wir-machen-druck.de/flyer-din-lang-105-cm-x-210-cm-topseller-beidseitig-bedruckt.html', 189766, 'Offset: 150g Qualitätsdruck auf Offsetpapier (beschreibbar, Inkjet- und Laserdruck geeignet)', 'STANDARD_PRODUCTION', '100000', 34, 'Postaktuell DIN-L Flyer', 72, 'Flyer & Falzflyer, DIN-L', 102, '2-Seiter, ungefalzt', 153, '150g Naturkarton, creme', 1, 'Standard', '5', '1', NULL, NULL, 0),
(601, 'https://www.wir-machen-druck.de/flyer-din-lang-105-cm-x-210-cm-topseller-beidseitig-bedruckt.html', 189760, 'Natur: 150g Qualitätsdruck auf hochwertigem Naturkarton creme', 'STANDARD_PRODUCTION', '100000', 34, 'Postaktuell DIN-L Flyer', 72, 'Flyer & Falzflyer, DIN-L', 102, '2-Seiter, ungefalzt', 153, '150g Naturkarton, creme', 1, 'Standard', '5', '1', NULL, NULL, 0),
(602, 'https://www.wir-machen-druck.de/flyer-din-lang-105-cm-x-210-cm-topseller-beidseitig-bedruckt.html', 189766, 'Offset: 150g Qualitätsdruck auf Offsetpapier (beschreibbar, Inkjet- und Laserdruck geeignet)', 'STANDARD_PRODUCTION', '100000', 34, 'Postaktuell DIN-L Flyer', 72, 'Flyer & Falzflyer, DIN-L', 102, '2-Seiter, ungefalzt', 154, '150g Offsetpapier', 1, 'Standard', '5', '1', NULL, NULL, 0),
(603, 'https://www.wir-machen-druck.de/flyer-din-lang-105-cm-x-210-cm-topseller-beidseitig-bedruckt.html', 189770, 'Recycling: 170g hochwertiger Qualitätsdruck auf Recyclingpapier weiß matt', 'STANDARD_PRODUCTION', '100000', 34, 'Postaktuell DIN-L Flyer', 72, 'Flyer & Falzflyer, DIN-L', 102, '2-Seiter, ungefalzt', 158, '170g Recyclingpapier', 1, 'Standard', '5', '1', NULL, NULL, 0);

--
-- Indizes der exportierten Tabellen
--

--
-- Indizes für die Tabelle `tbl_url_list`
--
ALTER TABLE `tbl_url_list`
  ADD PRIMARY KEY (`id`) USING BTREE;

--
-- AUTO_INCREMENT für exportierte Tabellen
--

--
-- AUTO_INCREMENT für Tabelle `tbl_url_list`
--
ALTER TABLE `tbl_url_list`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=604;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
