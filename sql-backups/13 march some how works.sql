-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Mar 12, 2025 at 09:00 PM
-- Server version: 8.0.30
-- PHP Version: 8.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `inventra`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin_data`
--

CREATE TABLE `admin_data` (
  `admin_id` int NOT NULL,
  `username` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `company_id` int DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `apps`
--

CREATE TABLE `apps` (
  `app_id` int NOT NULL,
  `app_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `app_description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `app_route` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `apps`
--

INSERT INTO `apps` (`app_id`, `app_name`, `app_description`, `app_route`) VALUES
(1, 'Inventory', 'Manage and track inventory items', '/inventory'),
(2, 'Stock_Entry', 'Manage stock entries and updates', '/stock_entry'),
(3, 'Access_Control', 'Manage roles and permissions (Admin only)', '/access_control'),
(4, 'Analytics', 'Analyze data and generate reports', '/analytics'),
(5, 'Barcode_Module', 'Manage barcode scanning and integration', '/barcode_module'),
(6, 'vendor list', 'list of vendors', '/vendor_list');

-- --------------------------------------------------------

--
-- Table structure for table `company_data`
--

CREATE TABLE `company_data` (
  `company_id` int NOT NULL,
  `company_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `contact_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `website` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `date_established` date DEFAULT NULL,
  `status` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `company_data`
--

INSERT INTO `company_data` (`company_id`, `company_name`, `email`, `contact_number`, `website`, `date_established`, `status`, `user_id`, `created_at`) VALUES
(2, 'm.corp', 'main@mcorp.in', '09081363947', 'www.mcorp.in', '2025-03-01', 'Active', 1, '2025-03-08 19:24:20'),
(3, 'Mansukh and sons', 'mansukh@gmail.com', '9081363947', 'www.mansukh.com', '2025-03-14', 'Active', 4, '2025-03-10 08:03:25'),
(10, 'AlphaTech Solutions', 'contact@alphatech.com', '9876543210', 'https://alphatech.com', '2024-03-01', 'active', NULL, '2025-03-12 17:38:22'),
(11, 'AlphaTech', 'alpha@123', '0908136394', 'www.alpha.com', '2025-02-28', 'Active', 3, '2025-03-12 20:33:23');

-- --------------------------------------------------------

--
-- Table structure for table `employee_data`
--

CREATE TABLE `employee_data` (
  `employee_id` int NOT NULL,
  `user_id` int NOT NULL,
  `company_id` int NOT NULL,
  `company_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `role_id` int NOT NULL,
  `when_joined` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `employee_data`
--

INSERT INTO `employee_data` (`employee_id`, `user_id`, `company_id`, `company_name`, `role_id`, `when_joined`) VALUES
(201, 102, 10, 'AlphaTech Solutions', 2, '2025-03-12 23:08:48');

-- --------------------------------------------------------

--
-- Table structure for table `inventory_data`
--

CREATE TABLE `inventory_data` (
  `inventory_id` int NOT NULL,
  `item_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `quantity` int DEFAULT '0',
  `company_id` int DEFAULT NULL,
  `location_id` int NOT NULL,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `unit_price` decimal(10,2) NOT NULL DEFAULT '0.00',
  `reorder_level` int NOT NULL DEFAULT '0',
  `item_description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `vendor_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `inventory_data`
--

INSERT INTO `inventory_data` (`inventory_id`, `item_name`, `quantity`, `company_id`, `location_id`, `updated_at`, `unit_price`, `reorder_level`, `item_description`, `vendor_id`) VALUES
(1, 'Laptop Dell XPS 13', 30, 10, 1, '2025-03-12 18:32:00', 90000.00, 5, 'High-end ultrabook laptop.', 1),
(2, 'Wireless Mouse Logitech', 50, 10, 2, '2025-03-12 18:32:00', 2500.00, 10, 'Ergonomic wireless mouse.', 2),
(3, 'Printer HP LaserJet', 10, 10, 3, '2025-03-12 18:32:00', 15000.00, 2, 'High-speed laser printer.', 3),
(4, 'Office Chair', 20, 10, 3, '2025-03-12 18:32:00', 7500.00, 5, 'Ergonomic office chair.', 2),
(5, 'Notebook A5', 100, 10, 4, '2025-03-12 18:32:00', 50.00, 20, 'Standard A5 notebook.', 1),
(6, 'Smartphone Samsung S23', 15, 10, 1, '2025-03-12 18:32:00', 65000.00, 3, 'Latest flagship smartphone.', 1),
(7, 'adapters', 12, 10, 1, '2025-03-12 20:51:11', 12222.00, 1, 'asdawe', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `inventory_locations`
--

CREATE TABLE `inventory_locations` (
  `location_id` int NOT NULL,
  `company_id` int NOT NULL,
  `location_name` varchar(255) NOT NULL,
  `address` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `inventory_location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `inventory_locations`
--

INSERT INTO `inventory_locations` (`location_id`, `company_id`, `location_name`, `address`, `created_at`, `inventory_location`) VALUES
(1, 10, 'Main Warehouse', NULL, '2025-03-12 18:32:00', NULL),
(2, 10, 'Office Storage', NULL, '2025-03-12 18:32:00', NULL),
(3, 10, 'Retail Store', NULL, '2025-03-12 18:32:00', NULL),
(4, 10, 'Distribution Center', NULL, '2025-03-12 18:32:00', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `join_requests`
--

CREATE TABLE `join_requests` (
  `request_id` int NOT NULL,
  `user_id` int NOT NULL,
  `company_id` int NOT NULL,
  `status` enum('pending','approved','rejected') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT 'pending',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `join_requests`
--

INSERT INTO `join_requests` (`request_id`, `user_id`, `company_id`, `status`, `created_at`) VALUES
(4, 2, 2, '', '2025-03-08 19:56:35'),
(5, 3, 2, '', '2025-03-08 20:00:28'),
(6, 2, 2, '', '2025-03-09 08:22:51'),
(7, 2, 2, '', '2025-03-09 08:29:19'),
(8, 2, 2, '', '2025-03-09 08:39:21'),
(9, 1, 2, '', '2025-03-09 08:47:51'),
(10, 1, 2, 'rejected', '2025-03-09 08:48:28'),
(11, 3, 2, '', '2025-03-09 09:08:59'),
(12, 3, 2, '', '2025-03-09 09:17:24'),
(13, 3, 2, '', '2025-03-09 09:21:07'),
(14, 3, 2, '', '2025-03-09 09:26:35'),
(15, 3, 2, '', '2025-03-09 09:41:07'),
(16, 3, 2, '', '2025-03-09 09:44:06'),
(17, 5, 3, 'approved', '2025-03-10 08:05:46');

-- --------------------------------------------------------

--
-- Table structure for table `location_data`
--

CREATE TABLE `location_data` (
  `location_id` int NOT NULL,
  `company_id` int DEFAULT NULL,
  `address` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `city` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `state` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `zip` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `notification_id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `company_id` int DEFAULT NULL,
  `message` text,
  `notification_type` varchar(50) DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `roles`
--

CREATE TABLE `roles` (
  `role_id` int NOT NULL,
  `role_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `roles`
--

INSERT INTO `roles` (`role_id`, `role_name`) VALUES
(1, 'admin'),
(3, 'employee'),
(2, 'manager');

-- --------------------------------------------------------

--
-- Table structure for table `role_permissions`
--

CREATE TABLE `role_permissions` (
  `role_id` int NOT NULL,
  `role_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `permissions` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `role_permissions`
--

INSERT INTO `role_permissions` (`role_id`, `role_name`, `permissions`) VALUES
(1, 'Admin', '1'),
(2, 'Admin', '2'),
(3, 'Admin', '3'),
(4, 'Admin', '4'),
(5, 'Admin', '5'),
(6, 'Admin', '6'),
(7, 'Admin', '7'),
(8, 'Admin', '8'),
(9, 'Admin', '9'),
(10, 'Admin', '10');

-- --------------------------------------------------------

--
-- Table structure for table `sessions`
--

CREATE TABLE `sessions` (
  `session_id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `login_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `expiration_time` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `ip_address` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sessions`
--

INSERT INTO `sessions` (`session_id`, `user_id`, `login_time`, `expiration_time`, `is_active`, `ip_address`) VALUES
(1, 1, '2025-03-13 02:05:25', '2025-03-13 03:05:25', 1, '127.0.0.1'),
(2, 4, '2025-03-13 02:06:05', '2025-03-13 03:06:05', 1, '127.0.0.1'),
(3, 101, '2025-03-13 02:16:38', '2025-03-13 03:16:38', 1, '127.0.0.1');

-- --------------------------------------------------------

--
-- Table structure for table `stock_levels`
--

CREATE TABLE `stock_levels` (
  `stock_id` int NOT NULL,
  `inventory_id` int NOT NULL,
  `location_id` int NOT NULL,
  `quantity` int NOT NULL DEFAULT '0',
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `stock_levels`
--

INSERT INTO `stock_levels` (`stock_id`, `inventory_id`, `location_id`, `quantity`, `last_updated`) VALUES
(1, 7, 1, 12, '2025-03-12 20:51:11');

-- --------------------------------------------------------

--
-- Table structure for table `stock_movements`
--

CREATE TABLE `stock_movements` (
  `movement_id` int NOT NULL,
  `inventory_id` int NOT NULL,
  `from_location` int DEFAULT NULL,
  `to_location` int DEFAULT NULL,
  `quantity` int NOT NULL,
  `movement_type` enum('IN','OUT','TRANSFER') NOT NULL,
  `performed_by` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `stock_movements`
--

INSERT INTO `stock_movements` (`movement_id`, `inventory_id`, `from_location`, `to_location`, `quantity`, `movement_type`, `performed_by`, `created_at`) VALUES
(1, 1, 1, NULL, 5, 'OUT', 1001, '2025-03-12 18:32:00'),
(2, 2, 2, NULL, 10, 'OUT', 1002, '2025-03-12 18:32:00'),
(3, 3, 3, NULL, 2, 'OUT', 1003, '2025-03-12 18:32:00'),
(4, 4, 3, NULL, 3, 'OUT', 1004, '2025-03-12 18:32:00'),
(5, 5, 4, NULL, 50, 'OUT', 1005, '2025-03-12 18:32:00'),
(6, 6, 1, NULL, 4, 'OUT', 1006, '2025-03-12 18:32:00'),
(7, 1, NULL, 1, 10, 'IN', 1001, '2025-03-12 18:32:00'),
(8, 2, NULL, 2, 20, 'IN', 1002, '2025-03-12 18:32:00'),
(9, 3, NULL, 3, 5, 'IN', 1003, '2025-03-12 18:32:00'),
(10, 4, NULL, 3, 5, 'IN', 1004, '2025-03-12 18:32:00'),
(11, 5, NULL, 4, 100, 'IN', 1005, '2025-03-12 18:32:00'),
(12, 6, NULL, 1, 10, 'IN', 1006, '2025-03-12 18:32:00'),
(13, 1, 1, NULL, 3, 'OUT', 4, '2025-03-11 20:44:34'),
(14, 2, 2, NULL, 5, 'OUT', 4, '2025-03-10 20:44:34'),
(15, 3, NULL, 3, 10, 'IN', 4, '2025-03-09 20:44:34'),
(16, 4, 4, NULL, 2, 'OUT', 4, '2025-03-08 20:44:34'),
(17, 5, 2, 1, 4, 'TRANSFER', 4, '2025-03-07 20:44:34'),
(18, 6, 1, NULL, 1, 'OUT', 4, '2025-03-06 20:44:34');

-- --------------------------------------------------------

--
-- Table structure for table `task_data`
--

CREATE TABLE `task_data` (
  `task_id` int NOT NULL,
  `task_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `assigned_to` int DEFAULT NULL,
  `status` enum('pending','completed') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT 'pending',
  `company_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `timesheet_data`
--

CREATE TABLE `timesheet_data` (
  `timesheet_id` int NOT NULL,
  `employee_id` int DEFAULT NULL,
  `check_in` datetime DEFAULT CURRENT_TIMESTAMP,
  `check_out` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_access`
--

CREATE TABLE `user_access` (
  `access_id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `company_id` int DEFAULT NULL,
  `app_id` int DEFAULT NULL,
  `can_view` tinyint(1) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_apps`
--

CREATE TABLE `user_apps` (
  `user_app_id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `app_id` int DEFAULT NULL,
  `added_to_dashboard` tinyint(1) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_apps`
--

INSERT INTO `user_apps` (`user_app_id`, `user_id`, `app_id`, `added_to_dashboard`) VALUES
(11, 2, 2, 0),
(13, 3, 4, 1),
(17, 3, 2, 1),
(24, 4, 8, 0),
(25, 4, 8, 0),
(26, 4, 8, 0),
(27, 4, 8, 0),
(28, 4, 8, 0),
(29, 4, 8, 0),
(30, 4, 8, 0),
(31, 4, 8, 0),
(32, 4, 8, 0),
(33, 4, 8, 0),
(34, 4, 8, 0),
(43, 5, 4, 1);

-- --------------------------------------------------------

--
-- Table structure for table `user_data`
--

CREATE TABLE `user_data` (
  `user_id` int NOT NULL,
  `username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `first_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `last_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `role_id` int DEFAULT NULL,
  `company_id` int DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_data`
--

INSERT INTO `user_data` (`user_id`, `username`, `email`, `password_hash`, `first_name`, `last_name`, `role_id`, `company_id`, `created_at`) VALUES
(1, 'meet17', 'meet17', 'meet', 'Meet', 'Oza', 1, 2, '2025-03-07 12:04:30'),
(2, 'admin', 'admin@123', 'admin', NULL, NULL, 2, 2, '2025-03-08 13:54:42'),
(3, 'test1', 'test1@123', 'test', NULL, NULL, 1, 11, '2025-03-08 20:00:13'),
(4, 'test2', 'test2@123', 'test', NULL, NULL, 1, 3, '2025-03-10 08:02:25'),
(5, 'test3', 'test3@gmail.com', 'test', NULL, NULL, 3, 3, '2025-03-10 08:05:05'),
(101, 'johndoe_admin', 'john.admin@alphatech.com', 'admin123', 'John', NULL, 1, 10, '2025-03-12 17:38:33'),
(102, 'janedoe_emp', 'jane.employee@alphatech.com', 'employee123', 'Jane', NULL, 2, 10, '2025-03-12 17:38:33');

-- --------------------------------------------------------

--
-- Table structure for table `vendor_data`
--

CREATE TABLE `vendor_data` (
  `vendor_id` int NOT NULL,
  `company_id` int DEFAULT NULL,
  `vendor_name` varchar(255) NOT NULL,
  `vendor_contact` varchar(50) DEFAULT NULL,
  `vendor_email` varchar(255) DEFAULT NULL,
  `vendor_address` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `vendor_data`
--

INSERT INTO `vendor_data` (`vendor_id`, `company_id`, `vendor_name`, `vendor_contact`, `vendor_email`, `vendor_address`) VALUES
(1, 10, 'Tech Supplies Inc.', '9876543210', 'techsupplies@example.com', '123 Tech Park, City A'),
(2, 10, 'Office Gear Ltd.', '8765432109', 'officegear@example.com', '456 Office St, City B'),
(3, 10, 'LogiTech Solutions', '7654321098', 'logitech@example.com', '789 Gadget Ave, City C'),
(4, 3, 'Prime Tech Suppliers', '9876543210', 'prime@techsuppliers.com', '123 Supplier St, NY'),
(5, 3, 'Global Office Solutions', '9123456789', 'contact@globaloffice.com', '456 Office Lane, NY'),
(6, 3, 'Rapid Electronics', '9988776655', 'info@rapidelec.com', '789 Electronics Ave, NY'),
(7, 3, 'Prime Tech Suppliers', '9876543210', 'prime@techsuppliers.com', '123 Supplier St, NY'),
(8, 3, 'Global Office Solutions', '9123456789', 'contact@globaloffice.com', '456 Office Lane, NY'),
(9, 3, 'Rapid Electronics', '9988776655', 'info@rapidelec.com', '789 Electronics Ave, NY');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin_data`
--
ALTER TABLE `admin_data`
  ADD PRIMARY KEY (`admin_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `company_id` (`company_id`);

--
-- Indexes for table `apps`
--
ALTER TABLE `apps`
  ADD PRIMARY KEY (`app_id`);

--
-- Indexes for table `company_data`
--
ALTER TABLE `company_data`
  ADD PRIMARY KEY (`company_id`);

--
-- Indexes for table `employee_data`
--
ALTER TABLE `employee_data`
  ADD PRIMARY KEY (`employee_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `company_id` (`company_id`);

--
-- Indexes for table `inventory_data`
--
ALTER TABLE `inventory_data`
  ADD PRIMARY KEY (`inventory_id`),
  ADD KEY `company_id` (`company_id`),
  ADD KEY `location_id` (`location_id`);

--
-- Indexes for table `inventory_locations`
--
ALTER TABLE `inventory_locations`
  ADD PRIMARY KEY (`location_id`),
  ADD KEY `company_id` (`company_id`);

--
-- Indexes for table `join_requests`
--
ALTER TABLE `join_requests`
  ADD PRIMARY KEY (`request_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `company_id` (`company_id`);

--
-- Indexes for table `location_data`
--
ALTER TABLE `location_data`
  ADD PRIMARY KEY (`location_id`),
  ADD KEY `company_id` (`company_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`notification_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `company_id` (`company_id`);

--
-- Indexes for table `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`role_id`),
  ADD UNIQUE KEY `role_name` (`role_name`);

--
-- Indexes for table `role_permissions`
--
ALTER TABLE `role_permissions`
  ADD PRIMARY KEY (`role_id`);

--
-- Indexes for table `sessions`
--
ALTER TABLE `sessions`
  ADD PRIMARY KEY (`session_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `stock_levels`
--
ALTER TABLE `stock_levels`
  ADD PRIMARY KEY (`stock_id`),
  ADD KEY `inventory_id` (`inventory_id`),
  ADD KEY `location_id` (`location_id`);

--
-- Indexes for table `stock_movements`
--
ALTER TABLE `stock_movements`
  ADD PRIMARY KEY (`movement_id`),
  ADD KEY `inventory_id` (`inventory_id`),
  ADD KEY `from_location` (`from_location`),
  ADD KEY `to_location` (`to_location`);

--
-- Indexes for table `task_data`
--
ALTER TABLE `task_data`
  ADD PRIMARY KEY (`task_id`),
  ADD KEY `assigned_to` (`assigned_to`),
  ADD KEY `company_id` (`company_id`);

--
-- Indexes for table `timesheet_data`
--
ALTER TABLE `timesheet_data`
  ADD PRIMARY KEY (`timesheet_id`),
  ADD KEY `employee_id` (`employee_id`);

--
-- Indexes for table `user_access`
--
ALTER TABLE `user_access`
  ADD PRIMARY KEY (`access_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `company_id` (`company_id`),
  ADD KEY `app_id` (`app_id`);

--
-- Indexes for table `user_apps`
--
ALTER TABLE `user_apps`
  ADD PRIMARY KEY (`user_app_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `app_id` (`app_id`);

--
-- Indexes for table `user_data`
--
ALTER TABLE `user_data`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `role_id` (`role_id`),
  ADD KEY `company_id` (`company_id`);

--
-- Indexes for table `vendor_data`
--
ALTER TABLE `vendor_data`
  ADD PRIMARY KEY (`vendor_id`),
  ADD KEY `company_id` (`company_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin_data`
--
ALTER TABLE `admin_data`
  MODIFY `admin_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `apps`
--
ALTER TABLE `apps`
  MODIFY `app_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `company_data`
--
ALTER TABLE `company_data`
  MODIFY `company_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `employee_data`
--
ALTER TABLE `employee_data`
  MODIFY `employee_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=202;

--
-- AUTO_INCREMENT for table `inventory_data`
--
ALTER TABLE `inventory_data`
  MODIFY `inventory_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `inventory_locations`
--
ALTER TABLE `inventory_locations`
  MODIFY `location_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `join_requests`
--
ALTER TABLE `join_requests`
  MODIFY `request_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `location_data`
--
ALTER TABLE `location_data`
  MODIFY `location_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `notification_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `roles`
--
ALTER TABLE `roles`
  MODIFY `role_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `role_permissions`
--
ALTER TABLE `role_permissions`
  MODIFY `role_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT for table `sessions`
--
ALTER TABLE `sessions`
  MODIFY `session_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `stock_levels`
--
ALTER TABLE `stock_levels`
  MODIFY `stock_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `stock_movements`
--
ALTER TABLE `stock_movements`
  MODIFY `movement_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT for table `task_data`
--
ALTER TABLE `task_data`
  MODIFY `task_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `timesheet_data`
--
ALTER TABLE `timesheet_data`
  MODIFY `timesheet_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user_access`
--
ALTER TABLE `user_access`
  MODIFY `access_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user_apps`
--
ALTER TABLE `user_apps`
  MODIFY `user_app_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=44;

--
-- AUTO_INCREMENT for table `user_data`
--
ALTER TABLE `user_data`
  MODIFY `user_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=103;

--
-- AUTO_INCREMENT for table `vendor_data`
--
ALTER TABLE `vendor_data`
  MODIFY `vendor_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `admin_data`
--
ALTER TABLE `admin_data`
  ADD CONSTRAINT `admin_data_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `company_data` (`company_id`) ON DELETE SET NULL;

--
-- Constraints for table `employee_data`
--
ALTER TABLE `employee_data`
  ADD CONSTRAINT `employee_data_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_data` (`user_id`),
  ADD CONSTRAINT `employee_data_ibfk_2` FOREIGN KEY (`company_id`) REFERENCES `company_data` (`company_id`);

--
-- Constraints for table `inventory_data`
--
ALTER TABLE `inventory_data`
  ADD CONSTRAINT `inventory_data_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `company_data` (`company_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `inventory_data_ibfk_2` FOREIGN KEY (`location_id`) REFERENCES `inventory_locations` (`location_id`) ON DELETE CASCADE;

--
-- Constraints for table `inventory_locations`
--
ALTER TABLE `inventory_locations`
  ADD CONSTRAINT `inventory_locations_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `company_data` (`company_id`) ON DELETE CASCADE;

--
-- Constraints for table `join_requests`
--
ALTER TABLE `join_requests`
  ADD CONSTRAINT `join_requests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_data` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `join_requests_ibfk_2` FOREIGN KEY (`company_id`) REFERENCES `company_data` (`company_id`) ON DELETE CASCADE;

--
-- Constraints for table `location_data`
--
ALTER TABLE `location_data`
  ADD CONSTRAINT `location_data_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `company_data` (`company_id`) ON DELETE CASCADE;

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_data` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`company_id`) REFERENCES `company_data` (`company_id`) ON DELETE CASCADE;

--
-- Constraints for table `sessions`
--
ALTER TABLE `sessions`
  ADD CONSTRAINT `sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_data` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `stock_levels`
--
ALTER TABLE `stock_levels`
  ADD CONSTRAINT `stock_levels_ibfk_1` FOREIGN KEY (`inventory_id`) REFERENCES `inventory_data` (`inventory_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `stock_levels_ibfk_2` FOREIGN KEY (`location_id`) REFERENCES `inventory_locations` (`location_id`) ON DELETE CASCADE;

--
-- Constraints for table `stock_movements`
--
ALTER TABLE `stock_movements`
  ADD CONSTRAINT `stock_movements_ibfk_1` FOREIGN KEY (`inventory_id`) REFERENCES `inventory_data` (`inventory_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `stock_movements_ibfk_2` FOREIGN KEY (`from_location`) REFERENCES `inventory_locations` (`location_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `stock_movements_ibfk_3` FOREIGN KEY (`to_location`) REFERENCES `inventory_locations` (`location_id`) ON DELETE SET NULL;

--
-- Constraints for table `task_data`
--
ALTER TABLE `task_data`
  ADD CONSTRAINT `task_data_ibfk_1` FOREIGN KEY (`assigned_to`) REFERENCES `employee_data` (`employee_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `task_data_ibfk_2` FOREIGN KEY (`company_id`) REFERENCES `company_data` (`company_id`) ON DELETE CASCADE;

--
-- Constraints for table `timesheet_data`
--
ALTER TABLE `timesheet_data`
  ADD CONSTRAINT `timesheet_data_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employee_data` (`employee_id`) ON DELETE CASCADE;

--
-- Constraints for table `user_access`
--
ALTER TABLE `user_access`
  ADD CONSTRAINT `user_access_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_data` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_access_ibfk_2` FOREIGN KEY (`company_id`) REFERENCES `company_data` (`company_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_access_ibfk_3` FOREIGN KEY (`app_id`) REFERENCES `apps` (`app_id`) ON DELETE CASCADE;

--
-- Constraints for table `user_data`
--
ALTER TABLE `user_data`
  ADD CONSTRAINT `user_data_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `role_permissions` (`role_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `user_data_ibfk_2` FOREIGN KEY (`company_id`) REFERENCES `company_data` (`company_id`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
