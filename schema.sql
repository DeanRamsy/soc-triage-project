-- MySQL dump 10.13  Distrib 9.3.0, for macos15 (x86_64)
--
-- Host: localhost    Database: SOCTriage
-- ------------------------------------------------------
-- Server version	9.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Endpoints`
--

DROP TABLE IF EXISTS `Endpoints`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Endpoints` (
  `IP_Address` varchar(45) NOT NULL,
  PRIMARY KEY (`IP_Address`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Network_Connections`
--

DROP TABLE IF EXISTS `Network_Connections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Network_Connections` (
  `UID` varchar(50) NOT NULL,
  `Timestamp` datetime DEFAULT NULL,
  `Source_IP` varchar(45) DEFAULT NULL,
  `Source_Port` int DEFAULT NULL,
  `Dest_IP` varchar(45) DEFAULT NULL,
  `Dest_Port` int DEFAULT NULL,
  `Protocol` varchar(10) DEFAULT NULL,
  `Conn_State` varchar(10) DEFAULT NULL,
  `Service_Name` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`UID`),
  KEY `Source_IP` (`Source_IP`),
  KEY `Dest_IP` (`Dest_IP`),
  KEY `Service_Name` (`Service_Name`),
  CONSTRAINT `network_connections_ibfk_1` FOREIGN KEY (`Source_IP`) REFERENCES `Endpoints` (`IP_Address`),
  CONSTRAINT `network_connections_ibfk_2` FOREIGN KEY (`Dest_IP`) REFERENCES `Endpoints` (`IP_Address`),
  CONSTRAINT `network_connections_ibfk_3` FOREIGN KEY (`Service_Name`) REFERENCES `Services` (`Service_Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Services`
--

DROP TABLE IF EXISTS `Services`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Services` (
  `Service_Name` varchar(20) NOT NULL,
  PRIMARY KEY (`Service_Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-18 19:34:25
