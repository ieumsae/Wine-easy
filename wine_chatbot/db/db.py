import mysql.connector
import os
from dotenv import load_dotenv
import re

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME')
    )

def is_korean(text):
    """Determine if the text contains Korean characters."""
    return bool(re.search('[\u3131-\uD79D]', text))

def get_wine_info_by_name(wine_name):
    """Fetch wine info by name with full-text search for English names or exact match for Korean names."""
    conn = None
    try:
        print("Connecting to the database...")
        conn = get_db_connection()
        print("Connected to the database.")
        
        cursor = conn.cursor()

        # 입력된 이름이 한글인지 영어인지 판별
        if is_korean(wine_name):
            query =  """
                SELECT * 
                FROM wines
                WHERE MATCH(wine_name_ko) AGAINST (%s IN BOOLEAN MODE) 
                ORDER BY MATCH(wine_name_ko) AGAINST (%s IN BOOLEAN MODE) DESC
                LIMIT 1
            """
            params = (wine_name, wine_name)
        else:
            query = """
                SELECT * 
                FROM wines
                WHERE MATCH(wine_name_en) AGAINST (%s IN BOOLEAN MODE) 
                ORDER BY MATCH(wine_name_en) AGAINST (%s IN BOOLEAN MODE) DESC
                LIMIT 1
            """
            params = (wine_name, wine_name)

        print(f"Executing query: {query} with parameter: {params}")

        cursor.execute(query, params)
        
        result = cursor.fetchall()
        print("Query executed successfully.")
        print(f"Number of rows fetched: {len(result)}")
        
        wine_details = [
            {
                'id': row[0],
                'wine_name_ko': row[1],
                'wine_name_en': row[2],
                'wine_type': row[3],
                'country': row[4],
                'recommended_dish': row[5],
                'taste': row[6],
                'wine_sweet': row[7],
                'wine_body': row[8],
                'wine_acidity': row[9],
                'wine_tannin': row[10]
            }
            for row in result
        ]
        print("Wine details processed successfully.")
        return wine_details
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")
