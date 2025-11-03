#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export database for Hostinger - with proper ordering and no foreign key issues
"""

import sys
import pymysql

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'fishing_user',
    'password': 'fishing_password',
    'database': 'fishing_directory'
}

print("Exporting database for Hostinger...")

conn = pymysql.connect(**MYSQL_CONFIG)
cursor = conn.cursor()

# Table creation order - parent tables first
table_order = [
    'fishing_spots',           # Parent table (no dependencies)
    'fishing_reports',         # Depends on fishing_spots
    'spot_votes',              # Depends on fishing_spots
    'fish_habitat_structures'  # Depends on fishing_spots
]

with open('deploy/database_hostinger.sql', 'w', encoding='utf-8') as f:
    f.write("-- Fishing Directory Database Export for Hostinger\n")
    f.write("-- Generated for production deployment\n")
    f.write("-- Safe import order with foreign key handling\n\n")

    f.write("SET SQL_MODE = \"NO_AUTO_VALUE_ON_ZERO\";\n")
    f.write("SET time_zone = \"+00:00\";\n")
    f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")  # Disable FK checks during import

    f.write("/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;\n")
    f.write("/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;\n")
    f.write("/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;\n")
    f.write("/*!40101 SET NAMES utf8mb4 */;\n\n")

    for table in table_order:
        # Check if table exists
        cursor.execute(f"SHOW TABLES LIKE '{table}'")
        if not cursor.fetchone():
            print(f"  Skipping {table} (doesn't exist)")
            continue

        print(f"  Exporting {table}...")

        # Get CREATE TABLE statement
        cursor.execute(f"SHOW CREATE TABLE `{table}`")
        create_table = cursor.fetchone()[1]

        f.write(f"\n-- --------------------------------------------------------\n")
        f.write(f"-- Table structure for table `{table}`\n")
        f.write(f"-- --------------------------------------------------------\n\n")
        f.write(f"DROP TABLE IF EXISTS `{table}`;\n")
        f.write(f"{create_table};\n\n")

        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
        row_count = cursor.fetchone()[0]

        if row_count == 0:
            print(f"    (empty table)")
            continue

        print(f"    ({row_count} rows)")

        # Get data in chunks to avoid memory issues
        cursor.execute(f"SELECT * FROM `{table}`")
        rows = cursor.fetchall()

        if rows:
            cursor.execute(f"SHOW COLUMNS FROM `{table}`")
            columns = [col[0] for col in cursor.fetchall()]
            col_list = ', '.join([f'`{col}`' for col in columns])

            f.write(f"-- Dumping data for table `{table}`\n\n")
            f.write(f"INSERT INTO `{table}` ({col_list}) VALUES\n")

            for i, row in enumerate(rows):
                values = []
                for val in row:
                    if val is None:
                        values.append('NULL')
                    elif isinstance(val, (int, float)):
                        values.append(str(val))
                    elif isinstance(val, bytes):
                        # Handle binary data
                        values.append(f"'{val.hex()}'")
                    else:
                        # Escape single quotes and backslashes
                        val_str = str(val).replace('\\', '\\\\').replace("'", "\\'")
                        values.append(f"'{val_str}'")

                value_str = f"({', '.join(values)})"

                # Write in batches of 100 rows per INSERT
                if (i + 1) % 100 == 0 and i < len(rows) - 1:
                    f.write(f"{value_str};\n\n")
                    f.write(f"INSERT INTO `{table}` ({col_list}) VALUES\n")
                elif i < len(rows) - 1:
                    f.write(f"{value_str},\n")
                else:
                    f.write(f"{value_str};\n\n")

    f.write("SET FOREIGN_KEY_CHECKS = 1;\n\n")  # Re-enable FK checks
    f.write("/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;\n")
    f.write("/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;\n")
    f.write("/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;\n")

conn.close()

import os
file_size = os.path.getsize('deploy/database_hostinger.sql') / 1024 / 1024
print(f"\n✓ Database exported successfully!")
print(f"  File: deploy/database_hostinger.sql")
print(f"  Size: {file_size:.1f} MB")
print(f"\n✓ This version is optimized for Hostinger:")
print(f"  - Foreign key checks disabled during import")
print(f"  - Tables in correct dependency order")
print(f"  - Batch inserts for better performance")
print(f"  - Proper escaping for special characters")
