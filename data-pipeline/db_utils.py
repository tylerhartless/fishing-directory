"""
Database utility functions for ETL scripts
"""
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

def get_connection():
    """
    Create and return a MySQL database connection

    Returns:
        mysql.connector.connection.MySQLConnection: Database connection
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            print(f"✓ Connected to MySQL database: {DB_CONFIG['database']}")
            return conn
    except Error as e:
        print(f"✗ Error connecting to MySQL: {e}")
        raise

def execute_query(query, params=None, fetch=False):
    """
    Execute a SQL query with optional parameters

    Args:
        query (str): SQL query to execute
        params (tuple): Optional parameters for prepared statement
        fetch (bool): Whether to fetch and return results

    Returns:
        list: Query results if fetch=True, else None
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(query, params or ())

        if fetch:
            results = cursor.fetchall()
            return results
        else:
            conn.commit()
            print(f"✓ Query executed successfully. Rows affected: {cursor.rowcount}")

    except Error as e:
        print(f"✗ Query error: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def bulk_insert(table, columns, data):
    """
    Perform bulk insert into a table

    Args:
        table (str): Table name
        columns (list): List of column names
        data (list): List of tuples containing row data

    Returns:
        int: Number of rows inserted
    """
    if not data:
        print("⚠ No data to insert")
        return 0

    conn = get_connection()
    cursor = conn.cursor()

    # Build INSERT query
    placeholders = ', '.join(['%s'] * len(columns))
    column_names = ', '.join(columns)
    query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"

    try:
        cursor.executemany(query, data)
        conn.commit()
        rows_inserted = cursor.rowcount
        print(f"✓ Inserted {rows_inserted} rows into {table}")
        return rows_inserted

    except Error as e:
        print(f"✗ Bulk insert error: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def check_duplicate_slug(slug):
    """
    Check if a slug already exists in fishing_spots

    Args:
        slug (str): URL slug to check

    Returns:
        bool: True if exists, False otherwise
    """
    query = "SELECT COUNT(*) as count FROM fishing_spots WHERE slug = %s"
    result = execute_query(query, (slug,), fetch=True)
    return result[0]['count'] > 0

if __name__ == "__main__":
    # Test database connection
    conn = get_connection()
    if conn:
        print("Database connection test successful!")
        conn.close()
