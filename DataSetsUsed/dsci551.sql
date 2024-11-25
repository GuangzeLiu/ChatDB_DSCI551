INSERT INTO Instructoradvisor (Instructor_ID, Instructor_Name)
VALUES 
(2, 'Dr. Brown'),
(3, 'Dr. Smith'),
(4, 'Dr. White');

INSERT INTO Students (StudentID, FirstName, LastName, Email, Major, AdvisorID)
VALUES 
(1, 'John', 'Doe', 'john.doe@example.com', 'Computer Science', 3),
(2, 'Jane', 'Doe', 'jane.doe@example.com', 'Business', 2),
(3, 'Jim', 'Beam', 'jim.beam@example.com', 'Mathematics', 3),
(4, 'Alice', 'Johnson', 'alice.johnson@example.com', 'Computer Science', 4),
(5, 'John', 'Smith', 'john.smith@example.com', 'Business', 2),
(6, 'Bill', 'Chu', 'bill.chu@example.com', 'Mathematics', 3),
(7, 'David', 'Small', 'david.small@example.com', 'Computer Science', 3);

INSERT INTO Courses (CourseID, CourseName, CreditHours, InstructorID)
VALUES 
(101, 'Data Structures', 3, 2),
(102, 'Calculus', 4, 3),
(103, 'Database Systems', 3, 2),
(104, 'Linear Algebra', 3, 3),
(105, 'Introduction to Business', 3, 4),
(101, 'Data Structures', 3, 3);

INSERT INTO Enrollments (EnrollmentID, StudentID, CourseID, Semester, Grade)
VALUES 
(1, 1, 101, 'Fall 2023', 'A'),
(2, 2, 102, 'Fall 2023', 'B'),
(3, 1, 103, 'Fall 2023', 'A'),
(4, 3, 101, 'Fall 2023', 'A'),
(5, 4, 104, 'Fall 2023', 'C'),
(6, 5, 101, 'Fall 2023', 'A'),
(7, 6, 102, 'Fall 2023', 'B');

CREATE TABLE InstructorAdvisor (
    Instructor_ID INT PRIMARY KEY, 
    Instructor_Name VARCHAR(50) NOT NULL
);

CREATE TABLE Students( 
	StudentID INT Primary key,
    FirstName varchar(50) not null,
    LastName varchar(50) not null, 
    Email varchar(50) not null,
    Major varchar(50) not null,
    AdvisorID int, 
    foreign key (AdvisorID) references InstructorAdvisor(Instructor_ID)    
);

CREATE TABLE Courses(
	CourseID int,
    CourseName varchar(50) not null, 
    InstructorID int, 
    primary key (CourseID, InstructorID),
    foreign key (InstructorID) references InstructorAdvisor(Instructor_ID),
    CreditHours int not null
);

CREATE TABLE Enrollments(
	EnrollmentID int primary key,
    StudentID int not null,
    CourseID int not null,
    foreign key(StudentID) references Students(StudentID),
    foreign key(CourseID) references Courses(CourseID), 
    Semester varchar(50) not null,
    Grade varchar(10) not null
);
