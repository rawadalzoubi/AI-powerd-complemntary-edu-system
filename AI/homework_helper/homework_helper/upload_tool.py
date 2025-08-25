import mysql.connector
import os
import argparse
from config import MYSQL_CONFIG # Assuming your .env and config.py are set up

def upload_file_to_db(file_path: str):
    """Uploads a single file to the MySQL database specified in MYSQL_CONFIG."""
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    file_name = os.path.basename(file_path)
    try:
        with open(file_path, "rb") as f:
            file_content = f.read()
    except Exception as e:  
        print(f"Error reading file {file_path}: {e}")
        return

    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # Check if file with the same name already exists
        cursor.execute("SELECT id FROM files WHERE file_name = %s", (file_name,))
        existing_file = cursor.fetchone()
        
        if existing_file:
            overwrite = input(f"File '{file_name}' already exists in the database. Overwrite? (yes/no): ").lower()
            if overwrite == 'yes':
                cursor.execute("UPDATE files SET file_content = %s, uploaded_at = CURRENT_TIMESTAMP WHERE id = %s", 
                               (file_content, existing_file[0]))
                conn.commit()
                print(f"File '{file_name}' (ID: {existing_file[0]}) updated in the database.")
            else:
                print(f"Skipped existing file: {file_name}")
                return
        else:
            # Insert new file
            query = "INSERT INTO files (file_name, file_content) VALUES (%s, %s)"
            cursor.execute(query, (file_name, file_content))
            conn.commit()
            print(f"File '{file_name}' (ID: {cursor.lastrowid}) uploaded successfully to database '{MYSQL_CONFIG.get('database')}'.")
            
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def main():
    parser = argparse.ArgumentParser(description="Upload files to the Homework Helper database.")
    parser.add_argument("file_paths", nargs='+', help="Path(s) to the file(s) to upload.")
    
    args = parser.parse_args()
    
    # Ensure .env is loaded by config.py if it hasn't been already
    # from config import MYSQL_CONFIG is enough if config.py handles dotenv.load_dotenv()

    if not MYSQL_CONFIG.get("database") or not MYSQL_CONFIG.get("user") :
        print("MySQL configuration is not fully set. Please check your .env file and config.py.")
        print(f"Current config: User={MYSQL_CONFIG.get('user')}, DB={MYSQL_CONFIG.get('database')}")
        return

    for file_path in args.file_paths:
        upload_file_to_db(file_path)

if __name__ == "__main__":
    main() 