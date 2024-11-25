# ChatDB

ChatDB is an interactive application that simplifies database interactions for both SQL (MySQL) and NoSQL (MongoDB) databases. It allows users to query, upload, delete, and explore datasets using either natural language or predefined constructs, making database management intuitive and user-friendly.

## Features

### General Features
- Support for **MySQL** and **MongoDB** databases.
- Secure credential handling for database connections.
- Dynamic schema exploration:
    - View tables and columns in MySQL.
    - View collections and fields in MongoDB.

### MySQL Features
- Generate sample queries with advanced SQL constructs like:
    - `GROUP BY`
    - `HAVING`
    - `JOIN`
    - `ORDER BY`
- Execute queries and display results.
- Upload datasets from `.sql` files.
- Delete specific tables or entire schemas.
- Process natural language queries into SQL.

### MongoDB Features
- Generate aggregation pipelines for constructs like:
    - `$group`
    - `$match`
    - `$sort`
    - `$limit`
- Execute queries and display results.
- Upload datasets from `.json` files.
- Delete specific collections or entire databases.
- Process natural language queries into MongoDB pipelines.

## Installation

### Prerequisites
- Python 3.8 or higher
- MySQL server and/or MongoDB server

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repository/chatdb.git
   cd chatdb
   ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Ensure that the nltk data is downloaded:
    ```bash
    import nltk
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('punkt')
    nltk.download('punkt_tab')
    ```
## Usage

1. Run the ChatDB application:
   ```bash
   python ChatDB_query.py
   ```
2. Follow the on-screen instructions to:
- Connect to a Database:
  - For MySQL, provide the host, username, and password to connect.
  - For MongoDB, provide the connection string and database name.
- Explore Schema:
  - View tables and their columns for MySQL.
  - View collections and their fields for MongoDB.
- Upload Datasets:
  - Upload .sql files for MySQL or .json files for MongoDB.
- Delete Data:
  - Drop specific tables/collections or entire databases.
- Generate Queries:
  - Create and execute sample queries with constructs like GROUP BY, $group, ORDER BY, $sort, etc.
- Use Natural Language:
  - Enter natural language queries like "Find total sales grouped by product" to generate SQL or MongoDB queries automatically.
## Datasets used for testing
- MySQL: MySQL Example datasets: https://dev.mysql.com/doc/index-other.html
  - Sakila database on MySQL Example datasets
  - World database on MySQL Example datasets
  - Students and enrollments datasets from Hw3
- MongoDB: Sample datasets from MongoDB cloud:
  - Sample_airbnb
  - Sample_restaurants
  - Students and enrollments datasets from Hw3(transformed to .json format)