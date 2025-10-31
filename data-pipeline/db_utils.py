"""
Database utility functions for ETL scripts
"""
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

def get_connection(silent=False):
    """
    Create and return a MySQL database connection

    Args:
        silent (bool): If True, suppress connection success message

    Returns:
        mysql.connector.connection.MySQLConnection: Database connection
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            if not silent:
                print(f"[OK] Connected to MySQL database: {DB_CONFIG['database']}")
            return conn
    except Error as e:
        print(f"[ERROR] Error connecting to MySQL: {e}")
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
            print(f"[OK] Query executed successfully. Rows affected: {cursor.rowcount}")

    except Error as e:
        print(f"[ERROR] Query error: {e}")
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
        print("[WARNING] No data to insert")
        return 0

    print(f"Connecting to database...")
    conn = get_connection(silent=False)
    cursor = conn.cursor()

    # Build INSERT query
    placeholders = ', '.join(['%s'] * len(columns))
    column_names = ', '.join(columns)
    query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"

    try:
        cursor.executemany(query, data)
        conn.commit()
        rows_inserted = cursor.rowcount
        print(f"[OK] Inserted {rows_inserted} rows into {table}")
        return rows_inserted

    except Error as e:
        print(f"[ERROR] Bulk insert error: {e}")
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
    conn = get_connection(silent=True)  # Silent connection
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT COUNT(*) as count FROM fishing_spots WHERE slug = %s", (slug,))
        result = cursor.fetchone()
        return result['count'] > 0
    finally:
        cursor.close()
        conn.close()

def find_nearby_spots(latitude, longitude, radius_meters=100):
    """
    Find existing fishing spots within a radius using Haversine formula

    Args:
        latitude (float): Latitude to search around
        longitude (float): Longitude to search around
        radius_meters (int): Search radius in meters (default 100m)

    Returns:
        list: List of nearby spots with distance in meters
    """
    conn = get_connection(silent=True)
    cursor = conn.cursor(dictionary=True)

    # Haversine formula for distance in meters
    # Formula: 6371000 * 2 * ASIN(SQRT(POWER(SIN((lat1 - lat2) * PI()/180 / 2), 2) +
    #          COS(lat1 * PI()/180) * COS(lat2 * PI()/180) *
    #          POWER(SIN((lon1 - lon2) * PI()/180 / 2), 2)))
    query = """
        SELECT
            id,
            name,
            slug,
            latitude,
            longitude,
            spot_type,
            data_source,
            (
                6371000 * 2 * ASIN(SQRT(
                    POWER(SIN((latitude - %s) * PI()/180 / 2), 2) +
                    COS(%s * PI()/180) * COS(latitude * PI()/180) *
                    POWER(SIN((longitude - %s) * PI()/180 / 2), 2)
                ))
            ) AS distance_meters
        FROM fishing_spots
        HAVING distance_meters <= %s
        ORDER BY distance_meters ASC
        LIMIT 5
    """

    try:
        cursor.execute(query, (latitude, latitude, longitude, radius_meters))
        results = cursor.fetchall()
        return results
    finally:
        cursor.close()
        conn.close()

def update_spot_if_better(spot_id, new_data):
    """
    Update an existing spot with better/richer data

    Args:
        spot_id (int): ID of spot to update
        new_data (dict): Dictionary of fields to update

    Returns:
        bool: True if updated successfully
    """
    conn = get_connection(silent=True)
    cursor = conn.cursor()

    # Build UPDATE query dynamically from new_data
    set_clauses = []
    values = []

    for field, value in new_data.items():
        set_clauses.append(f"{field} = %s")
        values.append(value)

    values.append(spot_id)  # For WHERE clause

    query = f"UPDATE fishing_spots SET {', '.join(set_clauses)} WHERE id = %s"

    try:
        cursor.execute(query, tuple(values))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"[ERROR] Update error: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # Test database connection
    conn = get_connection()
    if conn:
        print("Database connection test successful!")
        conn.close()
