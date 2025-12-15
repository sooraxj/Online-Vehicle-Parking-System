-- Table for managing slots (independent table)
CREATE TABLE `tbl_slots` (
  `slot_id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `slotname` VARCHAR(50) NOT NULL,
  `fare` DECIMAL(10,2) NOT NULL,
  `number_of_slots` INT(11) NOT NULL,
  `status` ENUM('Active', 'Inactive') DEFAULT 'Active'
);

-- Table for login credentials (independent table)
CREATE TABLE `tbl_login` (
  `username` VARCHAR(50) NOT NULL PRIMARY KEY,
  `password` VARCHAR(255) NOT NULL,
  `status` ENUM('Active', 'Inactive') DEFAULT 'Active'
);

-- Table for managing parking slots
CREATE TABLE `tbl_parking` (
  `park_id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `custname` VARCHAR(100) NOT NULL,
  `veh_no` VARCHAR(20) NOT NULL,
  `contact_no` VARCHAR(15) NOT NULL,
  `entry_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  `exit_time` TIMESTAMP NULL DEFAULT NULL,
  `date` DATE DEFAULT CURDATE(),
  `status` ENUM('Parked', 'Exited') DEFAULT 'Parked',
  `slot_id` INT(11),
  `slot_number` INT(11),
  CONSTRAINT `fk_slot` FOREIGN KEY (`slot_id`) REFERENCES `tbl_slots` (`slot_id`) ON DELETE SET NULL
);

-- Table for payments, referencing parking
CREATE TABLE `tbl_payment` (
  `payment_id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `park_id` INT(11) NOT NULL,
  `amount` DECIMAL(10,2) NOT NULL,
  `status` ENUM('Paid', 'Pending') DEFAULT 'Pending',
  `ticket_number` VARCHAR(20) UNIQUE NOT NULL,
  CONSTRAINT `fk_park` FOREIGN KEY (`park_id`) REFERENCES `tbl_parking` (`park_id`) ON DELETE CASCADE
);

