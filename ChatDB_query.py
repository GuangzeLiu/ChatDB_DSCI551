import mysql.connector
from pymongo import MongoClient
import random
import getpass
from difflib import get_close_matches
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Function to connect to MySQL
def connect_mysql():
    host = input("Enter MySQL host (default: 'localhost'): ") or "localhost"
    user = input("Enter MySQL username: ")
    password = getpass.getpass("Enter MySQL password: ")
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

    print("\nAvailable MySQL Tables:")
    for table in tables:
        print(f"Table: {table[0]}")

        cursor.execute(f"SHOW COLUMNS FROM {table[0]};")
        columns = cursor.fetchall()

        print("Columns:")
        for column in columns:
            print(f" - {column[0]} ({column[1]})")
        print("\n")

def connect_mongodb():
    while True:
        try:
            connection_string = input("Enter your MongoDB connection string (or type 'back' to back to main menu) "
                                      "(format: "
                                      "mongodb+srv://<db_username>:<db_password>@cluster0.l0hlw.mongodb.net/): "
                                      "").strip()

            if connection_string.lower() == 'back':
                return None

            client = MongoClient(connection_string)

            db_name = input("Enter the MongoDB database name: ").strip()
            db = client[db_name]

            if not db.list_collection_names():
                print(f"The database '{db_name}' exists but has no collections. Please try again.")
                continue

            print("MongoDB connection successful!")
            return db

        except Exception as e:
            print(f"Error: {e}")
            print("Failed to connect to MongoDB. Please check the connection string and try again.")

def show_mongodb_collections_and_fields(db):
    if db is None:
        print("MongoDB connection is not available.")
        return

    # List all collections
    collections = db.list_collection_names()

    if not collections:
        print("No collections found in the MongoDB database.")
        return

    print("\nAvailable MongoDB Collections:")
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

def generate_mysql_sample_queries(connection, max_queries=2):
    if connection is None:
        print("MySQL connection is not available.")
        return []

    cursor = connection.cursor()

    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    if not tables:
        print("No tables found in the database.")
        return []

    valid_queries = []
    attempts = 0

    while len(valid_queries) < max_queries and attempts < max_queries * 5:  # Limit attempts
        table_name = random.choice(tables)[0]
        cursor.execute(f"SHOW COLUMNS FROM {table_name};")
        columns = cursor.fetchall()

        if not columns:
            continue

        cursor.execute(f"SHOW INDEX FROM {table_name} WHERE Key_name = 'PRIMARY';")
        primary_keys = [index[4] for index in cursor.fetchall()]

        cursor.execute(f"""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = DATABASE() AND REFERENCED_TABLE_NAME IS NOT NULL;
        """)
        foreign_keys = [row[0] for row in cursor.fetchall()]

        id_columns = set(primary_keys + foreign_keys)

        column_types = {col[0]: col[1] for col in columns}
        numeric_columns = [col for col, dtype in column_types.items() if
                           "int" in dtype or "float" in dtype]
        text_columns = [col for col, dtype in column_types.items() if "varchar" in dtype or "text" in dtype]
        numeric_columns = [col for col in numeric_columns if col not in id_columns]


        query_patterns = []

        for numeric_col in numeric_columns:
            for text_col in text_columns:
                query_patterns.append({
                    "title": f"Total {numeric_col} by {text_col}",
                    "query": f"SELECT {text_col}, SUM({numeric_col}) AS total FROM {table_name} GROUP BY {text_col} LIMIT 10;",
                    "description": f"This query calculates the total of {numeric_col} grouped by {text_col}, inspired by the '{table_name}' table."
                })

        for numeric_col in numeric_columns:
            for text_col in text_columns:
                query_patterns.append({
                    "title": f"Filter Groups by {numeric_col} Total",
                    "query": f"SELECT {text_col}, SUM({numeric_col}) AS total FROM {table_name} GROUP BY {text_col} HAVING total > 0 LIMIT 10;",
                    "description": f"This query filters groups where the total {numeric_col} exceeds 0, grouped by {text_col}, inspired by the '{table_name}' table."
                })

        for numeric_col in numeric_columns:
            query_patterns.extend([
                {
                    "title": f"Top 10 Records Ordered by {numeric_col}",
                    "query": f"SELECT * FROM {table_name} ORDER BY {numeric_col} DESC LIMIT 10;",
                    "description": f"This query retrieves the top 10 records ordered by {numeric_col} in descending order, inspired by the '{table_name}' table."
                },
                {
                    "title": f"Bottom 10 Records Ordered by {numeric_col}",
                    "query": f"SELECT * FROM {table_name} ORDER BY {numeric_col} ASC LIMIT 10;",
                    "description": f"This query retrieves the bottom 10 records ordered by {numeric_col} in ascending order, inspired by the '{table_name}' table."
                }
            ])

        for numeric_col in numeric_columns:
            query_patterns.extend([
                {
                    "title": f"Select rows where {numeric_col} > 0",
                    "query": f"SELECT * FROM {table_name} WHERE {numeric_col} > 0 LIMIT 10;",
                    "description": f"This query selects rows where {numeric_col} is greater than 0, inspired by the '{table_name}' table."
                },
                {
                    "title": f"Select rows where {numeric_col} is between two values",
                    "query": f"SELECT * FROM {table_name} WHERE {numeric_col} BETWEEN 0 AND 100 LIMIT 10;",
                    "description": f"This query selects rows where {numeric_col} is between 0 and 100, inspired by the '{table_name}' table."
                }
            ])

        for text_col in text_columns:
            query_patterns.append({
                "title": f"Search for Partial Matches in {text_col}",
                "query": f"SELECT * FROM {table_name} WHERE {text_col} LIKE '%substring%' LIMIT 10;",
                "description": f"This query searches for rows where {text_col} contains the substring 'substring', inspired by the '{table_name}' table."
            })

        if foreign_keys:
            other_table = random.choice([t[0] for t in tables if t[0] != table_name])
            cursor.execute(f"SHOW COLUMNS FROM {other_table};")
            other_columns = cursor.fetchall()
            if other_columns:
                query_patterns.append({
                    "title": f"Join {table_name} with {other_table}",
                    "query": f"SELECT a.*, b.* FROM {table_name} a JOIN {other_table} b ON a.{foreign_keys[0]} = b.{other_columns[0][0]} LIMIT 10;",
                    "description": f"This query joins the '{table_name}' table with the '{other_table}' table using the foreign key {foreign_keys[0]}."
                })

        if query_patterns:
            query_example = random.choice(query_patterns)
            try:
                cursor.execute(query_example["query"])
                result = cursor.fetchall()

                if result:  # Ensure the query returns results
                    valid_queries.append(query_example)
            except Exception as e:
                print(f"Query failed: {query_example['query']}\nError: {e}")
            finally:
                attempts += 1

    if valid_queries:
        return valid_queries
    else:
        print("No meaningful sample queries found or not enough columns to generate queries.")
        return []

def generate_mysql_construct_queries(connection, construct, max_queries=2):
    if connection is None:
        print("MySQL connection is not available.")
        return []

    cursor = connection.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    if not tables:
        print("No tables found in the database.")
        return []

    valid_queries = []
    attempts = 0

    for table in tables:
        table_name = table[0]
        cursor.execute(f"SHOW COLUMNS FROM {table_name};")
        columns = cursor.fetchall()

        column_names = [column[0] for column in columns]
        column_types = {column[0]: column[1] for column in columns}

        cursor.execute(f"SHOW INDEX FROM {table_name} WHERE Key_name = 'PRIMARY';")
        primary_keys = [index[4] for index in cursor.fetchall()]

        cursor.execute(f"""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = DATABASE() AND REFERENCED_TABLE_NAME IS NOT NULL;
            """)
        foreign_keys = [row[0] for row in cursor.fetchall()]

        id_columns = set(primary_keys + foreign_keys)

        column_types = {col[0]: col[1] for col in columns}

        numeric_columns = [col for col, dtype in column_types.items() if "int" in dtype or "float" in dtype]
        text_columns = [col for col, dtype in column_types.items() if "varchar" in dtype or "text" in dtype]
        date_columns = [col for col, dtype in column_types.items() if "date" in dtype or "time" in dtype]

        numeric_columns_for_aggregation = [
            col for col in numeric_columns if col not in id_columns
        ]

        group_by_columns = text_columns + primary_keys

        query_patterns = []
        if construct == "GROUP BY":
            for group_by_col in group_by_columns:
                for numeric_col in numeric_columns_for_aggregation:
                    query_patterns.append({
                        "title": f"Total {numeric_col} by {group_by_col} in {table_name}",
                        "query": f"SELECT {group_by_col}, SUM({numeric_col}) AS total_{numeric_col} FROM {table_name} GROUP BY {group_by_col};",
                        "description": f"This query groups the data by '{group_by_col}' and calculates the total sum "
                                       f"of '{numeric_col}' for each group."
                    })
                for numeric_col in numeric_columns_for_aggregation:
                    query_patterns.append({
                        "title": f"Average {numeric_col} by {group_by_col} in {table_name}",
                        "query": f"SELECT {group_by_col}, AVG({numeric_col}) AS avg_{numeric_col} FROM {table_name} GROUP BY {group_by_col};",
                        "description": f"This query groups the data by '{group_by_col}' and calculates the average value of '{numeric_col}' for each group."
                    })
                query_patterns.append({
                    "title": f"Count of records grouped by {group_by_col} in {table_name}",
                    "query": f"SELECT {group_by_col}, COUNT(*) AS record_count FROM {table_name} GROUP BY {group_by_col};",
                    "description": f"This query groups the data by '{group_by_col}' and counts the number of records in each group."
                })

        elif construct == "HAVING":
            for group_by_col in group_by_columns:
                for numeric_col in numeric_columns_for_aggregation:
                    query_patterns.append({
                        "title": f"Total {numeric_col} by {group_by_col} with HAVING in {table_name}",
                        "query": f"SELECT {group_by_col}, SUM({numeric_col}) AS total_{numeric_col} FROM {table_name} GROUP BY {group_by_col} HAVING total_{numeric_col} > 0;",
                        "description": f"This query groups the data by '{group_by_col}', calculates the total sum of '{numeric_col}', and filters groups where the sum exceeds 0."
                    })
                    query_patterns.append({
                        "title": f"Average {numeric_col} by {group_by_col} with HAVING in {table_name}",
                        "query": f"SELECT {group_by_col}, AVG({numeric_col}) AS avg_{numeric_col} FROM {table_name} GROUP BY {group_by_col} HAVING avg_{numeric_col} > 0;",
                        "description": f"This query groups the data by '{group_by_col}', calculates the average value of '{numeric_col}', and filters groups where the average exceeds 0."
                    })
                query_patterns.append({
                    "title": f"Count of records grouped by {group_by_col} with HAVING in {table_name}",
                    "query": f"SELECT {group_by_col}, COUNT(*) AS record_count FROM {table_name} GROUP BY {group_by_col} HAVING record_count > 1;",
                    "description": f"This query groups the data by '{group_by_col}', counts the number of records in each group, and filters groups where the count exceeds 1."
                })


        elif construct == "JOIN":
            for other_table in tables:
                other_table_name = other_table[0]
                if other_table_name != table_name:
                    cursor.execute(f"SHOW COLUMNS FROM {other_table_name};")
                    other_columns = [col[0] for col in cursor.fetchall()]
                    if primary_keys and other_columns:
                        query_patterns.append({
                            "title": f"Join {table_name} with {other_table_name}",
                            "query": f"SELECT a.*, b.* FROM {table_name} a JOIN {other_table_name} b ON a.{primary_keys[0]} = b.{other_columns[0]} LIMIT 10;",
                            "description": f"This query joins '{table_name}' with '{other_table_name}' on the key '{primary_keys[0]}'."
                        })

        elif construct == "EXISTS":
            for col in text_columns:
                query_patterns.append({
                    "title": f"Select records if EXISTS in {table_name}",
                    "query": f"SELECT * FROM {table_name} t1 WHERE EXISTS (SELECT 1 FROM {table_name} t2 WHERE t1.{col} = t2.{col});",
                    "description": f"This query checks if a record exists in '{table_name}' where '{col}' matches."
                })

        elif construct == "ORDER BY":
            for col in numeric_columns + text_columns + date_columns:
                query_patterns.append({
                    "title": f"Order records by {col} ascending in {table_name}",
                    "query": f"SELECT * FROM {table_name} ORDER BY {col} ASC;",
                    "description": f"This query orders the data in ascending order based on the column '{col}'."
                })
                query_patterns.append({
                    "title": f"Order records by {col} descending in {table_name}",
                    "query": f"SELECT * FROM {table_name} ORDER BY {col} DESC;",
                    "description": f"This query orders the data in descending order based on the column '{col}'."
                })

    while len(valid_queries) < max_queries and attempts < max_queries * 5:
        if not query_patterns:
            break
        query_example = random.choice(query_patterns)
        try:
            cursor.execute(query_example["query"])
            result = cursor.fetchall()

            if result:
                valid_queries.append(query_example)
                query_patterns.remove(query_example)
        except Exception as e:
            print(f"Query validation failed: {query_example['query']}\nError: {e}")
        finally:
            attempts += 1

    if valid_queries:
        return valid_queries
    else:
        print("No meaningful sample queries found or not enough columns to generate queries.")
        return []

def generate_mongodb_sample_queries(db, max_queries=1):

    if db is None:
        print("MongoDB connection is not available.")
        return []

    collections = db.list_collection_names()

    if not collections:
        print("No collections found in the MongoDB database.")
        return []

    valid_queries = []

    for collection_name in collections:
        collection = db[collection_name]
        sample_doc = collection.find_one()
        if not sample_doc:
            print(f"Collection '{collection_name}' is empty. Skipping.")
            continue

        numeric_fields = [key for key, value in sample_doc.items() if isinstance(value, (int, float))]
        text_fields = [key for key, value in sample_doc.items() if isinstance(value, str)]
        date_fields = [key for key, value in sample_doc.items() if isinstance(value, dict) and "$date" in value]

        query_patterns = []

        # Aggregation Queries
        if numeric_fields and (text_fields or date_fields):
            for numeric_field in numeric_fields:
                for group_field in text_fields + date_fields:
                    query_patterns.append({
                        "title": f"Total {numeric_field} grouped by {group_field} in {collection_name}",
                        "query": [
                            {"$group": {"_id": f"${group_field}", "total": {"$sum": f"${numeric_field}"}}}
                        ],
                        "description": f"Groups documents by '{group_field}' and calculates the total of '{numeric_field}'.",
                        "type": "aggregate",
                        "collection": collection_name
                    })
                    query_patterns.append({
                        "title": f"Average {numeric_field} grouped by {group_field} in {collection_name}",
                        "query": [
                            {"$group": {"_id": f"${group_field}", "avg": {"$avg": f"${numeric_field}"}}}
                        ],
                        "description": f"Groups documents by '{group_field}' and calculates the average of '{numeric_field}'.",
                        "type": "aggregate",
                        "collection": collection_name
                    })

        # Text Search Queries
        for text_field in text_fields:
            query_patterns.append({
                "title": f"Find documents where {text_field} contains 'sample' (case-insensitive) in {collection_name}",
                "query": {text_field: {"$regex": "sample", "$options": "i"}},
                "description": f"Finds documents where the field '{text_field}' contains the substring 'sample' (case-insensitive).",
                "type": "find",
                "collection": collection_name
            })

            query_patterns.append({
                "title": f"Find documents where {text_field} is exactly 'example' in {collection_name}",
                "query": {text_field: "example"},
                "description": f"Finds documents where the field '{text_field}' is exactly 'example'.",
                "type": "find",
                "collection": collection_name
            })

            query_patterns.append({
                "title": f"Count occurrences of unique values in {text_field} in {collection_name}",
                "query": [
                    {"$group": {"_id": f"${text_field}", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ],
                "description": f"Counts the occurrences of each unique value in the field '{text_field}', sorted in descending order.",
                "type": "aggregate",
                "collection": collection_name
            })

        # Sorting Queries
        for field in numeric_fields + text_fields + date_fields:
            query_patterns.extend([
                {
                    "title": f"Sort documents by {field} in ascending order in {collection_name}",
                    "query": {"sort": {field: 1}},
                    "description": f"Sorts documents in ascending order by '{field}'.",
                    "type": "find",
                    "collection": collection_name
                },
                {
                    "title": f"Sort documents by {field} in descending order in {collection_name}",
                    "query": {"sort": {field: -1}},
                    "description": f"Sorts documents in descending order by '{field}'.",
                    "type": "find",
                    "collection": collection_name
                }
            ])

        # Randomly select a limited number of patterns
        if query_patterns:
            selected_queries = random.sample(query_patterns, min(max_queries, len(query_patterns)))

            # Validate the queries
            for query in selected_queries:
                try:
                    if query["type"] == "aggregate":
                        collection.aggregate(query["query"])
                    elif query["type"] == "find":
                        collection.find(query["query"])
                    valid_queries.append(query)
                except Exception as e:
                    print(f"Query validation failed for collection '{collection_name}': {query['title']}")
                    print(f"Error: {e}")

    return valid_queries

def generate_mongodb_construct_queries(db, construct, max_queries=2):
    if db is None:
        print("MongoDB connection is not available.")
        return []

    collections = db.list_collection_names()

    if not collections:
        print("No collections found in the MongoDB database.")
        return []

    valid_queries = []

    for collection_name in collections:
        collection = db[collection_name]
        sample_doc = collection.find_one()
        if not sample_doc:
            print(f"Collection '{collection_name}' is empty. Skipping.")
            continue

        numeric_fields = [key for key, value in sample_doc.items() if isinstance(value, (int, float))]
        text_fields = [key for key, value in sample_doc.items() if isinstance(value, str)]
        date_fields = [key for key, value in sample_doc.items() if isinstance(value, dict) and "$date" in value]

        query_patterns = []

        # Handle MATCH
        if construct == "$match":
            # Match numeric fields
            for numeric_field in numeric_fields:
                query_patterns.append({
                    "title": f"Filter documents where {numeric_field} > 10 in {collection_name}",
                    "query": [{ "$match": { numeric_field: { "$gt": 10 } } }],
                    "description": f"Filters documents where the field '{numeric_field}' is greater than 10 using the MATCH stage.",
                    "type": "aggregate",
                    "collection": collection_name
                })
                query_patterns.append({
                    "title": f"Filter documents where {numeric_field} is exactly 5 in {collection_name}",
                    "query": [{ "$match": { numeric_field: 5 } }],
                    "description": f"Filters documents where the field '{numeric_field}' is exactly 5 using the MATCH stage.",
                    "type": "aggregate",
                    "collection": collection_name
                })

            # Match text fields
            for text_field in text_fields:
                query_patterns.append({
                    "title": f"Find documents where {text_field} contains 'sample' (case-insensitive) in {collection_name}",
                    "query": [{ "$match": { text_field: {"$regex": "sample", "$options": "i"} } }],
                    "description": f"Finds documents where the field '{text_field}' contains the substring 'sample' (case-insensitive) using the MATCH stage.",
                    "type": "aggregate",
                    "collection": collection_name
                })
                query_patterns.append({
                    "title": f"Find documents where {text_field} starts with 'example' (case-sensitive) in {collection_name}",
                    "query": [{ "$match": { text_field: {"$regex": "^example"} } }],
                    "description": f"Finds documents where the field '{text_field}' starts with 'example' (case-sensitive) using the MATCH stage.",
                    "type": "aggregate",
                    "collection": collection_name
                })
                query_patterns.append({
                    "title": f"Find documents where {text_field} is exactly 'example' in {collection_name}",
                    "query": [{ "$match": { text_field: "example" } }],
                    "description": f"Finds documents where the field '{text_field}' is exactly 'example' using the MATCH stage.",
                    "type": "aggregate",
                    "collection": collection_name
                })

        # Handle GROUP
        if construct == "$group":
            for numeric_field in numeric_fields:
                for group_field in text_fields:
                    query_patterns.append({
                        "title": f"Group by {group_field} and calculate total {numeric_field} in {collection_name}",
                        "query": [{ "$group": { "_id": f"${group_field}", "total": { "$sum": f"${numeric_field}" } } }],
                        "description": f"Groups documents by '{group_field}' and calculates the total of '{numeric_field}' using the GROUP stage.",
                        "type": "aggregate",
                        "collection": collection_name
                    })
                    query_patterns.append({
                        "title": f"Group by {group_field} and calculate average {numeric_field} in {collection_name}",
                        "query": [{ "$group": { "_id": f"${group_field}", "average": { "$avg": f"${numeric_field}" } } }],
                        "description": f"Groups documents by '{group_field}' and calculates the average of '{numeric_field}' using the GROUP stage.",
                        "type": "aggregate",
                        "collection": collection_name
                    })

            # Count documents grouped by text fields
            for group_field in text_fields:
                query_patterns.append({
                    "title": f"Group by {group_field} and count documents in {collection_name}",
                    "query": [{ "$group": { "_id": f"${group_field}", "count": { "$sum": 1 } } }],
                    "description": f"Groups documents by '{group_field}' and counts the number of documents in each group using the GROUP stage.",
                    "type": "aggregate",
                    "collection": collection_name
                })

            # Calculate maximum and minimum values for numeric fields
            for numeric_field in numeric_fields:
                for group_field in text_fields:
                    query_patterns.append({
                        "title": f"Group by {group_field} and find maximum {numeric_field} in {collection_name}",
                        "query": [{ "$group": { "_id": f"${group_field}", "maxValue": { "$max": f"${numeric_field}" } } }],
                        "description": f"Groups documents by '{group_field}' and finds the maximum value of '{numeric_field}' using the GROUP stage.",
                        "type": "aggregate",
                        "collection": collection_name
                    })
                    query_patterns.append({
                        "title": f"Group by {group_field} and find minimum {numeric_field} in {collection_name}",
                        "query": [{ "$group": { "_id": f"${group_field}", "minValue": { "$min": f"${numeric_field}" } } }],
                        "description": f"Groups documents by '{group_field}' and finds the minimum value of '{numeric_field}' using the GROUP stage.",
                        "type": "aggregate",
                        "collection": collection_name
                    })

        # Handle SORT
        if construct == "$sort":
            for field in numeric_fields + text_fields + date_fields:
                query_patterns.extend([
                    {
                        "title": f"Sort documents by {field} in ascending order in {collection_name}",
                        "query": {"sort": {field: 1}},
                        "description": f"Sorts documents in ascending order by '{field}'.",
                        "type": "find",
                        "collection": collection_name
                    },
                    {
                        "title": f"Sort documents by {field} in descending order in {collection_name}",
                        "query": {"sort": {field: -1}},
                        "description": f"Sorts documents in descending order by '{field}'.",
                        "type": "find",
                        "collection": collection_name
                    }
                ])

        # Handle LIMIT
        if construct == "$limit":
            query_patterns.append({
                "title": f"Limit results to 10 documents in {collection_name}",
                "query": [{ "$limit": 10 }],
                "description": f"Limits the number of documents returned to 10 using the LIMIT stage.",
                "type": "aggregate",
                "collection": collection_name
            })
            # Example: Limit to 5 documents
            query_patterns.append({
                "title": f"Limit results to 5 documents in {collection_name}",
                "query": [{ "$limit": 5 }],
                "description": f"Limits the number of documents returned to 5 using the LIMIT stage.",
                "type": "aggregate",
                "collection": collection_name
            })

            # Example: Combine with $sort (descending order by _id)
            query_patterns.append({
                "title": f"Sort by _id in descending order and limit to 3 documents in {collection_name}",
                "query": [{ "$sort": { "_id": -1 } }, { "$limit": 3 }],
                "description": f"Sorts documents by '_id' in descending order and limits the results to 3 documents using the LIMIT stage.",
                "type": "aggregate",
                "collection": collection_name
            })

            # Example: Combine with $skip and $limit (pagination)
            query_patterns.append({
                "title": f"Skip the first 5 documents and limit to 5 documents in {collection_name}",
                "query": [{ "$skip": 5 }, { "$limit": 5 }],
                "description": f"Skips the first 5 documents and then limits the results to 5 documents, useful for pagination, using the LIMIT stage.",
                "type": "aggregate",
                "collection": collection_name
            })

            # Example: Complex pipeline with $match, $sort, and $limit
            if numeric_fields:
                query_patterns.append({
                    "title": f"Filter by a numeric field, sort, and limit results to 2 documents in {collection_name}",
                    "query": [
                        { "$match": { numeric_fields[0]: { "$gt": 0 } } },
                        { "$sort": { numeric_fields[0]: -1 } },
                        { "$limit": 2 }
                    ],
                    "description": f"Filters documents where '{numeric_fields[0]}' is greater than 0, sorts them in descending order, and limits the results to 2 documents.",
                    "type": "aggregate",
                    "collection": collection_name
                })

        # Append queries for the current collection to the overall results
        valid_queries.extend(query_patterns)

    # Randomly select up to `max_queries` queries
    return random.sample(valid_queries, min(max_queries, len(valid_queries)))

def upload_dataset_to_database(connection=None, db=None, db_type="MySQL"):
    """
    Upload a dataset into the connected database and display the updated tables or collections.
    """
    file_path = input("Enter the full path (.sql or.json) to the dataset file: ").strip()

    try:
        if db_type == "MySQL" and connection:
            # Allow user to specify a new database name
            cursor = connection.cursor()
            new_db_name = input("Enter the name of the database to use or create (leave empty to use the current database): ").strip()

            if new_db_name:
                # Create database if it does not exist
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {new_db_name};")
                print(f"Database '{new_db_name}' is ready.")
                # Switch to the new database
                cursor.execute(f"USE {new_db_name};")
                print(f"Switched to database '{new_db_name}'.")
            else:
                print(f"Using the currently connected database '{connection.database}'.")

            if file_path.endswith('.sql'):
                # Execute SQL script
                with open(file_path, 'r') as file:
                    sql_script = file.read()
                for statement in sql_script.split(';'):
                    if statement.strip():  # Skip empty statements
                        cursor.execute(statement)
                connection.commit()
                print("SQL file executed successfully. Dataset uploaded to MySQL database.")

                # Display updated tables
                cursor.execute("SHOW TABLES;")
                tables = cursor.fetchall()
                if tables:
                    print("Available Tables:")
                    for table in tables:
                        print(f" - {table[0]}")
                else:
                    print("No tables found in the database.")
            else:
                print("Invalid file format for MySQL. Please provide a .sql file.")

        elif db_type == "MongoDB" and db is not None:
            if file_path.endswith('.json'):
                # Insert JSON data
                import json
                with open(file_path, 'r') as file:
                    data = json.load(file)
                collection_name = input("Enter the collection name to insert data: ").strip()
                collection = db[collection_name]
                if isinstance(data, list):
                    collection.insert_many(data)
                else:
                    collection.insert_one(data)
                print(f"JSON file inserted successfully into '{collection_name}' collection.")

                # Display updated collections
                collections = db.list_collection_names()
                if collections:
                    print("Available Collections:")
                    for collection in collections:
                        print(f" - {collection}")
                else:
                    print("No collections found in the database.")
            else:
                print("Invalid file format for MongoDB. Please provide a .json file.")
        else:
            print("Invalid database type or no active connection.")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error uploading dataset: {e}")

def drop_tables_or_schema(connection=None, db=None, db_type="MySQL"):
    """
    Drop specific tables or the entire schema (MySQL) or collections or the entire database (MongoDB),
    and allow users to choose a new schema/database if the current one is dropped.
    """
    try:
        if db_type == "MySQL" and connection:
            cursor = connection.cursor()

            # Get the currently connected database name
            current_db = connection.database
            if not current_db:
                print("No database is currently selected.")
                return

            print("\nWhat would you like to drop?")
            print("1. Drop specific tables")
            print("2. Drop the entire schema")
            choice = input("Enter your choice (1/2): ").strip()

            if choice == "1":
                # Show available tables
                cursor.execute("SHOW TABLES;")
                tables = cursor.fetchall()
                if not tables:
                    print("No tables found in the database.")
                    return

                print("Available Tables:")
                for table in tables:
                    print(f" - {table[0]}")

                # Prompt user to enter table names to drop
                table_names = input("Enter the names of the tables to drop (comma-separated): ").strip()
                tables_to_drop = [t.strip() for t in table_names.split(",")]

                confirm = input(f"Are you sure you want to drop the following tables: {', '.join(tables_to_drop)}? This action cannot be undone. (yes/no): ").strip().lower()

                if confirm == "yes":
                    for table in tables_to_drop:
                        cursor.execute(f"DROP TABLE {table};")
                    connection.commit()
                    print(f"Tables '{', '.join(tables_to_drop)}' have been dropped successfully.")
                else:
                    print("Drop operation cancelled.")

            elif choice == "2":
                # Confirm the drop operation for the entire schema
                confirm = input(f"Are you sure you want to drop the entire schema '{current_db}'? This action cannot be undone. (yes/no): ").strip().lower()

                if confirm == "yes":
                    cursor.execute(f"DROP DATABASE {current_db};")
                    print(f"Schema '{current_db}' has been dropped successfully.")

                    # Show all available schemas and allow the user to choose a new one
                    cursor.execute("SHOW DATABASES;")
                    schemas = cursor.fetchall()
                    print("Available Schemas:")
                    for schema in schemas:
                        print(f" - {schema[0]}")

                    new_schema = input("Enter the name of a new schema to use, or leave empty to exit the current database context: ").strip()

                    if new_schema:
                        try:
                            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {new_schema};")
                            cursor.execute(f"USE {new_schema};")
                            print(f"Switched to new schema '{new_schema}'.")
                        except Exception as e:
                            print(f"Error switching to new schema '{new_schema}': {e}")
                    else:
                        print("No new schema selected. You are now outside any schema context.")
                        chatdb_menu()
                else:
                    print("Drop operation cancelled.")
            else:
                print("Invalid choice. Please select 1 or 2.")

        elif db_type == "MongoDB" and db is not None:
            print("\nWhat would you like to drop?")
            print("1. Drop specific collections")
            print("2. Drop the entire database")
            choice = input("Enter your choice (1/2): ").strip()

            if choice == "1":
                # Show available collections
                collections = db.list_collection_names()
                if not collections:
                    print("No collections found in the database.")
                    return

                print("Available Collections:")
                for collection in collections:
                    print(f" - {collection}")

                # Prompt user to enter collection names to drop
                collection_names = input("Enter the names of the collections to drop (comma-separated): ").strip()
                collections_to_drop = [c.strip() for c in collection_names.split(",")]

                confirm = input(f"Are you sure you want to drop the following collections: {', '.join(collections_to_drop)}? This action cannot be undone. (yes/no): ").strip().lower()

                if confirm == "yes":
                    for collection in collections_to_drop:
                        db[collection].drop()
                    print(f"Collections '{', '.join(collections_to_drop)}' have been dropped successfully.")
                else:
                    print("Drop operation cancelled.")

            elif choice == "2":
                # Confirm the drop operation for the entire database
                current_db_name = db.name
                confirm = input(f"Are you sure you want to drop the entire database '{current_db_name}'? This action cannot be undone. (yes/no): ").strip().lower()

                if confirm == "yes":
                    client = db.client  # Get the client to drop the database
                    client.drop_database(current_db_name)
                    print(f"Database '{current_db_name}' has been dropped successfully.")

                    # Return to main menu after dropping the database
                    print("Returning to the main menu.")
                    chatdb_menu()  # Call main menu
                else:
                    print("Drop operation cancelled.")
            else:
                print("Invalid choice. Please select 1 or 2.")

        else:
            print("Invalid database type or no active connection.")
    except Exception as e:
        print(f"Error dropping tables or schema/database: {e}")

def get_table_schema(connection):
    """
    Fetch table schema information dynamically from the database.
    """
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    schema = {}
    for (table,) in tables:
        cursor.execute(f"SHOW COLUMNS FROM {table};")
        columns = cursor.fetchall()
        schema[table] = [column[0].lower() for column in columns]
    return schema

def map_field_to_column(user_field, schema):
    """
    Map user-provided field names to actual database columns using schema.
    Leverage NLTK for tokenization, lemmatization, and normalization.
    """

    # Initialize NLTK tools
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))

    # Normalize user field (tokenize, lemmatize, and remove stopwords)
    def normalize(text):
        tokens = word_tokenize(text.lower())  # Tokenize and lowercase
        tokens = [lemmatizer.lemmatize(token) for token in tokens]  # Lemmatize
        tokens = [token for token in tokens if token not in stop_words]  # Remove stopwords
        return "".join(tokens)  # Join tokens to form a normalized string
    # Normalize schema columns
    field_mapping = {}
    for table, columns in schema.items():
        for column in columns:
            normalized_column = normalize(column)
            field_mapping[normalized_column] = column  # Map normalized column to the original

    # Normalize user input
    user_field_normalized = normalize(user_field)

    # Attempt to find the closest match
    match = get_close_matches(user_field_normalized, field_mapping.keys(), n=1, cutoff=0.6)
    
    if match:
        mapped_field = field_mapping[match[0]]
        return mapped_field

    print(f"Failed to map field '{user_field}'.")
    return user_field

def find_table_for_columns(columns, schema):
   
    for table, table_columns in schema.items():
       
        if all(column in table_columns for column in columns):
          
            return table

    return None

sql_patterns = [
    {
        "pattern": r"\b(count|number of|how many)\b\s+([\w\s]+)\s+(group by|by|categorized by|organized by)\s+(\w+)(?:\s+having\s+([\w\s<>!=\'\"]+))?",
        "description": "Counts occurrences of '<field>' grouped by '<group_field>' with optional 'HAVING' clause.",
        "query_template": "SELECT {group_by}, COUNT({total_field}) AS total FROM {table} GROUP BY {group_by} {having_clause};"
    },
    {
        "pattern": r"\b(sum|add up|aggregate|total)\b\s+([\w\s]+)\s+(groupby|by|group by|categorized by|organized by)\s+(\w+)(?:\s+having\s+([\w\s<>!=().]+))?",
        "description": "Calculates the sum of '<field>' grouped by '<group_field>' with optional 'HAVING' clause.",
        "query_template": "SELECT {group_by}, SUM({sum_field}) AS total_sum FROM {table} GROUP BY {group_by} {having_clause};"
    },
    {
        "pattern": r"\b(average|avg|mean|compute average)\s+([\w\s]+)\s+(groupby|by|group by|categorized by|organized by)\s+(\w+)(?:\s+having\s+(.+))?",
        "description": "Calculates the average of '<field>' grouped by '<group_field>' with optional 'HAVING' clause.",
        "query_template": "SELECT {group_by}, AVG({avg_field}) AS average FROM {table} GROUP BY {group_by} {having_clause};"
    },
    
   {
    "pattern": r"\b(select|filter|find)\b\s+([\w\s]+)\s+(group by|groupby|by)\s+([\w\s]+)\s+where\s+(.+)",
    "description": "Selects rows from '<table>' where '<condition>' grouped by '<group_field>'.",
    "query_template": "SELECT * FROM {table} {where_clause} GROUP BY {group_by};"
}





]

def process_natural_language_query_mysql(user_query, connection=None, db_type="MySQL"):
    """
    Process the natural language query and map it to a SQL query, with support for HAVING, WHERE, and comparison operators.
    """
    import re

    user_query = user_query.replace("group by", "by")
    # Fetch schema dynamically if MySQL
    if connection and db_type == "MySQL":
        schema = get_table_schema(connection)
    else:
        schema = {}

    for pattern in sql_patterns:
        match = re.search(pattern["pattern"], user_query, re.IGNORECASE)
        if match:
            groups = match.groups()
            print(f"Matched groups: {groups}")
            operation = groups[0]  # Extract operation (e.g., "count", "sum")
            field = groups[1]  # Extract target field
            group_by = groups[3] if len(groups) > 3 else None  # Extract group by field
            if len(groups) > 4 and groups[4]:
                condition = groups[4].strip()
              
            else:
                condition = None
                print("Condition not captured.")

           
            # Map fields to schema columns
            field_mapped = clean_and_map_field(field, schema)
            group_by_mapped = clean_and_map_field(group_by, schema) if group_by else None

            total_field_mapped = map_field_to_column(field_mapped, schema)
            group_by_mapped = map_field_to_column(group_by_mapped, schema)

            # Identify the table that contains the fields
            table = find_table_for_columns([total_field_mapped] + ([group_by_mapped] if group_by else []), schema)
            if not table:
                print(f"Error: Could not find a table containing the fields '{field}' and '{group_by}'.")
                return None

            # Determine the placeholder dynamically based on the operation
            field_placeholder = (
                "avg_field" if operation.lower() in ["average", "avg", "mean", "compute average"] else
                "sum_field" if operation.lower() in ["sum", "add up", "aggregate", "total"] else
                "total_field"
            )
            if condition and "having" in user_query.lower():
                if "sum_field" in field_placeholder:
                    condition = condition.replace(total_field_mapped, "total_sum")
                elif "avg_field" in field_placeholder:
                    condition = condition.replace(total_field_mapped, "average")
                having_clause = f"HAVING {condition}"
            else:
                having_clause = ""

            if condition and "where" in user_query.lower():
                where_clause = f"WHERE {condition}"
            else:
                where_clause = ""

            # Ensure there is no duplicate WHERE
            if where_clause.startswith("WHERE WHERE"):
                where_clause = where_clause.replace("WHERE WHERE", "WHERE")

            print(f"Condition: {condition}, Having Clause: {having_clause}, Where Clause: {where_clause}")
        
            # Construct the query dynamically
            try:
                query = pattern["query_template"].format(
                    **{
                        field_placeholder: total_field_mapped,
                        "group_by": group_by_mapped,
                        "table": table, 
                        "having_clause": having_clause,
                        "where_clause": where_clause
                    }
                )
            except KeyError as e:
                print(f"Error: Missing placeholder in the query template: {e}")
                return None

            # Dynamically update the description
            description = pattern["description"].replace("<field>", field).replace("<group_field>", group_by)

            return {
                "description": description,
                "query": query
            }

    print("No matching query pattern found for the given natural language query.")
    return None

def clean_field(field):
    
   
    cleaned_field = re.sub(r"\b(grouped|group by|from|where|having|select|order|as|into)\b", "", field, flags=re.IGNORECASE).strip()
   
    return cleaned_field.strip()
def generate_join_query(columns, schema):
   
    tables_with_columns = {table: [col for col in columns if col in table_columns] 
                           for table, table_columns in schema.items()}
    involved_tables = [table for table, cols in tables_with_columns.items() if cols]
    if len(involved_tables) > 1:
        
        join_query = f"SELECT {columns[0]}, COUNT({columns[1]}) FROM {involved_tables[0]} "
        join_query += f"INNER JOIN {involved_tables[1]} ON {involved_tables[0]}.key = {involved_tables[1]}.key "
        join_query += f"GROUP BY {columns[0]}"
        return join_query
    return None
def clean_and_map_field(field, schema):
   
    cleaned_field = clean_field(field)  
    mapped_field = map_field_to_column(cleaned_field, schema) 
    return mapped_field

def mongo_get_collection_schema(db):

    """
    Fetch schema information dynamically from MongoDB collections.
    """
    schema = {}
    collections = db.list_collection_names()
    for collection_name in collections:
        collection = db[collection_name]
        sample_doc = collection.find_one()
        if sample_doc:
            schema[collection_name] = list(sample_doc.keys())  # Collect field names from a sample document
    return schema
def mongo_find_collection_for_fields(fields, schema):
    """
    Find a MongoDB collection containing all specified fields.
    """
    for collection, collection_fields in schema.items():
        if all(field in collection_fields for field in fields):
            return collection
    return None
mongo_patterns = [
    {
        "pattern": r"\b(count|number of|how many)\b\s+([\w\s]+)\s+(group by|by|categorized by|organized by)\s+(\w+)(?:\s+having\s+([\w\s<>!=().]+))?",
        "description": "Counts occurrences of '<field>' grouped by '<group_field>' with optional 'HAVING' clause.",
        "query_template": [
            {"$group": {"_id": "${group_by}", "count": {"$sum": 1}}},
            {"$match": {}}
        ]
    },
    {
        "pattern": r"\b(sum|add up|aggregate|total)\b\s+([\w\s]+)\s+(groupby|by|group by|categorized by|organized by)\s+(\w+)(?:\s+having\s+([\w\s<>!=().]+))?",
        "description": "Calculates the sum of '<field>' grouped by '<group_field>' with optional 'HAVING' clause.",
        "query_template": [
            {"$group": {"_id": "${group_by}", "total_sum": {"$sum": "${sum_field}"}}},
            {"$match": {}}
        ]
    },
    {
        "pattern": r"\b(average|avg|mean|compute average)\s+([\w\s]+)\s+(groupby|by|group by|categorized by|organized by)\s+(\w+)(?:\s+having\s+([\w\s<>!=().]+))?",
        "description": "Calculates the average of '<field>' grouped by '<group_field>' with optional 'HAVING' clause.",
        "query_template": [
            {"$group": {"_id": "${group_by}", "average": {"$avg": "${avg_field}"}}},
            {"$match": {}}
        ]
    },
   {
    "pattern": r"\b(select|filter|find)\b\s+([\w\s]+)\s+(where)\s+(\w+)\s*(==|!=|>|<|>=|<=|=)\s*['\"]?(.+?)['\"]?$",
    "description": "Finds documents from '<collection>' where '<field> <operator> <value>' applies.",
    "query_template": [{"$match": {}}]
}



]

def process_natural_language_query_mongodb(user_query, db=None):
    """
    Process natural language query for MongoDB and generate an aggregation pipeline.
    """
    import re
    user_query = user_query.replace("group by", "by")

    def normalize_field_name(user_field, schema):
        """
        Normalize user-provided field names to match MongoDB schema fields.
        """
        from difflib import get_close_matches
        normalized_field = user_field.strip().lower().replace(" ", "_")  # Basic normalization
        for collection, fields in schema.items():
            closest_match = get_close_matches(normalized_field, fields, n=1, cutoff=0.6)
            if closest_match:
                return closest_match[0], collection
        return None, None

    # Fetch the schema
    schema = mongo_get_collection_schema(db)

    for pattern in mongo_patterns:
        match = re.search(pattern["pattern"], user_query, re.IGNORECASE)
        if match:
            groups = match.groups()
            print(f"Matched groups: {groups}")
            operation = groups[0]  # Extract operation (e.g., "find", "filter")
            field = groups[1]  # Extract target field
            group_by = groups[3] if len(groups) > 3 else None  # Extract group by field
            where_field = groups[3] if len(groups) > 3 else None
            operator = groups[4] if len(groups) > 4 else None  # Extract operator
            value = groups[5] if len(groups) > 5 else None  # Extract value

            # Map fields to schema fields
            field_mapped, collection_for_field = normalize_field_name(field, schema)
            group_by_mapped, collection_for_group_by = normalize_field_name(group_by, schema) if group_by else (None, None)
            where_field_mapped, collection_for_where = normalize_field_name(where_field, schema)

            
            if not field_mapped:
                print(f"Error: Could not map the field '{field}' to any collection.")
                return None

            if group_by and not group_by_mapped:
                print(f"Error: Could not map the group_by field '{group_by}' to any collection.")
                return None
            if not where_field_mapped:
                print(f"Error: Could not map the where field '{where_field}' to any collection.")
                return None

            # Ensure both fields are in the same collection
            if collection_for_field != collection_for_where:
                print(f"Error: Fields '{field_mapped}' and '{where_field_mapped}' are in different collections.")
                return None
            collection = collection_for_field

            # Ensure both fields are in the same collection
            if group_by and collection_for_field != collection_for_group_by:
                print(f"Error: Fields '{field_mapped}' and '{group_by_mapped}' are in different collections.")
                return None

            # Build the aggregation pipeline
            pipeline = []
            if value:
                try:
                    # Parse value type
                    value = value.strip()  # Remove any surrounding whitespace
                    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                        # String value
                        value = value.strip('"').strip("'")
                    elif value.isdigit():  # Integer value
                        value = int(value)
                    else:
                        # Float value or leave as string if it cannot be parsed
                        try:
                            value = float(value)
                        except ValueError:
                            value = str(value)
                except ValueError as ve:
                    print(f"Error: Unable to parse the value '{value}'.")
                    return None
            if operation.lower() in ["count", "number of", "how many"]:
                pipeline.append({
                    "$group": {
                        "_id": f"${group_by_mapped}",
                        "count": {"$sum": 1}
                    }
                })
                if groups[4]:  # HAVING condition exists
                    having_condition = groups[4].strip()
                    operator_map = {
                        ">": "$gt",
                        "<": "$lt",
                        ">=": "$gte",
                        "<=": "$lte",
                        "==": "$eq",
                        "=": "$eq",
                        "!=": "$ne"
                    }
                    having_parts = re.match(r"(?i)(count)\s*(>|<|>=|<=|==|!=)\s*(\d+)", having_condition)
                    if having_parts:
                        field_name, operator, value = having_parts.groups()
                        value = int(value)  # Convert value to integer
                        mongo_operator = operator_map[operator]
                        pipeline.append({
                            "$match": {"count": {mongo_operator: value}}
                        })
                    else:
                        print(f"Error: Could not parse the HAVING condition: {having_condition}")
            elif operation.lower() in ["sum", "add up", "aggregate", "total"]:
                pipeline.append({
                        "$group": {
                            "_id": f"${group_by_mapped}",
                            "total_sum": {"$sum": f"${field_mapped}"}
                    }
                })
                if groups[4]:  # HAVING condition exists
                    having_condition = groups[4].strip()
                    operator_map = {
                            ">": "$gt",
                            "<": "$lt",
                            ">=": "$gte",
                            "<=": "$lte",
                            "==": "$eq",
                            "=": "$eq",
                            "!=": "$ne"
                }
                        # Parse the HAVING clause
                    having_parts = re.match(r"(?i)(sum|total_sum)\s*(>|<|>=|<=|==|!=)\s*(\d+)", having_condition)
                    if having_parts:
                        field_name, operator, value = having_parts.groups()
                        value = int(value)  # Convert value to integer
                        mongo_operator = operator_map[operator]
                        pipeline.append({
                                "$match": {f"total_sum": {mongo_operator: value}}
            })
            elif operation.lower() in ["average", "avg", "mean", "compute average"]:
                pipeline.append({
                    "$group": {
                        "_id": f"${group_by_mapped}",
                        "average": {"$avg": f"${field_mapped}"}
                         }
                })
                if groups[4]:  # HAVING condition exists
                    having_condition = groups[4].strip()
                    operator_map = {
                        ">": "$gt",
                        "<": "$lt",
                        ">=": "$gte",
                        "<=": "$lte",
                        "==": "$eq",
                        "=": "$eq",
                        "!=": "$ne"
                    }
                    having_parts = re.match(r"(?i)(average)\s*(>|<|>=|<=|==|!=)\s*(\d+)", having_condition)
                    if having_parts:
                        field_name, operator, value = having_parts.groups()
                        value = int(value)  # Convert value to integer
                        mongo_operator = operator_map[operator]
                        pipeline.append({
                            "$match": {"average": {mongo_operator: value}}
                        })
                    else:
                        print(f"Error: Could not parse the HAVING condition: {having_condition}")

            elif operation.lower() in ["select", "filter", "find"]:
                operator_map = {
                    ">": "$gt",
                    "<": "$lt",
                    ">=": "$gte",
                    "<=": "$lte",
                    "==": "$eq",
                    "=": "$eq",
                    "!=": "$ne"
                }
                if operator in operator_map:
                    mongo_operator = operator_map[operator]
                    pipeline.append({"$match": {where_field: {mongo_operator: value}}})
                    pipeline.append({
                    "$project": {
                        "_id": 0,
                        field_mapped: 1,
                        group_by_mapped: 1 if group_by else None
                    }
                })
                else:
                    print(f"Error: Unsupported operator '{operator}'.")
                    return None
            

           

            

            description = pattern["description"].replace("<field>", field).replace("<field> <operator> <value>", f"{where_field} {operator} {value}").replace("<group_field>", group_by)

            return {
                "description": description,
                "pipeline": pipeline,
                "collection": collection
            }

    print("No matching query pattern found for the given natural language query.")
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

    print("\nAvailable MongoDB Collections:")
    for collection_name in collections:
        print(f"Collection: {collection_name}")

        # Fetch a sample document to display its fields
        collection = db[collection_name]
        sample_doc = collection.find_one()

        if sample_doc:
            print("Fields:")
            for key in sample_doc.keys():
                print(f" - {key}")
        else:
            print(f" - No documents found in collection '{collection_name}'")

        print("\n")  # Newline after each collection for clarity

def query_decision(connection=None, db=None, db_type="MySQL"):
    generated_queries = []
    while True:
        print("\n\033[1mWhat would you like to do next?\033[0m")
        print("1. Generate sample queries")
        if db_type == "MySQL":
            print("2. Generate queries with specific constructs (e.g., GROUP BY, ORDER BY, etc.)")
        if db_type == "MongoDB":
            print("2. Generate queries with specific constructs (e.g., $match, $group, etc.)")
        if db_type == "MySQL":
            print("3. Execute a sample MySQL query")
        if db_type == "MongoDB":
            print("3. Execute a sample MongoDB query")
        print("0. Back")

        decision = input("Enter your choice (1/2/3/0): ").strip()

        if decision == "1":
            if db_type == "MySQL":
                if connection:
                    generated_queries = generate_mysql_sample_queries(connection)
                    if generated_queries:
                        print("\n\033[1mGenerated Queries:\033[0m")
                        for idx, query in enumerate(generated_queries, start=1):
                            print(f"\033[1m{idx}. {query['title']}:\033[0m")
                            print(f"{query['description']}")
                            print(f"Query:\n{query['query']}\n")
                else:
                    print("MySQL connection is not available.")
            elif db_type == "MongoDB":
                if db is not None:
                    generated_queries = generate_mongodb_sample_queries(db)
                    if generated_queries:
                        print("\n\033[1mGenerated Queries:\033[0m")
                        for idx, query in enumerate(generated_queries, start=1):
                            print(f"\033[1m{idx}. {query['title']}:\033[0m")
                            print(f"{query['description']}")
                            print(f"Query:\n{query['query']}\n")
                    else:
                        print("No sample queries could be generated for MongoDB.")
                else:
                    print("MongoDB connection is not available.")

        elif decision == "2":
            if db_type == "MySQL":
                construct = input("Enter the construct (e.g., GROUP BY, ORDER BY, HAVING, JOIN, EXISTS for MySQL): ").strip().upper()
                if connection:
                    generated_queries = generate_mysql_construct_queries(connection, construct)
                    if generated_queries:
                        print(f"\nThe \033[1m{construct}\033[0m clause in SQL is used as follows:")
                    if construct == "GROUP BY":
                        print("The \033[1mGROUP BY\033[0m clause in SQL is used to aggregate data based on one or more columns. "
                              "It allows you to group rows that have the same values into summary rows, "
                              "often used with aggregate functions like SUM(), COUNT(), AVG(), etc.\n")
                    elif construct == "ORDER BY":
                        print("The \033[1mORDER BY\033[0m clause is used to sort the result set of a query by one or more columns. "
                          "It is commonly used to organize the data in a meaningful way, "
                          "allowing you to order rows in ascending (ASC) or descending (DESC) order. "
                          "\033[1mORDER BY\033[0m can be applied to numeric, text, or date columns.\n")
                    elif construct == "HAVING":
                        print("The \033[1mHAVING\033[0m clause filters the groups created by the GROUP BY clause. "
                              "It is often used to restrict the output of aggregate functions such as SUM() or AVG().\n")
                    elif construct == "JOIN":
                        print("The \033[1mJOIN\033[0m clause is used to combine rows from two or more tables based on a related column."
                            "It allows you to retrieve data that spans multiple tables in a relational database.\n")
                    elif construct == "EXISTS":
                        print("The \033[1mEXISTS\033[0m clause is used to test for the existence of any record in a subquery. "
                              "It returns true if the subquery returns one or more rows.\n")
                    else:
                        print(f"The \033[1m{construct}\033[0m clause is a specific SQL construct used to refine query results.\n")

                    print(f"Here are some examples of queries using \033[1m{construct}\033[0m based on the available data:\n")

                    for query in generated_queries:
                        print(f"\033[1m{query['title']}\033[0m")
                        print(f"SQLQuery:\n{query['query']}")
                        print(f"Description: {query['description']}\n")
                else:
                    print(f"Wrong construct entered. No meaningful sample queries found or not enough columns to generate queries.")

            elif db_type == "MongoDB":
                construct = input("Enter the construct (e.g., $match, $group, $sort, $limit for MongoDB): ").strip().lower()
                if db is not None:
                    generated_queries = generate_mongodb_construct_queries(db, construct)
                    if generated_queries:
                        print(f"\nThe \033[1m{construct}\033[0m stage in MongoDB is used as follows:")
                    if construct == "$match":
                        print("The \033[1m$match\033[0m stage filters documents based on specified criteria. "
                              "It is similar to the WHERE clause in SQL and is typically the first stage in a pipeline.\n")
                    elif construct == "$group":
                        print("The \033[1m$group\033[0m stage groups documents by a specified field and performs aggregations on them, "
                              "similar to the GROUP BY clause in SQL.\n")
                    elif construct == "$sort":
                        print("The \033[1m$sort\033[0m stage sorts documents in ascending or descending order based on specified fields. "
                              "It is similar to the ORDER BY clause in SQL.\n")
                    elif construct == "$limit":
                        print("The \033[1m$limit\033[0m stage restricts the number of documents returned by the pipeline. "
                              "It is equivalent to the LIMIT clause in SQL.\n")
                    else:
                        print(f"The \033[1m{construct}\033[0m stage is a specific MongoDB construct used to refine query results. Not supported for now. \n")

                    print(f"Here are some examples of queries using \033[1m{construct}\033[0m based on the available data:\n")

                    if generated_queries:
                        print("\n\033[1mGenerated Queries:\033[0m")
                        for idx, query in enumerate(generated_queries, start=1):
                            print(f"\033[1m{idx}. {query['title']}:\033[0m")
                            print(f"{query['description']}")
                            print(f"Query:\n{query['query']}\n")
                else:
                    print(f"Wrong construct entered or No meaningful sample queries found for the \033[1m{construct}\033[0m stage or not enough data in collections.")
        elif decision == "3":
            if db_type == "MySQL":
                if connection:
                    if not generated_queries:
                        print("No queries available to execute. Please generate sample queries first.")
                    else:
                        print("\nAvailable Queries:")
                        for idx, query in enumerate(generated_queries, start=1):
                            print(f"{idx}. {query['title']}")
                        try:
                            selected_index = int(input("Enter the query number you want to execute: ").strip()) - 1
                            if 0 <= selected_index < len(generated_queries):
                                selected_query = generated_queries[selected_index]
                                print(f"\nExecuting Query:\n{selected_query['title']}")
                                print(f"{selected_query['description']}")
                                print(f"Query:\n{selected_query['query']}\n")
                                cursor = connection.cursor()
                                cursor.execute(selected_query['query'])
                                results = cursor.fetchall()
                                if results:
                                    print("\nQuery Results:")
                                    for row in results:
                                        print(row)
                                else:
                                    print("The query executed successfully but returned no results.")
                            else:
                                print("Invalid query number. Please try again.")
                        except ValueError:
                            print("Invalid input. Please enter a valid query number.")
                        except Exception as e:
                            print(f"Error executing MySQL query: {e}")
                else:
                    print("MySQL connection is not available.")
            elif db_type == "MongoDB":
                if db is not None:
                    if not generated_queries:
                        print("No queries available to execute. Please generate sample queries first.")
                        return

                    # Display available queries
                    print("\nAvailable Queries:")
                    for idx, query in enumerate(generated_queries, start=1):
                        print(f"{idx}. {query['title']}")

                    try:
                        # Select a query to execute
                        selected_index = int(input("Enter the query number you want to execute: ").strip()) - 1
                        if not (0 <= selected_index < len(generated_queries)):
                            print("Invalid query number. Please try again.")
                            return

                        selected_query = generated_queries[selected_index]
                        print(f"\nExecuting Query: {selected_query['title']}")
                        print(f"{selected_query['description']}")
                        print(f"Query:\n{selected_query['query']}\n")

                        # Retrieve the collection
                        collection_name = selected_query["collection"]
                        collection = db[collection_name]

                        # Execute the query based on its type
                        if selected_query["type"] == "aggregate":
                            # Execute an aggregation query
                            results = list(collection.aggregate(selected_query["query"]))
                        elif selected_query["type"] == "find":
                            # Extract the find command (filter and optional modifiers like sort, limit)
                            filter_query = selected_query["query"].get("filter", {})
                            sort_query = selected_query["query"].get("sort", None)
                            limit_query = selected_query["query"].get("limit", None)

                            # Build and execute the find query
                            cursor = collection.find(filter_query)
                            if sort_query:
                                cursor = cursor.sort(list(sort_query.items()))
                            if limit_query:
                                cursor = cursor.limit(limit_query)
                            results = list(cursor)
                        else:
                            print(f"Unknown query type: {selected_query['type']}")
                            return

                        # Display results
                        if results:
                            print("\nQuery Results:")
                            for result in results:
                                print(result)
                        else:
                            print("The query executed successfully but returned no results.")
                    except ValueError:
                        print("Invalid input. Please enter a valid query number.")
                    except Exception as e:
                        print(f"Error executing MongoDB query: {e}")
                else:
                    print("MongoDB connection is not available.")
        elif decision == "0":
            print("Exiting to main menu.")
            break

        else:
            print("Invalid choice. Please try again.")
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
                while True:
                    print("\n--- MySQL Options ---")
                    print("1. Show tables and columns")
                    print("2. Upload a dataset")
                    print("3. Delete a dataset")
                    print("4. Sample queries")
                    print("5. Enter a natural language query")
                    print("0. Back to main menu")

                    choice = input("Choose an option: ").strip()

                    if choice == "1":
                        show_mysql_tables_and_columns(connection)
                    elif choice == "2":
                        upload_dataset_to_database(connection=connection, db_type="MySQL")
                    elif choice == "3":
                        drop_tables_or_schema(connection=connection, db_type="MySQL")
                    elif choice == "4":
                        query_decision(connection=connection, db_type="MySQL")
                    elif choice == "5":
                        # For MySQL Queries
                        if connection:
                            user_query = input("Enter your natural language query: ").strip()

                            # Process the query
                            result = process_natural_language_query_mysql(user_query, connection=connection, db_type="MySQL")
                            if result:
                                print("\nGenerated Query Description:")
                                print(result["description"])
                                print("\nGenerated Query:")
                                print(result["query"])

                                # Execute the query
                                try:
                                    cursor = connection.cursor()
                                    cursor.execute(result["query"])
                                    results = cursor.fetchall()
                                    if results:
                                        print("\nQuery Results:")
                                        for row in results:
                                            print(row)
                                    else:
                                        print("The query executed successfully but returned no results.")
                                except Exception as e:
                                    print(f"Error executing query: {e}")
                            else:
                                print("Could not process the natural language query.")
                        else:
                            print("MySQL connection is not available.")
                    elif choice == "0":
                        break
        elif db_type == "2":
            db = connect_mongodb()
            if db is not None:
                while True:
                    print("\n--- MongoDB Options ---")
                    print("1. Show collections and fields")
                    print("2. Upload a collection")
                    print("3. Delete a collection")
                    print("4. Sample queries")
                    print("5. Enter a natural language query")
                    print("0. Back to main menu")

                    choice = input("Choose an option: ").strip()

                    if choice == "1":
                        show_mongodb_collections_and_fields(db)
                    elif choice == "2":
                        upload_dataset_to_database(db=db, db_type="MongoDB")
                    elif choice == "3":
                        drop_tables_or_schema(db=db, db_type="MongoDB")
                    elif choice == "4":
                        query_decision(db=db, db_type="MongoDB")
                    elif choice == "5":
                        if db is not None:
                            user_query = input("Enter your natural language query: ").strip()
                            # Call the general function for processing natural language queries
                            result = process_natural_language_query_mongodb(user_query, db=db)
                            if result:
                            

                               
                                    # Display the query results
                                    
                                        print("Generated Query Description:", result["description"])
                                        print("Generated Query Pipeline:", result["pipeline"])  # Ensure we access the correct key
                                        print("Target Collection:", result["collection"])

                                        # Execute the query
                                        try:
                                            collection = db[result["collection"]]
                                            results = list(collection.aggregate(result["pipeline"]))  # Adjust to execute the pipeline
                                            if results:
                                                print("\nQuery Results:")
                                                for doc in results:
                                                    print(doc)
                                            else:
                                                print("The query executed successfully but returned no results.")
                                        except Exception as e:
                                            print(f"Error executing query: {e}")
                            else:
                                        print("Could not process the query.")

                    elif choice == "0":
                        break
        elif db_type == "0":
            print("Exiting the system... Have a good day :) ")
            exit()

        else:
            print("Invalid choice. Please enter '1' for MySQL, '2' for MongoDB, or '0' to exit.")

if __name__ == "__main__":
    chatdb_menu()
