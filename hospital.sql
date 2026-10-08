CREATE DATABASE IF NOT EXISTS py_doctor_appoinment_booking;
USE py_doctor_appoinment_booking;

CREATE TABLE IF NOT EXISTS doctor_tb (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(150) NOT NULL,
    doctor_name VARCHAR(150),
    speciality VARCHAR(150),
    doctor_image VARCHAR(255),
    experience INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS patient_tb (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(150) NOT NULL,
    mobile VARCHAR(30),
    gender VARCHAR(30),
    age INT
);

CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    doctor_id VARCHAR(100) NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    description TEXT,
    status VARCHAR(30) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
