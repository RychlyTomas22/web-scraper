import mysql.connector
from mysql.connector import Error
import json

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            # FILL WITH CORRECT INFORMATION
            host='localhost',
            database='',
            user='',
            password=''
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    return None

def execute_query(connection, query):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"Error executing query: {e}")
    finally:
        cursor.close()

def main():
    connection = connect_to_database()
    if not connection:
        return

    try:
        # 1
        query = "SELECT title, article_text FROM articles ORDER BY RAND() LIMIT 1"
        result = execute_query(connection, query)
        if result:
            print("1. Random Article:")
            print(f"Title: {result[0]['title']}")
            print()

        # 2
        query = "SELECT COUNT(*) AS total_articles FROM articles"
        result = execute_query(connection, query)
        if result:
            print(f"2. Total number of articles: {result[0]['total_articles']}")
            print()

        # 3
        query = "SELECT AVG(image_count) AS avg_photos FROM articles"
        result = execute_query(connection, query)
        if result:
            print(f"3. Average number of photos per article: {result[0]['avg_photos']:.2f}")
            print()

        # 4
        query = "SELECT COUNT(*) AS articles_with_many_comments FROM articles WHERE comments_count > 100"
        result = execute_query(connection, query)
        if result:
            print(f"4. Number of articles with more than 100 comments: {result[0]['articles_with_many_comments']}")
            print()

        # 5
        query = """
        SELECT 
            category,
            COUNT(*) AS article_count
        FROM articles
        WHERE YEAR(time_date) = 2022
        GROUP BY category
        """
        result = execute_query(connection, query)
        if result:
            print("5. Number of articles from 2022 for each category:")
            for row in result:
                print(f"   {row['category']}: {row['article_count']}")

    finally:
        if connection.is_connected():
            connection.close()

if __name__ == "__main__":
    main()
