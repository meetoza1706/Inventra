-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 09, 2025 at 10:27 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

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
  `admin_id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `company_id` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `apps`
--

CREATE TABLE `apps` (
  `app_id` int(11) NOT NULL,
  `app_name` varchar(255) NOT NULL,
  `app_description` text DEFAULT NULL,
  `default_access` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `apps`
--

INSERT INTO `apps` (`app_id`, `app_name`, `app_description`, `default_access`) VALUES
(1, 'Toolbox', 'App store to manage and install apps', 0),
(2, 'Inventory', 'Manage and track inventory items', 0),
(3, 'Order Book', 'Keep track of customer orders', 0),
(4, 'Stock Entry', 'Manage stock entries and updates', 0),
(5, 'Access Control', 'Manage roles and permissions (Admin only)', 0),
(6, 'Analytics', 'Analyze data and generate reports', 0),
(7, 'Payments', 'Manage and process payments', 0),
(8, 'Barcode Module', 'Manage barcode scanning and integration', 0),
(9, 'RFID', 'Handle RFID-based stock management', 0),
(10, 'Vendor List', 'Manage and track vendor information', 0);

-- --------------------------------------------------------

--
-- Table structure for table `company_data`
--

CREATE TABLE `company_data` (
  `company_id` int(11) NOT NULL,
  `company_name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `contact_number` varchar(50) DEFAULT NULL,
  `website` varchar(255) DEFAULT NULL,
  `date_established` date DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `company_data`
--

INSERT INTO `company_data` (`company_id`, `company_name`, `email`, `contact_number`, `website`, `date_established`, `status`, `user_id`, `created_at`) VALUES
(2, 'mcorp', 'main@mcorp.in', '09081363947', 'www.mcorp.in', '2025-03-01', 'Active', 1, '2025-03-08 19:24:20');

-- --------------------------------------------------------

--
-- Table structure for table `crm_table`
--

CREATE TABLE `crm_table` (
  `crm_id` int(11) NOT NULL,
  `customer_name` varchar(255) NOT NULL,
  `contact` varchar(100) DEFAULT NULL,
  `company_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `employee_data`
--

CREATE TABLE `employee_data` (
  `employee_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `company_id` int(11) NOT NULL,
  `company_name` varchar(255) NOT NULL,
  `role_id` int(11) NOT NULL,
  `when_joined` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `inventory_data`
--

CREATE TABLE `inventory_data` (
  `inventory_id` int(11) NOT NULL,
  `item_name` varchar(255) NOT NULL,
  `quantity` int(11) DEFAULT 0,
  `company_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `join_requests`
--

CREATE TABLE `join_requests` (
  `request_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `company_id` int(11) NOT NULL,
  `status` enum('pending','approved','rejected') DEFAULT 'pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
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
(14, 3, 2, 'pending', '2025-03-09 09:26:35');

-- --------------------------------------------------------

--
-- Table structure for table `location_data`
--

CREATE TABLE `location_data` (
  `location_id` int(11) NOT NULL,
  `company_id` int(11) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `zip` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `order_data`
--

CREATE TABLE `order_data` (
  `order_id` int(11) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `order_date` datetime DEFAULT current_timestamp(),
  `company_id` int(11) DEFAULT NULL,
  `total_amount` decimal(10,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `roles`
--

CREATE TABLE `roles` (
  `role_id` int(11) NOT NULL,
  `role_name` varchar(50) NOT NULL
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
  `role_id` int(11) NOT NULL,
  `role_name` varchar(50) NOT NULL,
  `permissions` text DEFAULT NULL
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
(10, 'Admin', '10'),
(12, 'Manager', '2'),
(13, 'Manager', '3'),
(14, 'Manager', '4'),
(15, 'Manager', '6'),
(17, 'Employee', '2'),
(18, 'Employee', '3');

-- --------------------------------------------------------

--
-- Table structure for table `sessions`
--

CREATE TABLE `sessions` (
  `session_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `login_time` datetime DEFAULT current_timestamp(),
  `expiration_time` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sessions`
--

INSERT INTO `sessions` (`session_id`, `user_id`, `login_time`, `expiration_time`, `is_active`) VALUES
(1, 3, '2025-03-09 14:34:03', '2025-03-09 15:34:03', 1),
(2, 1, '2025-03-09 14:55:24', '2025-03-09 15:55:24', 1),
(4, 1, '2025-03-09 14:47:29', '2025-03-09 15:47:29', 1),
(5, 1, '2025-03-09 14:21:55', '2025-03-09 15:21:55', 1),
(7, 1, '2025-03-09 14:18:23', '2025-03-09 15:18:23', 1),
(70, 1, '2025-03-09 14:51:15', '2025-03-09 15:51:15', 1),
(85, 2, '2025-03-09 14:09:15', '2025-03-09 15:09:15', 1),
(86, 1, '2025-03-09 14:09:31', '2025-03-09 15:09:31', 1),
(721, 2, '2025-03-09 14:27:16', '2025-03-09 15:27:16', 1),
(722, 3, '2025-03-09 14:33:20', '2025-03-09 15:33:20', 1),
(47321, 3, '2025-03-09 14:39:25', '2025-03-09 15:39:25', 1),
(64016, 3, '2025-03-09 14:51:42', '2025-03-09 15:51:42', 1),
(4825620, 1, '2025-03-09 14:39:04', '2025-03-09 15:39:04', 1),
(4825621, 1, '2025-03-09 14:47:53', '2025-03-09 15:47:53', 1),
(4825622, 3, '2025-03-09 14:48:07', '2025-03-09 15:48:07', 1),
(4825623, 2, '2025-03-09 14:52:01', '2025-03-09 15:52:01', 1),
(4825624, 3, '2025-03-09 14:54:33', '2025-03-09 15:54:33', 1),
(4825625, 2, '2025-03-09 14:54:57', '2025-03-09 15:54:57', 1),
(2147483647, 3, '2025-03-09 14:56:28', '2025-03-09 15:56:28', 1);

-- --------------------------------------------------------

--
-- Table structure for table `task_data`
--

CREATE TABLE `task_data` (
  `task_id` int(11) NOT NULL,
  `task_name` varchar(255) NOT NULL,
  `assigned_to` int(11) DEFAULT NULL,
  `status` enum('pending','completed') DEFAULT 'pending',
  `company_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `timesheet_data`
--

CREATE TABLE `timesheet_data` (
  `timesheet_id` int(11) NOT NULL,
  `employee_id` int(11) DEFAULT NULL,
  `check_in` datetime DEFAULT current_timestamp(),
  `check_out` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `transaction_data`
--

CREATE TABLE `transaction_data` (
  `transaction_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `transaction_type` enum('credit','debit') DEFAULT NULL,
  `amount` decimal(10,2) DEFAULT NULL,
  `transaction_date` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_access`
--

CREATE TABLE `user_access` (
  `access_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `company_id` int(11) DEFAULT NULL,
  `app_id` int(11) DEFAULT NULL,
  `can_view` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_apps`
--

CREATE TABLE `user_apps` (
  `user_app_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `app_id` int(11) DEFAULT NULL,
  `added_to_dashboard` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_data`
--

CREATE TABLE `user_data` (
  `user_id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `first_name` varchar(255) DEFAULT NULL,
  `last_name` varchar(255) DEFAULT NULL,
  `role_id` int(11) DEFAULT NULL,
  `company_id` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_data`
--

INSERT INTO `user_data` (`user_id`, `username`, `email`, `password_hash`, `first_name`, `last_name`, `role_id`, `company_id`, `created_at`) VALUES
(1, 'meet17', 'meet17', 'meet', 'Meet', 'Oza', 1, 2, '2025-03-07 12:04:30'),
(2, 'admin', 'admin@123', 'admin', NULL, NULL, 2, 2, '2025-03-08 13:54:42'),
(3, 'test1', 'test1@123', 'test', NULL, NULL, NULL, NULL, '2025-03-08 20:00:13');

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
-- Indexes for table `crm_table`
--
ALTER TABLE `crm_table`
  ADD PRIMARY KEY (`crm_id`),
  ADD KEY `company_id` (`company_id`);

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
-- Indexes for table `order_data`
--
ALTER TABLE `order_data`
  ADD PRIMARY KEY (`order_id`),
  ADD KEY `customer_id` (`customer_id`),
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
-- Indexes for table `transaction_data`
--
ALTER TABLE `transaction_data`
  ADD PRIMARY KEY (`transaction_id`),
  ADD KEY `user_id` (`user_id`);

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
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin_data`
--
ALTER TABLE `admin_data`
  MODIFY `admin_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `apps`
--
ALTER TABLE `apps`
  MODIFY `app_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `company_data`
--
ALTER TABLE `company_data`
  MODIFY `company_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `crm_table`
--
ALTER TABLE `crm_table`
  MODIFY `crm_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `employee_data`
--
ALTER TABLE `employee_data`
  MODIFY `employee_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `inventory_data`
--
ALTER TABLE `inventory_data`
  MODIFY `inventory_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `join_requests`
--
ALTER TABLE `join_requests`
  MODIFY `request_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `location_data`
--
ALTER TABLE `location_data`
  MODIFY `location_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `order_data`
--
ALTER TABLE `order_data`
  MODIFY `order_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `roles`
--
ALTER TABLE `roles`
  MODIFY `role_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `role_permissions`
--
ALTER TABLE `role_permissions`
  MODIFY `role_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT for table `sessions`
--
ALTER TABLE `sessions`
  MODIFY `session_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2147483648;

--
-- AUTO_INCREMENT for table `task_data`
--
ALTER TABLE `task_data`
  MODIFY `task_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `timesheet_data`
--
ALTER TABLE `timesheet_data`
  MODIFY `timesheet_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `transaction_data`
--
ALTER TABLE `transaction_data`
  MODIFY `transaction_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user_access`
--
ALTER TABLE `user_access`
  MODIFY `access_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user_apps`
--
ALTER TABLE `user_apps`
  MODIFY `user_app_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `user_data`
--
ALTER TABLE `user_data`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `admin_data`
--
ALTER TABLE `admin_data`
  ADD CONSTRAINT `admin_data_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `company_data` (`company_id`) ON DELETE SET NULL;

--
-- Constraints for table `crm_table`
--
ALTER TABLE `crm_table`
  ADD CONSTRAINT `crm_table_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `company_data` (`company_id`) ON DELETE CASCADE;

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
  ADD CONSTRAINT `inventory_data_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `company_data` (`company_id`) ON DELETE CASCADE;

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
-- Constraints for table `order_data`
--
ALTER TABLE `order_data`
  ADD CONSTRAINT `order_data_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `crm_table` (`crm_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `order_data_ibfk_2` FOREIGN KEY (`company_id`) REFERENCES `company_data` (`company_id`) ON DELETE CASCADE;

--
-- Constraints for table `sessions`
--
ALTER TABLE `sessions`
  ADD CONSTRAINT `sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_data` (`user_id`) ON DELETE CASCADE;

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
-- Constraints for table `transaction_data`
--
ALTER TABLE `transaction_data`
  ADD CONSTRAINT `transaction_data_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_data` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `user_access`
--
ALTER TABLE `user_access`
  ADD CONSTRAINT `user_access_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_data` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_access_ibfk_2` FOREIGN KEY (`company_id`) REFERENCES `company_data` (`company_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_access_ibfk_3` FOREIGN KEY (`app_id`) REFERENCES `apps` (`app_id`) ON DELETE CASCADE;

--
-- Constraints for table `user_apps`
--
ALTER TABLE `user_apps`
  ADD CONSTRAINT `user_apps_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_data` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_apps_ibfk_2` FOREIGN KEY (`app_id`) REFERENCES `apps` (`app_id`) ON DELETE CASCADE;

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
