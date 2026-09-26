import json

# Cesta k souboru JSON
file_path = 'articles_data.json'

# Načtení dat ze souboru JSON
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Odstranění článků s prázdným textem
cleaned_data = [article for article in data if article.get('article_text', '').strip()]

# Odstranění duplicit na základě titulu článku (nebo jiného kritéria)
# Pokud je potřeba odstranit duplicity na základě jiného kritéria, uprav klíč 'title'
seen_titles = set()
unique_articles = []
for article in cleaned_data:
    title = article.get('title', '').strip()
    if title not in seen_titles:
        seen_titles.add(title)
        unique_articles.append(article)

# Uložení vyčištěného seznamu článků zpět do původního souboru
with open(file_path, 'w', encoding='utf-8') as file:
    json.dump(unique_articles, file, ensure_ascii=False, indent=4)

print(f"Data byla úspěšně vyčištěna a uložena zpět do {file_path}.")
