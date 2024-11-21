# ChatDB Project

This project provides a command-line interface for interacting with MySQL and MongoDB databases. It supports querying, database exploration, and connection handling.

## Prerequisites

- Python 3.8 or higher
- `pip` package manager
- Installed MySQL and/or MongoDB servers

## Setup Instructions

### 1. **Clone the Repository**
Clone the project repository to your local machine:
```bash
git clone <repository-url>
cd <repository-folder>
```

### **2. Activate a Virtual Environment**

```bash
python -m venv .venv
.venv\Scripts\activate (Windows)
```
### **3. Install Dependencies**
Install the required libraries by running:

```bash
pip install -r requirements.txt
```

### **4. How to Execute the Code**

#### 1. Run the Main Script
   To execute the main script, use the following command:

```bash
python ChatDB_query.py
```
### 2. Interactive Menu
   Once the script starts, follow the interactive prompts:

* Select the database type (MySQL or MongoDB).
* Provide the necessary credentials (e.g., host, username, password, MongoDB connection string).
* Explore the tables, collections, or generate sample queries.

### **5. Functionalities**
#### MySQL
* Show Tables and Columns: View all tables in the current schema and their columns.
* Upload Dataset: Upload .sql files to the connected MySQL database for creating or populating tables.
* Delete Dataset: Drop specific tables or the entire schema.
* Switch Schema: After dropping a schema, select another existing schema or create a new one.
* Generate Sample Queries: Create basic and advanced queries based on available tables.
#### MongoDB
* Show Collections and Fields: List all collections in the current database and explore their field structures.
* Upload Dataset: Insert .json files into the connected MongoDB database as collections.
* Delete Dataset: Drop specific collections or the entire database.
* Switch Database: After dropping a database, choose an existing one or create a new database.
* Generate Sample Queries: Generate MongoDB aggregation pipelines and queries based on collections.