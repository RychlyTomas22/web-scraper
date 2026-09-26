import json
import mysql.connector

cnx = mysql.connector.connect(
    # FILL WITH CORRECT INFORMATION
    user='root',
    password='',
    host='127.0.0.1',
    database='idnes_articles'
)
cursor = cnx.cursor()

with open('articles_data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

add_article = (
    "INSERT INTO articles (title, article_text, image_count, time_date, comments_count, category) "
    "VALUES (%s, %s, %s, %s, %s, %s)"
)

for article in data:
    title = article.get('title')
    article_text = article.get('article_text')
    image_count = article.get('image_count')
    time_date = article.get('time_date')
    comments_count = article.get('comments_count')
    category = article.get('category')

    cursor.execute(add_article, (title, article_text, image_count, time_date, comments_count, category))

cnx.commit()
cursor.close()
cnx.close()
