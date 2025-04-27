CREATE DATABASE GymManagement;
USE GymManagement;

-- Users Table (General Users - Admins, Trainers, Members)
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15) UNIQUE,
    role ENUM('Admin', 'Trainer', 'Member') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
select * from users;

-- Membership Plans Table
CREATE TABLE Memberships (
    membership_id INT AUTO_INCREMENT PRIMARY KEY,
    type ENUM('Monthly', 'Quarterly', 'Yearly') NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    start_date DATE,
    end_date DATE
);
ALTER TABLE Memberships
CHANGE COLUMN type type ENUM('Premium', 'Gold', 'Silver') NOT NULL;
select * from memberships;


-- Members Table (Gym Members)
CREATE TABLE Members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    date_of_birth DATE,
    address TEXT,
    membership_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (membership_id) REFERENCES Memberships(membership_id) ON DELETE SET NULL
);
DESC Members;
ALTER TABLE Members ADD COLUMN name_full VARCHAR(255);
ALTER TABLE Members ADD COLUMN membership_type VARCHAR(255);
ALTER TABLE Members
ADD COLUMN membership_id INT,
ADD FOREIGN KEY (membership_id) REFERENCES Memberships(membership_id) ON DELETE SET NULL;
ALTER TABLE Members DROP COLUMN membership_id;
ALTER TABLE Members
DROP FOREIGN KEY members_ibfk_2;
ALTER TABLE Members
DROP COLUMN membership_id;
ALTER TABLE Members
ADD COLUMN membership_id INT,
ADD FOREIGN KEY (membership_id) REFERENCES Memberships(membership_id) ON DELETE SET NULL;
SELECT * FROM MEMBERS;







-- Trainers Table (Gym Trainers)
CREATE TABLE Trainers (
    trainer_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    specialization VARCHAR(255),
    experience INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);
desc trainers;
SELECT * FROM TRAINERS;
ALTER TABLE Trainers
ADD COLUMN bio TEXT;
ALTER TABLE Trainers
ADD COLUMN image_url VARCHAR(255);
ALTER TABLE Trainers
ADD CONSTRAINT fk_user_id
FOREIGN KEY (user_id) REFERENCES Users(user_id)
ON DELETE CASCADE;
SELECT t.user_id, u.name, u.email, t.bio, t.experience, t.specialization, t.image_url
FROM Users u
JOIN Trainers t ON u.user_id = t.user_id
WHERE u.role = 'trainer' AND u.user_id = 39;  -- Replace '1' with the actual user_id






-- Payments Table
CREATE TABLE Payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    method ENUM('Cash', 'Credit Card', 'UPI', 'Net Banking') NOT NULL,
    FOREIGN KEY (member_id) REFERENCES Members(member_id) ON DELETE CASCADE
);
select * from payments;
-- Attendance Table
CREATE TABLE Attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    check_in TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    check_out TIMESTAMP NULL,
    FOREIGN KEY (member_id) REFERENCES Members(member_id) ON DELETE CASCADE
);
select * from attendance;
-- Equipment Table
CREATE TABLE Equipment (
    equipment_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    purchase_date DATE,
    status ENUM('Operational', 'Under Maintenance', 'Out of Service') DEFAULT 'Operational'
);
desc equipment;
select * from equipment;
ALTER TABLE Equipment ADD COLUMN image_url VARCHAR(255);
ALTER TABLE Equipment 
CHANGE COLUMN image_url equipment_image_url VARCHAR(255) DEFAULT NULL;


