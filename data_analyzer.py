import json
from collections import Counter
from datetime import datetime


with open('articles_data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)


def parse_date(date_str):
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.replace(tzinfo=None)
    except ValueError:
        return None

def total_articles(data):
    return len(data)

def duplicate_titles(data):
    titles = []
    for article in data:
        if "title" in article:
            titles.append(article["title"])
    return len(titles) - len(set(titles))

def oldest_article_date(data):
    dates = []
    for article in data:
        if "time_date" in article and isinstance(article["time_date"], str):
            date = parse_date(article["time_date"])
            if date:
                dates.append(date)
    return min(dates).strftime("%Y-%m-%d") if dates else "N/A", dates

def most_comments_article(data):
    most_comments = "N/A"
    max_comments = 0
    for article in data:
        comments = article.get("comments_count", 0)
        if comments > max_comments:
            max_comments = comments
            most_comments = article.get("title", "N/A")
    return most_comments

def most_images_article(data):
    max_images = 0
    for article in data:
        images = article.get("image_count", 0)
        if images > max_images:
            max_images = images
    return max_images

def articles_by_year(dates):
    by_year = Counter()
    for date in dates:
        by_year[date.year] += 1
    return by_year

def articles_by_category(data):
    categories = []
    for article in data:
        categories.append(article.get("category", "Unknown"))
    unique_categories = len(set(categories))
    per_category = Counter(categories)
    return unique_categories, per_category

def frequent_words_2021(data):
    words = []
    for article in data:
        if "time_date" in article and isinstance(article["time_date"], str):
            date = parse_date(article["time_date"])
            if date and date.year == 2021:
                title_words = article.get("title", "").split()
                words.extend([word.lower() for word in title_words if len(word) >= 6])
    return Counter(words).most_common(5)

def total_comments(data):
    comments = 0
    for article in data:
        comments += article.get("comments_count", 0)
    return comments

def total_words(data):
    words = 0
    for article in data:
        words += len(article.get("article_text", "").split())
    return words

def frequent_words(data):
    words = []
    for article in data:
        article_words = article.get("article_text", "").split()
        words.extend([word.lower() for word in article_words if len(word) >= 6])
    return Counter(words).most_common(8)

def top_covid_articles(data):
    covid_articles = []
    for article in data:
        text = article.get("article_text", "").lower()
        count = text.count("covid-19")
        covid_articles.append((article.get("title", "N/A"), count))
    
    covid_articles.sort(key=get_second_item, reverse=True)
    return covid_articles[:3]

def get_second_item(item):
    return item[1]

def most_fewest_words(data):
    most_article = None
    fewest_article = None
    most_count = 0
    fewest_count = float('inf')

    for article in data:
        word_count = len(article.get("article_text", "").split())
        if word_count > most_count:
            most_count = word_count
            most_article = article.get("title", "N/A")
        if word_count < fewest_count:
            fewest_count = word_count
            fewest_article = article.get("title", "N/A")
    
    return most_article, most_count, fewest_article, fewest_count

def avg_word_length(data, total_words):
    total_len = 0
    for article in data:
        for word in article.get("article_text", "").split():
            total_len += len(word)
    return total_len / total_words if total_words > 0 else 0

def articles_by_month(dates):
    by_month = Counter()
    for date in dates:
        by_month[date.strftime("%Y-%m")] += 1
    return by_month

def most_fewest_articles(by_month):
    most = max(by_month.items(), key=get_dict_value, default=("N/A", 0))
    fewest = min(by_month.items(), key=get_dict_value, default=("N/A", 0))
    return most, fewest

def get_dict_value(item):
    return item[1]


# Main function to run all tasks and print results
def main():
    total = total_articles(data)
    duplicates = duplicate_titles(data)
    oldest, dates = oldest_article_date(data)
    most_comments = most_comments_article(data)
    max_images = most_images_article(data)
    by_year = articles_by_year(dates)
    unique_categories, per_category = articles_by_category(data)
    top_words_2021 = frequent_words_2021(data)
    comments = total_comments(data)
    words = total_words(data)
    top_words = frequent_words(data)
    top_covid = top_covid_articles(data)
    most_article, most_count, fewest_article, fewest_count = most_fewest_words(data)
    avg_length = avg_word_length(data, words)
    by_month = articles_by_month(dates)
    most_month, fewest_month = most_fewest_articles(by_month)

    # Print the Results
    print("\n=== Article Analysis Summary ===")
    print(f"1. Total number of articles: {total:,}")
    print(f"2. Number of duplicate articles: {duplicates:,}")
    print(f"3. Date of the oldest article: {oldest}")
    print(f"4. Title of the article with the most comments: \"{most_comments}\"")
    print(f"5. Highest number of images in an article: {max_images}")
    print("\n6. Number of articles by year:")
    for year, count in sorted(by_year.items()):
        print(f"   - {year}: {count:,} articles")
    print(f"\n7. Number of unique categories: {unique_categories}")
    print("   Articles per category:")
    for category, count in per_category.most_common():
        print(f"   - {category}: {count:,} articles")
    print("\n8. Top 5 most frequent words in titles from 2021:")
    for word, frequency in top_words_2021:
        print(f"   - '{word}': {frequency:,} occurrences")
    print(f"\n9. Total number of comments: {comments:,}")
    print(f"10. Total number of words in all articles: {words:,}")
    print("\n -------BONUS-------")
    print("\n11. Top 8 most frequent words in articles (6+ characters):")
    for word, frequency in top_words:
        print(f"   - '{word}': {frequency:,} occurrences")
    print("\n12. Top 3 articles with the highest occurrences of 'Covid-19':")
    for title, count in top_covid:
        print(f"   - '{title}': {count:,} occurrences")
    print(f"\n13. Article with the most words: \"{most_article}\" ({most_count:,} words)")
    print(f"14. Article with the fewest words: \"{fewest_article}\" ({fewest_count:,} words)")
    print(f"\n15. Average word length across all articles: {avg_length:.2f} characters")
    print(f"\n16. Month with the most articles: {most_month[0]} ({most_month[1]:,} articles)")
    print(f"17. Month with the fewest articles: {fewest_month[0]} ({fewest_month[1]:,} articles)")


main()
