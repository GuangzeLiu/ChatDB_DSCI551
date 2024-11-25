-- Create a table
CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    department VARCHAR(255)
);

-- Insert data into the table
INSERT INTO employees (name, age, department) VALUES
('Alice', 30, 'HR'),
('Bob', 40, 'Engineering'),
('Charlie', 35, 'Sales'),
('Diana', 25, 'Marketing');
