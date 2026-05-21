import os
import json
import psycopg2
from psycopg2 import extras
from dotenv import load_dotenv

# 1. Path Setup & Environment Loading
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, 'plants_data.json')

load_dotenv(os.path.join(BASE_DIR, '.env'))

# 2. Extract Database Configurations safely from Environment Variables
DB_NAME = os.getenv("DB_NAME", "leafsnap_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

def migrate_json_to_postgres():
    if not os.path.exists(JSON_PATH):
        print(f"❌ Error: Cannot find your data file at '{JSON_PATH}'")
        return

    print("📂 Reading your pristine narrative plants_data.json...")
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        try:
            plants_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Error decoding JSON: {e}")
            return

    connection = None
    cursor = None

    try:
        print("🔌 Connecting to the PostgreSQL database via environment variables...")
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = connection.cursor()

        # ====== UPDATED QUERY TO INJECT NOW() FOR CREATED_AT ======
        upsert_query = """
            INSERT INTO plant_backend_plantinfo (folder_id, common_name, botanical_name, medicinal_benefits, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            ON CONFLICT (folder_id) 
            DO UPDATE SET 
                common_name = EXCLUDED.common_name,
                botanical_name = EXCLUDED.botanical_name,
                medicinal_benefits = EXCLUDED.medicinal_benefits;
        """

        print(f"🚀 Preparing to seed {len(plants_data)} distinct botanical records into plant_backend_plantinfo...")
        
        success_count = 0
        for folder_id, details in plants_data.items():
            cursor.execute(upsert_query, (
                folder_id,
                details['common_name'],
                details['botanical_name'],
                details['medicinal_benefits']
            ))
            success_count += 1

        # Commit all transitions safely
        connection.commit()
        
        print("\n==================================================")
        print(f"🎉 SUCCESS: {success_count}/184 records synchronized!")
        print("🛡️  All database rows now feature unique, rich narrative descriptions.")
        print("==================================================")

    except Exception as error:
        print(f"\n❌ Database Migration Failed: {error}")
        if connection:
            print("🔄 Rolling back transactions...")
            connection.rollback()

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("🔌 Database connection closed cleanly.")

if __name__ == "__main__":
    migrate_json_to_postgres()