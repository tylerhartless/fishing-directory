"""
Script to reset the database - truncate table and reset AUTO_INCREMENT
"""
from db_utils import execute_query

def reset_fishing_spots():
    """Delete all data from fishing_spots and reset AUTO_INCREMENT to 1"""

    print("Resetting fishing_spots table...")

    # Can't use TRUNCATE due to foreign key constraints
    # Use DELETE instead and manually reset AUTO_INCREMENT
    execute_query("DELETE FROM fishing_spots", fetch=False)
    execute_query("ALTER TABLE fishing_spots AUTO_INCREMENT = 1", fetch=False)

    print("[OK] Table reset complete. AUTO_INCREMENT reset to 1.")
    print("You can now run process_boat_ramps.py to import fresh data.")

if __name__ == "__main__":
    print("="*50)
    print("Reset Fishing Spots Table")
    print("="*50)

    confirm = input("This will DELETE all data in fishing_spots. Continue? (yes/no): ")

    if confirm.lower() == 'yes':
        reset_fishing_spots()
    else:
        print("Cancelled.")