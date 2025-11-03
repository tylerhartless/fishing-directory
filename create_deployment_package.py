#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create deployment package for Hostinger
"""

import sys
import shutil
import os
import subprocess
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("CREATING DEPLOYMENT PACKAGE FOR HOSTINGER")
print("=" * 70)
print()

# Create deploy directory
deploy_dir = Path('deploy')
if deploy_dir.exists():
    shutil.rmtree(deploy_dir)
deploy_dir.mkdir()

print("1. Copying frontend build...")
shutil.copytree('frontend/dist', 'deploy/public_html')
print("   -> Copied to deploy/public_html/")

print("\n2. Copying backend API...")
os.makedirs('deploy/public_html/api', exist_ok=True)
for file in ['spots.php', 'submit-report.php', 'reports.php', 'vote.php', 'get-votes.php']:
    shutil.copy(f'backend/api/{file}', f'deploy/public_html/api/')
shutil.copy('backend/api/config.prod.php', 'deploy/public_html/api/config.php')
shutil.copy('backend/api/.htaccess', 'deploy/public_html/api/')
print("   -> Copied to deploy/public_html/api/")

print("\n3. Exporting database...")
import pymysql

MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'fishing_user',
    'password': 'fishing_password',
    'database': 'fishing_directory'
}

conn = pymysql.connect(**MYSQL_CONFIG)
cursor = conn.cursor()

# Get all tables
cursor.execute("SHOW TABLES")
tables = [row[0] for row in cursor.fetchall()]

with open('deploy/database.sql', 'w', encoding='utf-8') as f:
    f.write("-- Fishing Directory Database Export\n")
    f.write("-- Generated for production deployment\n\n")
    f.write("SET SQL_MODE = \"NO_AUTO_VALUE_ON_ZERO\";\n")
    f.write("SET time_zone = \"+00:00\";\n\n")
    f.write("/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;\n")
    f.write("/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;\n")
    f.write("/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;\n")
    f.write("/*!40101 SET NAMES utf8mb4 */;\n\n")

    for table in tables:
        # Get CREATE TABLE statement
        cursor.execute(f"SHOW CREATE TABLE `{table}`")
        create_table = cursor.fetchone()[1]
        f.write(f"\n-- Table structure for table `{table}`\n")
        f.write(f"DROP TABLE IF EXISTS `{table}`;\n")
        f.write(f"{create_table};\n\n")

        # Get data
        cursor.execute(f"SELECT * FROM `{table}`")
        rows = cursor.fetchall()

        if rows:
            cursor.execute(f"SHOW COLUMNS FROM `{table}`")
            columns = [col[0] for col in cursor.fetchall()]
            col_list = ', '.join([f'`{col}`' for col in columns])

            f.write(f"-- Dumping data for table `{table}`\n")
            f.write(f"INSERT INTO `{table}` ({col_list}) VALUES\n")

            for i, row in enumerate(rows):
                values = []
                for val in row:
                    if val is None:
                        values.append('NULL')
                    elif isinstance(val, (int, float)):
                        values.append(str(val))
                    else:
                        # Escape single quotes
                        val_str = str(val).replace("'", "''")
                        values.append(f"'{val_str}'")

                value_str = f"({', '.join(values)})"
                if i < len(rows) - 1:
                    f.write(f"{value_str},\n")
                else:
                    f.write(f"{value_str};\n")

            f.write("\n")

    f.write("/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;\n")
    f.write("/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;\n")
    f.write("/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;\n")

conn.close()

db_size = os.path.getsize('deploy/database.sql') / 1024 / 1024
print(f"   -> Exported to deploy/database.sql ({db_size:.1f} MB)")

print("\n4. Creating .htaccess for root...")
with open('deploy/public_html/.htaccess', 'w') as f:
    f.write("""# Fishing Directory - Main .htaccess

# Enable rewrite engine
RewriteEngine On

# Force HTTPS (uncomment when SSL is setup)
# RewriteCond %{HTTPS} off
# RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Remove trailing slashes
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.+)/$ /$1 [R=301,L]

# Security headers
<IfModule mod_headers.c>
    Header set X-Content-Type-Options "nosniff"
    Header set X-Frame-Options "SAMEORIGIN"
    Header set X-XSS-Protection "1; mode=block"
    Header set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>

# Compress text files
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/json
</IfModule>

# Browser caching
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/gif "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/svg+xml "access plus 1 year"
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
    ExpiresByType text/html "access plus 1 hour"
</IfModule>

# Disable directory listing
Options -Indexes

# Protect sensitive files
<FilesMatch "^(\\.htaccess|\\.env|config\\.php)$">
    Order allow,deny
    Deny from all
</FilesMatch>
""")
print("   -> Created deploy/public_html/.htaccess")

print("\n" + "=" * 70)
print("DEPLOYMENT PACKAGE READY!")
print("=" * 70)
print("\nContents of deploy/:")
print("  public_html/        <- Upload this entire folder to your Hostinger public_html")
print("  database.sql        <- Import this via phpMyAdmin")
print("\nNext steps: See HOSTINGER_DEPLOYMENT_GUIDE.md")
