import mysql.connector
from pymongo import MongoClient
import random
import pandas as pd


# Function to connect to MySQL
def connect_mysql():
    host = input("Enter MySQL host (default: 'localhost'): ") or "localhost"
    user = input("Enter MySQL username: ")
    password = input("Enter MySQL password: ")
    database = input("Enter MySQL database name: ")

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        print("MySQL connection successful!")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


# Function to show available tables and columns in MySQL
def show_mysql_tables_and_columns(connection):
    if connection is None:
        print("MySQL connection is not available.")
        return

    cursor = connection.cursor()

    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    if not tables:
        print("No tables found in the MySQL database.")
        return

    print("Available MySQL Tables:")
    for table in tables:
        print(f"Table: {table[0]}")

        cursor.execute(f"SHOW COLUMNS FROM {table[0]};")
        columns = cursor.fetchall()

        print("Columns:")
        for column in columns:
            print(f" - {column[0]} ({column[1]})")
        print("\n")


def connect_mongodb():
    connection_string = input("Enter your MongoDB connection string: ")

    try:
        client = MongoClient(connection_string)
        db_name = input("Enter the MongoDB database name: ")
        db = client[db_name]
        print("MongoDB connection successful!")
        return db
    except Exception as e:
        print(f"Error: {e}")
        return None


def show_mongodb_collections_and_fields(db):
    if db is None:
        print("MongoDB connection is not available.")
        return

    # List all collections
    collections = db.list_collection_names()

    if not collections:
        print("No collections found in the MongoDB database.")
        return

    print("Available MongoDB Collections:")
    for collection_name in collections:
        print(f"Collection: {collection_name}")

        # Fetch a sample document to display its fields
        collection = db[collection_name]
        sample_doc = collection.find_one()

        if sample_doc:
            print("Fields:")
            for key, value in sample_doc.items():
                print(f" - {key} ({type(value).__name__})")  # key is field name, type(value).__name__ gives field type
        else:
            print(f" - No documents found in collection '{collection_name}'")

        print("\n")  # Newline after each collection for clarity


# Function to generate bold text (for terminal output)
def bold(text):
    return f"\033[1m{text}\033[0m"


# Function to analyze dataset schema and generate a limited number of sample queries with correct type matching
def generate_mysql_sample_queries(connection, max_queries=3):
    if connection is None:
        print("MySQL connection is not available.")
        return
    cursor = connection.cursor()

    # Show available tables in the database
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    # Check if there are tables in the database
    if not tables:
        print("No tables found in the database.")
        return

    # Show the available tables and let the user select one
    print("Available tables:", [table[0] for table in tables])
    selected_table = input("Enter the table name you want to use (or press Enter to select randomly): ")

    # Select a random table if user input is empty
    if not selected_table:
        selected_table = random.choice(tables)[0]

    print(f"Selected table: {selected_table}")

    # Fetch columns and their types for the selected table
    cursor.execute(f"SHOW COLUMNS FROM {selected_table};")
    columns = cursor.fetchall()

    # Debugging: Check if columns were fetched correctly
    print(f"Fetched columns for table '{selected_table}': {columns}")

    if not columns:
        print(f"No columns found in the table '{selected_table}'.")
        return

    # Extract column names and types
    column_names = [column[0] for column in columns]
    column_types = {column[0]: column[1] for column in columns}

    # Separate columns into categories: numeric, text, date, etc.
    numeric_columns = [col for col, dtype in column_types.items() if "int" in dtype or "float" in dtype]
    text_columns = [col for col, dtype in column_types.items() if "varchar" in dtype or "text" in dtype]
    date_columns = [col for col, dtype in column_types.items() if "date" in dtype or "time" in dtype]

    # Based on column types, generate appropriate query patterns
    query_patterns = []

    if numeric_columns:
        query_patterns.append({
            "title": "Total Sum by Column",
            "instruction": "To calculate the total sum for a numeric column grouped by a text or date column:",
            "query": "SELECT {group_column},\n\tSUM({numeric_column}) AS total_sum\nFROM {table}\nGROUP BY {group_column};"
        })
        query_patterns.append({
            "title": "Average Value by Column",
            "instruction": "To calculate the average value for a numeric column grouped by another column:",
            "query": "SELECT {group_column},\n\tAVG({numeric_column}) AS avg_value\nFROM {table}\nGROUP BY {group_column};"
        })
        query_patterns.append({
            "title": "Maximum Value by Column",
            "instruction": "To find the maximum value for a numeric column grouped by a text or date column:",
            "query": "SELECT {group_column},\n\tMAX({numeric_column}) AS max_value\nFROM {table}\nGROUP BY {group_column};"
        })
        query_patterns.append({
            "title": "Minimum Value by Column",
            "instruction": "To find the minimum value for a numeric column grouped by a text or date column:",
            "query": "SELECT {group_column},\n\tMIN({numeric_column}) AS min_value\nFROM {table}\nGROUP BY {group_column};"
        })
        query_patterns.append({
            "title": "Top 10 Records Ordered by Numeric Column",
            "instruction": "To list the top 10 records ordered by a numeric column:",
            "query": "SELECT *\nFROM {table}\nORDER BY {numeric_column} DESC\nLIMIT 10;"
        })

    if date_columns:
        query_patterns.append({
            "title": "Count Records by Date",
            "instruction": "To count records for each date:",
            "query": "SELECT {date_column},\n\tCOUNT(*) AS record_count\nFROM {table}\nGROUP BY {date_column};"
        })
        query_patterns.append({
            "title": "Filter by Date Range",
            "instruction": "To filter records between two dates:",
            "query": "SELECT *\nFROM {table}\nWHERE {date_column} BETWEEN 'start_date' AND 'end_date';"
        })

    if text_columns:
        query_patterns.append({
            "title": "Filter by Specific Text",
            "instruction": "To list records where a text column matches a specific value:",
            "query": "SELECT *\nFROM {table}\nWHERE {text_column} = 'value';"
        })
        query_patterns.append({
            "title": "Count Grouped by Text Column",
            "instruction": "To count the number of records grouped by a text column:",
            "query": "SELECT {text_column},\n\tCOUNT(*) AS record_count\nFROM {table}\nGROUP BY {text_column};"
        })

    # Choose a limited number of query patterns based on available columns
    if query_patterns:
        selected_queries = random.sample(query_patterns, min(max_queries, len(query_patterns)))
    else:
        print(f"No suitable columns found to generate queries.")
        return

    # Generate and print only the selected sample queries, with numbered list
    for idx, selected_query in enumerate(selected_queries, start=1):
        # Safely handle selection of group_col (only select if text or date columns exist)
        if "numeric_column" in selected_query['query'] and numeric_columns:
            numeric_col = random.choice(numeric_columns)
            if text_columns + date_columns:  # Ensure there are valid group columns
                group_col = random.choice(text_columns + date_columns)
            else:
                group_col = numeric_col  # Fallback to numeric column if no group columns exist
            formatted_query = selected_query['query'].format(table=selected_table, numeric_column=numeric_col,
                                                             group_column=group_col)
        elif "date_column" in selected_query['query'] and date_columns:
            date_col = random.choice(date_columns)
            formatted_query = selected_query['query'].format(table=selected_table, date_column=date_col)
        elif "text_column" in selected_query['query'] and text_columns:
            text_col = random.choice(text_columns)
            formatted_query = selected_query['query'].format(table=selected_table, text_column=text_col)
        else:
            formatted_query = selected_query['query'].format(table=selected_table)

        # Print the formatted query with bold titles, indented SQL queries, and numbered list
        print(f"{idx}. {bold(selected_query['title'])}")
        print(f"{selected_query['instruction']}\n")
        print(f"SQL Query:\n{formatted_query}\n")


# Function to find suitable columns from other tables if the current table doesn't have the required columns
def find_suitable_columns(connection, numeric_required=False):
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        cursor.execute(f"SHOW COLUMNS FROM {table_name};")
        columns = cursor.fetchall()

        column_types = {column[0]: column[1] for column in columns}
        numeric_columns = [col for col, dtype in column_types.items() if "int" in dtype or "float" in dtype]
        text_columns = [col for col, dtype in column_types.items() if "varchar" in dtype or "text" in dtype]
        date_columns = [col for col, dtype in column_types.items() if "date" in dtype or "time" in dtype]

        if numeric_required and numeric_columns:
            return table_name, numeric_columns, text_columns, date_columns
        elif not numeric_required and (text_columns or date_columns):
            return table_name, numeric_columns, text_columns, date_columns

    return None, [], [], []


# Function to generate a MySQL query based on a specific construct, using other tables if necessary
def generate_mysql_construct_queries(connection, construct):
    if connection is None:
        print("MySQL connection is not available.")
        return

    cursor = connection.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    if not tables:
        print("No tables found in the database.")
        return

    # Select one random table to process
    selected_table = random.choice(tables)[0]
    cursor.execute(f"SHOW COLUMNS FROM {selected_table};")
    columns = cursor.fetchall()

    # Extract column names and types
    column_names = [column[0] for column in columns]
    column_types = {column[0]: column[1] for column in columns}

    # Separate numeric columns and text columns
    numeric_columns = [col for col, dtype in column_types.items() if "int" in dtype or "float" in dtype]
    text_columns = [col for col, dtype in column_types.items() if "varchar" in dtype or "text" in dtype]
    date_columns = [col for col, dtype in column_types.items() if "date" in dtype or "time" in dtype]

    # Check if the current table can be used for the specific construct
    if construct == "group by" or construct == "having":
        # For GROUP BY and HAVING, we need numeric columns for aggregation
        if not numeric_columns:
            # If no suitable numeric columns in the current table, find from other tables
            selected_table, numeric_columns, text_columns, date_columns = find_suitable_columns(connection,
                                                                                                numeric_required=True)
            if not numeric_columns:
                print("No suitable numeric columns found in any table.")
                return

    elif construct == "order by":
        # For ORDER BY, text or numeric columns can be used
        if not text_columns and not numeric_columns and not date_columns:
            # If no suitable columns, find from other tables
            selected_table, numeric_columns, text_columns, date_columns = find_suitable_columns(connection,
                                                                                                numeric_required=False)
            if not text_columns and not numeric_columns and not date_columns:
                print("No suitable columns found in any table for ORDER BY.")
                return

    print(f"\nSelected table: {selected_table}")

    # Generate a query based on the construct
    query_pool = []

    if construct == "group by":
        print(f"\nThe GROUP BY clause groups rows that have the same values in specified columns.")
        group_by_col = random.choice(text_columns + date_columns) if text_columns + date_columns else random.choice(
            column_names)
        sum_col = random.choice(numeric_columns)

        query_pool = [
            {
                "title": f"Total {sum_col} by {group_by_col}",
                "query": f"SELECT {group_by_col}, SUM({sum_col}) AS total_{sum_col} FROM {selected_table} GROUP BY {group_by_col};",
                "explanation": f"- GROUP BY {group_by_col}: This groups the data by the '{group_by_col}' column.\n"
                               f"- SUM({sum_col}): This calculates the total sum of '{sum_col}' for each group in '{group_by_col}'."
            },
            {
                "title": f"Count of {group_by_col}",
                "query": f"SELECT {group_by_col}, COUNT(*) AS record_count FROM {selected_table} GROUP BY {group_by_col};",
                "explanation": f"- GROUP BY {group_by_col}: This groups the data by the '{group_by_col}' column.\n"
                               f"- COUNT(*): This counts the number of records for each group in '{group_by_col}'."
            },
            {
                "title": f"Average {sum_col} by {group_by_col}",
                "query": f"SELECT {group_by_col}, AVG({sum_col}) AS avg_{sum_col} FROM {selected_table} GROUP BY {group_by_col};",
                "explanation": f"- GROUP BY {group_by_col}: This groups the data by the '{group_by_col}' column.\n"
                               f"- AVG({sum_col}): This calculates the average value of '{sum_col}' for each group in '{group_by_col}'."
            }
        ]

    elif construct == "having":
        print(f"\nThe HAVING clause filters records after aggregation has been performed with GROUP BY.")
        group_by_col = random.choice(text_columns + date_columns) if text_columns + date_columns else random.choice(
            column_names)
        sum_col = random.choice(numeric_columns)

        query_pool = [
            {
                "title": f"Total {sum_col} by {group_by_col} with HAVING",
                "query": f"SELECT {group_by_col}, SUM({sum_col}) AS total_{sum_col} FROM {selected_table} GROUP BY {group_by_col} HAVING total_{sum_col} > 100;",
                "explanation": f"- GROUP BY {group_by_col}: This groups the data by the '{group_by_col}' column.\n"
                               f"- SUM({sum_col}): This calculates the total sum of '{sum_col}' for each group in '{group_by_col}'.\n"
                               f"- HAVING total_{sum_col} > 100: This filters groups where the total sum is greater than 100."
            },
            {
                "title": f"Average {sum_col} by {group_by_col} with HAVING",
                "query": f"SELECT {group_by_col}, AVG({sum_col}) AS avg_{sum_col} FROM {selected_table} GROUP BY {group_by_col} HAVING avg_{sum_col} > 50;",
                "explanation": f"- GROUP BY {group_by_col}: This groups the data by the '{group_by_col}' column.\n"
                               f"- AVG({sum_col}): This calculates the average value of '{sum_col}' for each group in '{group_by_col}'.\n"
                               f"- HAVING avg_{sum_col} > 50: This filters groups where the average value is greater than 50."
            }
        ]

    elif construct == "order by":
        print(f"\nThe ORDER BY clause is used to sort the result set of a query by one or more columns.")
        order_by_col = random.choice(column_names)

        query_pool = [
            {
                "title": f"Order Records by {order_by_col} (Ascending)",
                "query": f"SELECT * FROM {selected_table} ORDER BY {order_by_col} ASC;",
                "explanation": f"- ORDER BY {order_by_col} ASC: This orders the data in ascending order based on the '{order_by_col}' column."
            },
            {
                "title": f"Order Records by {order_by_col} (Descending)",
                "query": f"SELECT * FROM {selected_table} ORDER BY {order_by_col} DESC;",
                "explanation": f"- ORDER BY {order_by_col} DESC: This orders the data in descending order based on the '{order_by_col}' column."
            }
        ]

    # Output a single randomly selected query from the query pool
    if query_pool:
        selected_query = random.choice(query_pool)
        print(f"1. {bold(selected_query['title'])}")
        print(f"SQL Query:\n{selected_query['query']}\n")
        print("Explanation:")
        print(f"{selected_query['explanation']}\n")


# Function to generate sample queries for MongoDB (using patterns)
def generate_mongodb_sample_queries(db, max_queries=3):
    if db is None:
        print("MongoDB connection is not available.")
        return

    collections = db.list_collection_names()

    if not collections:
        print("No collections found in the MongoDB database.")
        return

    selected_collection = random.choice(collections)
    print(f"Selected collection: {selected_collection}")

    collection = db[selected_collection]
    sample_doc = collection.find_one()

    if not sample_doc:
        print(f"No documents found in the collection '{selected_collection}'.")
        return

    field_names = list(sample_doc.keys())

    # Categorize fields
    numeric_fields = [key for key, value in sample_doc.items() if isinstance(value, (int, float))]
    text_fields = [key for key, value in sample_doc.items() if isinstance(value, str)]
    date_fields = [key for key, value in sample_doc.items() if isinstance(value, dict) and "$date" in value]

    # Predefined query patterns
    query_patterns = []

    if numeric_fields:
        query_patterns.append({
            "title": "Total Sum by Field",
            "instruction": "To calculate the total sum for a numeric field grouped by another field:",
            "query": "db.{collection}.aggregate([{{ $group: {{ _id: '${group_field}', total_sum: {{ $sum: '${numeric_field}' }} }} }}]);"
        })
        query_patterns.append({
            "title": "Average Value by Field",
            "instruction": "To calculate the average value for a numeric field grouped by another field:",
            "query": "db.{collection}.aggregate([{{ $group: {{ _id: '${group_field}', avg_value: {{ $avg: '${numeric_field}' }} }} }}]);"
        })

    if date_fields:
        query_patterns.append({
            "title": "Count Records by Date",
            "instruction": "To count records by a date field:",
            "query": "db.{collection}.aggregate([{{ $group: {{ _id: '${date_field}', record_count: {{ $sum: 1 }} }} }}]);"
        })

    if text_fields:
        query_patterns.append({
            "title": "Filter by Specific Text",
            "instruction": "To list records where a text field matches a specific value:",
            "query": "db.{collection}.find({{ {text_field}: 'value' }});"
        })

    # Randomly select and print sample queries
    selected_queries = random.sample(query_patterns, min(max_queries, len(query_patterns)))

    for idx, selected_query in enumerate(selected_queries, start=1):
        if "numeric_field" in selected_query['query'] and numeric_fields:
            numeric_field = random.choice(numeric_fields)
            group_field = random.choice(text_fields + date_fields) if text_fields + date_fields else numeric_field
            formatted_query = selected_query['query'].format(collection=selected_collection, numeric_field=numeric_field, group_field=group_field)
        elif "date_field" in selected_query['query'] and date_fields:
            date_field = random.choice(date_fields)
            formatted_query = selected_query['query'].format(collection=selected_collection, date_field=date_field)
        elif "text_field" in selected_query['query'] and text_fields:
            text_field = random.choice(text_fields)
            formatted_query = selected_query['query'].format(collection=selected_collection, text_field=text_field)
        else:
            formatted_query = selected_query['query'].format(collection=selected_collection)

        print(f"{idx}. {bold(selected_query['title'])}")
        print(f"{selected_query['instruction']}\n")
        print(f"MongoDB Query:\n{formatted_query}\n")


# Function to generate MongoDB query based on specific constructs, with title, instruction, and explanation
def generate_mongodb_construct_queries(db, construct):
    if db is None:
        print("MongoDB connection is not available.")
        return

    collections = db.list_collection_names()

    if not collections:
        print("No collections found in the MongoDB database.")
        return

    selected_collection = random.choice(collections)
    print(f"Selected collection: {selected_collection}")

    collection = db[selected_collection]
    sample_doc = collection.find_one()

    if not sample_doc:
        print(f"No documents found in the collection '{selected_collection}'.")
        return

    field_names = list(sample_doc.keys())
    numeric_fields = [key for key, value in sample_doc.items() if isinstance(value, (int, float))]
    text_fields = [key for key, value in sample_doc.items() if isinstance(value, str)]
    date_fields = [key for key, value in sample_doc.items() if isinstance(value, dict) and "$date" in value]

    query_pool = []

    if construct.lower() == "group by":
        if numeric_fields and (text_fields or date_fields):
            selected_numeric = random.choice(numeric_fields)
            selected_group = random.choice(text_fields + date_fields)

            query = f"db.{selected_collection}.aggregate([{{ $group: {{ _id: '${selected_group}', total: {{ $sum: '${selected_numeric}' }} }} }}]);"

            query_pool.append({
                "title": f"Total {selected_numeric} by {selected_group}",
                "instruction": "To calculate the total sum for a numeric field grouped by another field:",
                "query": query,
                "explanation": f"- $group by {selected_group}: This groups the data by the '{selected_group}' field.\n"
                               f"- $sum: This calculates the total sum of '{selected_numeric}' for each group."
            })

    elif construct.lower() == "order by":
        if field_names:
            selected_field = random.choice(field_names)

            query_asc = f"db.{selected_collection}.find().sort({{ '{selected_field}': 1 }});"
            query_desc = f"db.{selected_collection}.find().sort({{ '{selected_field}': -1 }});"

            query_pool.append({
                "title": f"Order by {selected_field} (Ascending)",
                "instruction": "To order the documents by a field in ascending order:",
                "query": query_asc,
                "explanation": f"- .sort({{ '{selected_field}': 1 }}): This sorts the data in ascending order based on the '{selected_field}' field."
            })

            query_pool.append({
                "title": f"Order by {selected_field} (Descending)",
                "instruction": "To order the documents by a field in descending order:",
                "query": query_desc,
                "explanation": f"- .sort({{ '{selected_field}': -1 }}): This sorts the data in descending order based on the '{selected_field}' field."
            })

    elif construct.lower() == "filter by":
        if text_fields or numeric_fields:
            selected_field = random.choice(text_fields + numeric_fields)
            query = f"db.{selected_collection}.find({{ '{selected_field}': 'value' }});"

            query_pool.append({
                "title": f"Filter by {selected_field}",
                "instruction": "To filter the documents by a specific field:",
                "query": query,
                "explanation": f"- .find({{ '{selected_field}': 'value' }}): This filters the documents where '{selected_field}' matches 'value'."
            })

    elif construct.lower() == "having":
        if numeric_fields and text_fields:
            selected_numeric = random.choice(numeric_fields)
            selected_group = random.choice(text_fields)

            query = f"db.{selected_collection}.aggregate([{{ $group: {{ _id: '${selected_group}', total: {{ $sum: '${selected_numeric}' }} }} }}, {{ $match: {{ total: {{ $gt: 100 }} }} }}]);"

            query_pool.append({
                "title": f"Total {selected_numeric} by {selected_group} with HAVING",
                "instruction": "To calculate the total sum and filter groups where the sum exceeds 100:",
                "query": query,
                "explanation": f"- $group by {selected_group}: This groups the data by '{selected_group}' and calculates the sum of '{selected_numeric}'.\n"
                               f"- $match: Filters the groups where the total sum is greater than 100."
            })

    elif construct.lower() == "limit":
        query = f"db.{selected_collection}.find().limit(10);"

        query_pool.append({
            "title": f"Limit 10 Records",
            "instruction": "To limit the number of returned documents to 10:",
            "query": query,
            "explanation": "- .limit(10): This limits the number of returned documents to 10."
        })

    elif construct.lower() == "count":
        if text_fields or date_fields:
            selected_field = random.choice(text_fields + date_fields)

            query = f"db.{selected_collection}.aggregate([{{ $group: {{ _id: '${selected_field}', count: {{ $sum: 1 }} }} }}]);"

            query_pool.append({
                "title": f"Count Documents by {selected_field}",
                "instruction": "To count the number of documents grouped by a field:",
                "query": query,
                "explanation": f"- $group by {selected_field}: This groups the documents by '{selected_field}' and counts the total number of documents for each group."
            })

    elif construct.lower() == "sum":
        if numeric_fields:
            selected_field = random.choice(numeric_fields)

            query = f"db.{selected_collection}.aggregate([{{ $group: {{ _id: null, total_sum: {{ $sum: '${selected_field}' }} }} }}]);"

            query_pool.append({
                "title": f"Sum of {selected_field}",
                "instruction": "To calculate the total sum of a numeric field across all documents:",
                "query": query,
                "explanation": f"- $sum: This calculates the total sum of '{selected_field}' across all documents."
            })

    elif construct.lower() == "average":
        if numeric_fields:
            selected_field = random.choice(numeric_fields)

            query = f"db.{selected_collection}.aggregate([{{ $group: {{ _id: null, avg_value: {{ $avg: '${selected_field}' }} }} }}]);"

            query_pool.append({
                "title": f"Average of {selected_field}",
                "instruction": "To calculate the average value of a numeric field across all documents:",
                "query": query,
                "explanation": f"- $avg: This calculates the average value of '{selected_field}' across all documents."
            })

    else:
        print(f"Construct '{construct}' is not supported.")

    # Output a single randomly selected query from the query pool
    if query_pool:
        for idx, selected_query in enumerate(query_pool, start=1):
            print(f"{idx}. {bold(selected_query['title'])}")
            print(f"{selected_query['instruction']}\n")
            print(f"MongoDB Query:\n{selected_query['query']}\n")
            print("Explanation:")
            print(f"{selected_query['explanation']}\n")


# Function for decision-making after generating queries
def query_decision(connection=None, db=None, db_type="MySQL"):
    while True:
        print("\nWhat would you like to do next?")
        print("1. Generate sample queries")
        print("2. Generate queries with specific constructs (e.g., GROUP BY, ORDER BY, etc.)")
        if db_type == "MongoDB":
            print("3. Execute a custom MongoDB query")
        print("0. Exit")

        decision = input("Enter your choice (1/2/3/0): ").strip()

        if decision == "1":
            if db_type == "MySQL":
                if connection:
                    generate_mysql_sample_queries(connection)
                else:
                    print("MySQL connection is not available.")
            elif db_type == "MongoDB":
                if db is not None:  # Explicitly check if db is not None
                    generate_mongodb_sample_queries(db)
                else:
                    print("MongoDB connection is not available.")

        elif decision == "2":
            construct = input("Enter the construct (e.g., GROUP BY, ORDER BY, HAVING): ").strip().upper()
            if db_type == "MySQL":
                if connection:
                    generate_mysql_construct_queries(connection, construct)
                else:
                    print("MySQL connection is not available.")
            elif db_type == "MongoDB":
                if db is not None:  # Explicitly check if db is not None
                    generate_mongodb_construct_queries(db, construct)
                else:
                    print("MongoDB connection is not available.")

        elif decision == "3" and db_type == "MongoDB":
            if db is not None:  # Explicitly check if db is not None
                custom_query = input("Enter your custom MongoDB query (e.g., db.collection.find()): ").strip()
                try:
                    result = db.command(custom_query)
                    print(f"Query Result:\n{result}")
                except Exception as e:
                    print(f"Error executing MongoDB query: {e}")
            else:
                print("MongoDB connection is not available.")

        elif decision == "0":
            print("Exiting the system. Goodbye!")
            exit()

        else:
            print("Invalid choice. Please try again.")

# Main menu for ChatDB
def chatdb_menu():
    while True:
        print("\n--- ChatDB Main Menu ---")
        print("1. Connect to MySQL")
        print("2. Connect to MongoDB")
        print("0. Exit")

        db_type = input("Choose the database to connect (1: MySQL, 2: MongoDB, 0: Exit): ").strip()

        if db_type == "1":
            connection = connect_mysql()
            if connection:
                show_mysql_tables_and_columns(connection)  # Display MySQL tables and columns
                query_decision(connection=connection, db_type="MySQL")
            else:
                print("Failed to connect to MySQL. Please check your credentials.")

        elif db_type == "2":
            db = connect_mongodb()
            if db is not None:  # Explicitly check if db is not None
                show_mongodb_collections_and_fields(db)  # Display MongoDB collections and fields
                query_decision(db=db, db_type="MongoDB")
            else:
                print("Failed to connect to MongoDB. Please check your connection string.")

        elif db_type == "0":
            print("Exiting the system. Goodbye!")
            exit()

        else:
            print("Invalid choice. Please enter '1' for MySQL, '2' for MongoDB, or '0' to exit.")


if __name__ == "__main__":
    chatdb_menu()
