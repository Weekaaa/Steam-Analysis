import os
from pathlib import Path

import re
import random
import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from wordcloud import WordCloud
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import MaxNLocator

csv_path = os.path.join('data', 'merged_progress.csv')
df = pd.read_csv(csv_path)
print(df.head())

# Check the data types of the columns
print(df.dtypes)

print(f"Original rows: {len(df)}")

# Filter str cols to only include english letters, digits, whitespace, and common punctuation
filtration_pattern = r"^[\w\s:\-\.,!\?()'\";]+$"
cleaned = df[df['name'].str.match(filtration_pattern, na=False)]
cleaned = cleaned[cleaned['developers'].str.match(filtration_pattern, na=False)]
cleaned = cleaned[cleaned['publishers'].str.match(filtration_pattern, na=False)]

print(f"Cleaned rows: {len(cleaned)}")

cleaned = cleaned.copy() # make a full independent copy to avoid errors (e.g. SettingWithCopyWarning)

# Convert 'release_date' to datetime, coercing errors to NaT (Not a Time)
cleaned['release_date'] = pd.to_datetime(cleaned['release_date'], errors='coerce')

today = pd.Timestamp.today()

# Check for games with a release date in the future or NaT
unreleased = cleaned['release_date'].isna() | (cleaned['release_date'] > today)
print(f"Number of unreleased games: {unreleased.sum()}")

cutoff_date = pd.Timestamp('2026-01-01')
outliers = cleaned['release_date'].isna() | (cleaned['release_date'] > cutoff_date)
cleaned = cleaned[outliers == False]

print(f"Rows after removing outliers: {len(cleaned)}, with {outliers.sum()} outliers removed")

# list of columns that contain lists of items
list_cols = ['developers', 'publishers', 'tags', 'platforms']

for col in list_cols:
    cleaned[col] = cleaned[col].fillna('')  # Fill NaN with empty string
    cleaned[col] = cleaned[col].apply(lambda x: [item.strip() for item in x.split(',') if item.strip()])

# samples to check the cleaned data
for col in list_cols:
    print(f"{col} sample: {cleaned[col].sample(3).tolist()}")

# w la msh ha7oto f nafs el for loop keda shaklo a7la

owners_split = (
    cleaned['owners']
    .fillna('')
    .str.replace(',', '')
    .str.split(r" *\.\. *", expand=True)
)
cleaned['min_owners'] = pd.to_numeric(owners_split[0], errors='coerce').fillna(0).astype(int)
cleaned['max_owners'] = pd.to_numeric(owners_split[1], errors='coerce').fillna(0).astype(int)

cleaned['estimated_owners'] = cleaned.apply(
    lambda game: random.randint(game['min_owners'], game['max_owners']) if game['max_owners'] > 0 else pd.NA,
    axis=1 # means we are working on rows
).astype('Int64')  # use 'Int64' to allow NA values

# return the number of games with no owners data available
missing_owners_count = cleaned['estimated_owners'].isna().sum()
print(f"Games with no owners data available: {missing_owners_count}")

def extract_currency_only(price):
    if pd.isna(price):
        return 'USD'
    
    return ''.join(c for c in str(price) if not c.isdigit() and c != '.').strip() or 'USD'

# create a set of all unique currency symbols
currency_set = set(cleaned['price'].apply(extract_currency_only).dropna().unique())
print("Currencies found in price column:", currency_set)

# Current conversion rates to USD 
currency_to_usd = {
    'CDN$': 0.72,
    ',€': 1.14,
    '₹ ,': 0.012,
    'R$ ,': 0.18,
    ',zł': 0.27,
    'руб': 0.012,
    'Rp': 0.00006,
    'RM': 0.23
}

def convert_price(price_str):
    if pd.isna(price_str):
        return 0.00
    
    for symbol, rate in currency_to_usd.items():

        if symbol in price_str:

            number = re.sub(r'[^\d\.]', '', price_str)
            try: return round(float(number) * rate, 2)
            except ValueError: return 0.00
            

    # if we dont encounter any of the symbols, we assume its already in USD
    number = re.sub(r'[^\d\.]', '', price_str)
    try: return round(float(number), 2)
    except ValueError: return 0.00


cleaned['price'] = cleaned['price'].apply(convert_price)

print(cleaned['price'].sample(20).tolist())

plt.figure(figsize=(18, 6))
sns.boxplot(x=cleaned['price'], color='skyblue', width=0.5)

plt.title('Price Distribution of Games', fontsize=30)
plt.xlabel('Price (USD)', fontsize=20)
plt.xticks(fontsize=12)
plt.tight_layout()
plt.show()


Q1 = cleaned['price'].quantile(0.25)
Q3 = cleaned['price'].quantile(0.75)
IQR = Q3 - Q1 

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers_count = cleaned[(cleaned['price'] < lower_bound) | (cleaned['price'] > upper_bound)].shape[0]

print(f"Number of outliers: {outliers_count}")

cleaned = cleaned[(cleaned['price'] >= lower_bound) & (cleaned['price'] <= upper_bound)]

print(f"Rows after removing outliers: {len(cleaned)}")


cleaned['total_reviews'] = cleaned['positive_reviews'] + cleaned['negative_reviews']
cleaned['positive_pct'] = (cleaned['positive_reviews'] / cleaned['total_reviews'].replace(0, pd.NA) * 100).astype('Float64').round(2) # use 'Float64' to allow NA values

# this is a function that calculates the review summary just...
# ... the way steam calculates it.
def get_review_summary(row):
    total = row['total_reviews']
    pct = row['positive_pct'] if not pd.isna(row['positive_pct']) else 0

    if total == 0:
        return 'No Reviews'

    if total >= 500:
        if pct >= 95:
            return 'Overwhelmingly Positive'
        if pct >= 80:
            return 'Very Positive'
        if pct >= 70:
            return 'Mostly Positive'
        if pct >= 40:
            return 'Mixed'
        if pct >= 20:
            return 'Mostly Negative'
        return 'Overwhelmingly Negative'

    if total >= 50:
        if pct >= 80:
            return 'Very Positive'
        if pct >= 70:
            return 'Mostly Positive'
        if pct >= 40:
            return 'Mixed'
        if pct >= 20:
            return 'Mostly Negative'
        return 'Very Negative'

    if total >= 10:
        if pct >= 80:
            return 'Positive'
        if pct >= 70:
            return 'Mostly Positive'
        if pct >= 40:
            return 'Mixed'
        if pct >= 20:
            return 'Mostly Negative'
        return 'Negative'


    return 'Too Few Reviews'

cleaned['review_summary'] = cleaned.apply(get_review_summary, axis=1)
print(f"Review summary counts:\n{cleaned['review_summary'].value_counts()}")

print(cleaned.dtypes)

# === VISUALIZATION === #
df_viz = cleaned.copy()

free_games = df_viz[df_viz['is_free'] == True]
paid_games = df_viz[df_viz['is_free'] == False]

# Count of free and paid games
free_games_count = len(free_games)
paid_games_count = len(paid_games)

# Total estimated owners
free_owners_total = free_games['estimated_owners'].sum(skipna=True)
paid_owners_total = paid_games['estimated_owners'].sum(skipna=True)

game_counts = pd.Series([free_games_count, paid_games_count], index=['Free', 'Paid'])
owner_totals = pd.Series([free_owners_total, paid_owners_total], index=['Free', 'Paid'])

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

def format_large_numbers_int(x, pos):
    if x >= 1e6:
        return f'{int(x/1e6)}M'
    elif x >= 1e3:
        return f'{int(x/1e3)}K' 
    else:
        return f'{int(x)}' 
    
# Subplot 1: Bar chart - Count of Free vs Paid Games
axes[0].bar(['Free', 'Paid'], game_counts, color=['sandybrown', 'cyan'], edgecolor='black')
axes[0].set_title('Count of Free vs Paid Games', fontsize=20)
axes[0].set_xlabel('Game Type', fontsize=17)
axes[0].set_ylabel('Number of Games', fontsize=17)
axes[0].yaxis.set_major_formatter(FuncFormatter(format_large_numbers_int))

# Subplot 2: Pie chart - Share of Free vs Paid Games
axes[1].pie(
    game_counts,
    labels=['Free', 'Paid'],
    autopct='%1.1f%%',
    startangle=90,
    colors=['sandybrown', 'cyan'],
    wedgeprops={'edgecolor': 'black'}
)
axes[1].set_title('Free vs Paid Games', fontsize=20)
axes[1].set_ylabel('')

# Subplot 3: Bar chart - Total Estimated Owners
axes[2].bar(['Free', 'Paid'], owner_totals, color=['sandybrown', 'cyan'], edgecolor='black')
axes[2].set_title('Total Number of Estimated Owners', fontsize=20)
axes[2].set_xlabel('Game Type', fontsize=17)
axes[2].set_ylabel('Estimated Owners Count', fontsize=17)
axes[2].yaxis.set_major_formatter(FuncFormatter(format_large_numbers_int))

plt.tight_layout()
plt.show()

owners_ratio = free_owners_total / paid_owners_total
type_ratio = free_games_count / paid_games_count
print(f"Ratio of Free games Owners to Paid games Owners: {owners_ratio:.4f}")
print(f"Ratio of Free games to Paid games: {type_ratio:.4f}")


# Explode the 'platforms' column to separate multiple platforms into individual...
# ... rows, this will be done frequently in the rest of the visualizations.
platform_counts = df_viz.explode('platforms')['platforms'].value_counts()

plt.figure()
platform_counts.plot.pie(
    autopct='%1.1f%%', 
    title='Game Distribution Across Platforms',
    colors=['deepskyblue', 'silver', 'gold'],
    wedgeprops={'edgecolor': 'black'}
)

plt.ylabel('')
plt.show()

# Filter out games with 'No Reviews' or 'Too Few Reviews' and count the review summaries
review_counts = df_viz.loc[df_viz['review_summary'].isin(['No Reviews', 'Too Few Reviews']) == False, 'review_summary'].value_counts()

plt.figure(figsize=(16, 8))
review_counts.plot.bar(color='goldenrod', edgecolor='black')

plt.title('Distribution of Review Summaries', fontsize=30)
plt.xlabel('Review Summary', fontsize=20)
plt.ylabel('Count', fontsize=20)
plt.xticks(rotation=0, fontsize=12)

plt.tight_layout()
plt.show()


top_developers = (
    df_viz.explode('developers')
    .groupby('developers')['estimated_owners']
    .sum()
    .nlargest(10)
)

plt.figure(figsize=(16, 8))
top_developers.plot.bar(color='violet', edgecolor='black')

plt.title('Top 10 Developers by Estimated Owners', fontsize=30)
plt.xlabel('Developer', fontsize=20)
plt.ylabel('Estimated Owners', fontsize=20)
plt.xticks(rotation=30, fontsize=12)
plt.gca().yaxis.set_major_formatter(FuncFormatter(format_large_numbers_float))
plt.ylim(1.7e6)

plt.tight_layout()
plt.show()


def format_large_numbers_float(x, pos):
    if x >= 1e6:
        return f'{x/1e6}M'
    elif x >= 1e3:
        return f'{x/1e3}K' 
    else:
        return f'{x}' 

top_games = (
    df_viz[['name', 'estimated_owners']]
    .dropna()
    .nlargest(20, 'estimated_owners')
    .set_index('name')['estimated_owners']
)

plt.figure(figsize=(16, 8))
top_games.plot.bar(color='mediumseagreen', edgecolor='black')

plt.title('Top 20 Games by Estimated Owners Count', fontsize=30)
plt.xlabel('Game Name', fontsize=20)
plt.ylabel('Estimated Owners Count', fontsize=14)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.gca().yaxis.set_major_formatter(FuncFormatter(format_large_numbers_float))
plt.ylim(1.e6)

plt.tight_layout()
plt.show()


exploded_platforms = df_viz.explode('platforms').reset_index(drop=True)

platform_free_paid = pd.crosstab(
    exploded_platforms['platforms'],
    exploded_platforms['is_free']
)

# Plot the stacked bar chart
plt.figure(figsize=(12, 6))

platform_free_paid.plot.bar(
    stacked=True,
    color=['lightcoral', 'mediumseagreen'],
    edgecolor='black'
)

plt.title('Game Type by Platform', fontsize=22)
plt.xlabel('Platform', fontsize=17)
plt.ylabel('Count', fontsize=18)
plt.legend(['Paid', 'Free'], fontsize=12)
plt.xticks(rotation=0, fontsize=14)
plt.gca().yaxis.set_major_formatter(FuncFormatter(format_large_numbers_int))

plt.tight_layout()
plt.show()


plt.figure(figsize=(15, 8))
vis1 = df_viz.dropna(subset=['estimated_owners'])

plt.scatter(vis1['price'], vis1['estimated_owners'], alpha=0.6, color='royalblue', edgecolors='w', linewidths=0.5)
plt.title('Estimated Owners vs Price', fontsize=30)
plt.xlabel('Price (USD)', fontsize=20)
plt.ylabel('Estimated Owners', fontsize=20)
plt.gca().yaxis.set_major_formatter(FuncFormatter(format_large_numbers_float))

plt.tight_layout()
plt.show()


plt.figure(figsize=(15, 8))
paid = df_viz[(df_viz['is_free'] == False) & (df_viz['positive_pct'] > 0)]

plt.scatter(paid['price'], paid['positive_pct'], alpha=0.6, color='darkorange', edgecolors='w', linewidths=0.5)
plt.title('Review Positivity vs Price (Paid Games)', fontsize=30)
plt.xlabel('Price (USD)', fontsize=20)
plt.ylabel('Positive Review %', fontsize=20)

plt.tight_layout()
plt.show()


plt.figure(figsize=(20, 5))
avg_price = df_viz.groupby(df_viz['release_date'].dt.to_period('M'))['price'].mean()
avg_price.plot(color='mediumvioletred')

plt.title('Average Game Price Over Time', fontsize=30)
plt.xlabel('Timeline', fontsize=20)
plt.ylabel('Average Price (USD)', fontsize=20) 
plt.xticks(rotation=0, fontsize=10)

plt.tight_layout()
plt.show()


plt.figure(figsize=(18, 9))
all_tags = ' '.join(df_viz.explode('tags')['tags'].dropna())
wordcloud = WordCloud(width=1600, height=800, background_color='white').generate(all_tags)

plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Word Cloud of Tags', fontsize=30)

plt.tight_layout()
plt.show()


plt.figure(figsize=(8, 6))
corr = df_viz[['price', 'estimated_owners', 'positive_reviews', 'negative_reviews', 'positive_pct']].corr()

plt.imshow(corr, cmap='coolwarm', aspect='auto')
plt.colorbar()
plt.xticks(range(len(corr)), corr.columns, rotation=45, fontsize=12)
plt.yticks(range(len(corr)), corr.columns, fontsize=12)
plt.title('Correlation Heatmap', fontsize=25)

plt.tight_layout()
plt.show()


cleaned['release_month'] = cleaned['release_date'].dt.to_period('M').dt.to_timestamp()

filtered = cleaned[
    (cleaned['release_month'] >= '2016-01') &
    (cleaned['release_month'] <= '2026-12')
]

plt.figure(figsize=(16, 8))
plt.hist(filtered['release_month'], bins=100, edgecolor='black')
plt.title('Games Released Over Time (2016–2026)')
plt.xlabel('Year')
plt.ylabel('Game Count')

plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()


plt.figure(figsize=(16, 9))
vis2 = df_viz.dropna(subset=['estimated_owners', 'positive_pct'])
sizes = vis2['price'].clip(lower=1) * 10  # avoid size 0 

plt.scatter(vis2['estimated_owners'], vis2['positive_pct'], s=sizes, alpha=0.5, c='mediumturquoise', edgecolors='w', linewidths=0.5)
plt.title('Owners vs Review Positivity (Bubble size = Price)', fontsize=30)
plt.xlabel('Estimated Owners', fontsize=20)
plt.ylabel('Positive Review %', fontsize=20)
plt.yscale('log')
plt.gca().xaxis.set_major_formatter(FuncFormatter(format_large_numbers_int))

plt.tight_layout()
plt.show()