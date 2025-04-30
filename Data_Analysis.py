import re
import random
import pandas as pd
from pathlib import Path
import os

# Read file and take a looksie
csv_path = os.path.join('data', 'merged_progress.csv')
df = pd.read_csv(csv_path)
print(df.head())


# Check the data types of the columns
print(df.dtypes)


# 1) Removing all games with weird characters
print(f"Original rows: {len(df)}")

# Filter str cols to only include english letters, digits, whitespace, and common punctuation
filtration_pattern = r"^[\w\s:\-\.,!\?()'\";]+$"
cleaned = df[df['name'].str.match(filtration_pattern, na=False)]
cleaned = cleaned[cleaned['developers'].str.match(filtration_pattern, na=False)]
cleaned = cleaned[cleaned['publishers'].str.match(filtration_pattern, na=False)]

print(f"Cleaned rows: {len(cleaned)}")


# 2) Fixing the release date format
cleaned = cleaned.copy() # make a full independent copy to avoid errors (e.g. SettingWithCopyWarning)

# Convert 'release_date' to datetime, coercing errors to NaT (Not a Time)
cleaned['release_date'] = pd.to_datetime(cleaned['release_date'], errors='coerce')

today = pd.Timestamp.today()

# Check for games with a release date in the future or NaT
unreleased = cleaned['release_date'].isna() | (cleaned['release_date'] > today)
print(f"Number of unreleased games: {unreleased.sum()}")


# 3) Fix columns that have lists of items
# list of columns that contain lists of items
list_cols = ['developers', 'publishers', 'tags', 'platforms']

for col in list_cols:
    cleaned[col] = cleaned[col].fillna('')  # Fill NaN with empty string
    cleaned[col] = cleaned[col].apply(lambda x: [item.strip() for item in x.split(',') if item.strip()])

# samples to check the cleaned data
for col in list_cols:
    print(f"{col} sample: {cleaned[col].sample(3).tolist()}")

# w la msh ha7oto f nafs el for loop keda shaklo a7la


# 3) Making useful columns that describe the owners count
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


# 4) Extracting the currency from the price column to fix 
def extract_currency_only(price):
    if pd.isna(price):
        return 'USD'
    
    return ''.join(c for c in str(price) if not c.isdigit() and c != '.').strip() or 'USD'

# create a set of all unique currency symbols
currency_set = set(cleaned['price'].apply(extract_currency_only).dropna().unique())
print("Currencies found in price column:", currency_set)

#Current conversion rates to USD 
currency_to_usd = {
    'CDN$': 0.72,  # Canadian Dollar
    ',€': 1.14,    # Euro
    '₹ ,': 0.012,  # Indian Rupee
    'R$ ,': 0.18,  # Brazilian Real
    ',zł': 0.27,   # Polish Zloty
    'руб': 0.012,  # Russian Ruble
    'Rp': 0.00006, # Indonesian Rupiah
    'RM': 0.23     # Malaysian Ringgit
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


# 5) Assign each game their appropriate review summary
# this is a function that calculates the review summary just...
# ... the way steam calculates it.
def get_review_summary(game):
    total_reviews = game['positive_reviews'] + game['negative_reviews']
    if total_reviews == 0:
        return 'No Reviews'
    
    # percentage of positive reviews
    positive_pct = 100 * game['positive_reviews'] / total_reviews

    # could check for the percentage first then the total reviews...
    # ... but i like this way better toz fik.
    if total_reviews >= 500:
        if positive_pct >= 95:
            return 'Overwhelmingly Positive'
        elif positive_pct >= 80:
            return 'Very Positive'
        elif positive_pct >= 70:
            return 'Mostly Positive'
        elif positive_pct >= 40:
            return 'Mixed'
        elif positive_pct >= 20:
            return 'Mostly Negative'
        else:
            return 'Overwhelmingly Negative'
        
    elif total_reviews >= 50:
        if positive_pct >= 80:
            return 'Very Positive'
        elif positive_pct >= 70:
            return 'Mostly Positive'
        elif positive_pct >= 40:
            return 'Mixed'
        elif positive_pct >= 20:
            return 'Mostly Negative'
        else:
            return 'Very Negative'

    elif total_reviews >= 10:
        if positive_pct >= 80:
            return 'Positive'
        elif positive_pct >= 70:
            return 'Mostly Positive'
        elif positive_pct >= 40:
            return 'Mixed'
        elif positive_pct >= 20:
            return 'Mostly Negative'
        else:
            return 'Negative'
    
    return 'Too Few Reviews'

cleaned['review_summary'] = cleaned.apply(get_review_summary, axis=1)
print(f"Review summary counts:\n{cleaned['review_summary'].value_counts()}")


# Final look at the data types of the columns
print(cleaned.dtypes)