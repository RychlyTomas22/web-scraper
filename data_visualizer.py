import json
import pandas as pd
import plotnine as p9
from plotnine import *
import matplotlib.pyplot as plt


with open('articles_data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

df = pd.DataFrame(data)
df['time_date'] = pd.to_datetime(df['time_date'], errors='coerce', utc=True)
df = df.dropna(subset=['time_date'])
df['word_count'] = df['article_text'].apply(lambda x: len(x.split()))  
df['word_length'] = df['article_text'].apply(lambda x: sum(len(word) for word in x.split()) / len(x.split())) 
df['year'] = df['time_date'].dt.year
df['day'] = df['time_date'].dt.date
df['c_count'] = df.groupby('day').cumcount() + 1
df['coronavirus_in_title'] = df['title'].apply(lambda x: 1 if 'koronavirus' in x.lower() else 0)
df_coronavirus = df.groupby('time_date')['coronavirus_in_title'].sum().reset_index()
df['vaccine_in_title'] = df['title'].apply(lambda x: 1 if 'vakcína' in x.lower() else 0)
df_vaccine = df.groupby('time_date')['vaccine_in_title'].sum().reset_index()
df['day_of_week'] = df['time_date'].dt.day_name()
category_share = df['category'].value_counts(normalize=True)

day_translation = {
    'Monday': 'Pondělí',
    'Tuesday': 'Úterý',
    'Wednesday': 'Středa',
    'Thursday': 'Čtvrtek',
    'Friday': 'Pátek',
    'Saturday': 'Sobota',
    'Sunday': 'Neděle'
}
df['day_of_week_cz'] = df['day_of_week'].map(day_translation)
day_of_week_counts = df['day_of_week_cz'].value_counts().reindex(
    ['Pondělí', 'Úterý', 'Středa', 'Čtvrtek', 'Pátek', 'Sobota', 'Neděle']
)

# Plot 1:
curve_plot = (
    ggplot(df, aes(x='time_date', y='c_count')) +
    geom_line(color='green') + 
    scale_x_datetime(date_breaks='12 month', date_labels='%b %Y') +
    expand_limits(y=(0, df['c_count'].max() + 5)) +
    labs(title="Přidávání článků v čase", x="Datum", y="Kumulativní počet článků") +
    theme(
        axis_text_x=element_text(rotation=45, hjust=1),
        figure_size=(25, 8) 
    )
)

# Plot 2:
line_graph_years = (
    ggplot(df, aes(x='year')) +
    geom_bar(stat="count", fill='blue', color='black') +
    labs(title="Počet článků za roky", x="Rok", y="Počet článků") +
    theme(axis_text_x=element_text(rotation=45, hjust=1))
)

# Plot 3:
scatter_plot = (
    ggplot(df, aes(x='word_count', y='comments_count')) +
    geom_point(color='green') +
    labs(title="Vztah mezi délkou článku a počtem komentářů", x="Počet slov", y="Počet komentářů")
)

# Plot 4
# colour pallete
cmap = plt.get_cmap('tab20')
colors = cmap.colors[:len(category_share)]

plt.figure(figsize=(8, 8))
wedges, texts, autotexts = plt.pie(
    category_share,
    autopct=lambda pct: f'{pct:.1f}%' if pct >= 3 else '',
    startangle=90,
    textprops={'fontsize': 10},
    colors=colors
)

plt.legend(
    wedges, 
    category_share.index, 
    title="Kategorie",
    loc="center left", 
    bbox_to_anchor=(1, 0.5),
    fontsize=10
)

plt.title("Podíl článků v jednotlivých kategoriích")
plt.axis('equal')
plt.tight_layout()
plt.savefig('graphs/data_vizualizer/pie_chart_fixed_legend.png', dpi=300)
plt.close()

# Plot 5: 
histogram_word_count = (
    ggplot(df, aes(x='word_count')) +
    geom_histogram(binwidth=50, fill='orange', color='black') +
    labs(title="Histogram počtu slov v článcích", x="Počet slov", y="Počet článků")
)

# Plot 6:
histogram_word_length = (
    ggplot(df, aes(x='word_length')) +
    geom_histogram(binwidth=0.5, fill='purple', color='black') +
    labs(title="Histogram délky slov v článcích", x="Průměrná délka slov", y="Počet článků")
)

# Plot 7a:
timeline_coronavirus = (
    ggplot(df_coronavirus, aes(x='time_date', y='coronavirus_in_title')) +
    geom_line(color='red', size=1) +
    scale_x_datetime(date_breaks='12 month', date_labels='%b %Y') +
    labs(title="Výskyt slova 'koronavirus' v nadpisech článků", 
         x="Datum", y="Počet zmínek") +
    theme(axis_text_x=element_text(rotation=45, hjust=1))
)

# Plot 7b:
timeline_vaccine = (
    ggplot(df_vaccine, aes(x='time_date', y='vaccine_in_title')) +
    geom_line(color='blue', size=1) +
    scale_x_datetime(date_breaks='12 month', date_labels='%b %Y') +
    labs(title="Výskyt slova 'vakcína' v nadpisech článků", 
         x="Datum", y="Počet zmínek") +
    theme(axis_text_x=element_text(rotation=45, hjust=1))
)

# Plot 8:
histogram_articles_day_of_week = (
    ggplot(df, aes(x='day_of_week_cz')) +
    geom_histogram(stat="count", fill='lightblue', color='black') +
    labs(title="Počet článků v jednotlivých dnech týdne", 
         x="Den týdne", y="Počet článků") +
    theme(axis_text_x=element_text(rotation=45, hjust=1))
)

curve_plot.save("graphs/data_vizualizer/curve_plot.png", dpi=300)
line_graph_years.save("graphs/data_vizualizer/line_graph_years.png", dpi=300)
scatter_plot.save("graphs/data_vizualizer/scatter_plot.png", dpi=300)
histogram_word_count.save("graphs/data_vizualizer/histogram_word_count.png", dpi=300)
histogram_word_length.save("graphs/data_vizualizer/histogram_word_length.png", dpi=300)
timeline_coronavirus.save("graphs/data_vizualizer/timeline_coronavirus.png", dpi=300)
timeline_vaccine.save("graphs/data_vizualizer/timeline_vaccine.png", dpi=300)
histogram_articles_day_of_week.save("graphs/data_vizualizer/histogram_articles_day.png", dpi=300)

print("All plots have been successfully saved.")
