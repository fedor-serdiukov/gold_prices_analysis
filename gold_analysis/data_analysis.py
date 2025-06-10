import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_excel('gold_bank_of_russia.xlsx')
df.columns = ['date', 'price_rub']

df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')

conn = sqlite3.connect('../gold_prices.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS gold_prices (
    date TEXT PRIMARY KEY,
    price_rub REAL
)
''')

df.to_sql('gold_prices', conn, if_exists='replace', index=False)

query = '''
SELECT date, price_rub
FROM gold_prices
ORDER BY date
'''
df = pd.read_sql_query(query, conn)
conn.close()

df['date'] = pd.to_datetime(df['date'])
df['price_change_pct'] = df['price_rub'].pct_change() * 100
df['moving_avg'] = df['price_rub'].rolling(window=365).mean()

sns.set_theme(style="whitegrid")

plt.figure(figsize=(12, 6))
sns.lineplot(data=df, x='date', y='price_rub', label='Цена золота (₽)', marker='o')
sns.lineplot(data=df, x='date', y='moving_avg', label='Скользящее среднее (365 дней)', color='orange')
plt.title('Динамика учетной цены на золото (ЦБ РФ, рубли)')
plt.xlabel('Дата')
plt.ylabel('Цена за грамм (₽)')
plt.xticks(rotation=45)
plt.legend()
plt.show()

df['date_ordinal'] = df['date'].map(pd.Timestamp.toordinal)
plt.figure(figsize=(12, 6))
sns.scatterplot(data=df, x='date_ordinal', y='price_rub', label='Цена золота', alpha=0.5)
sns.regplot(data=df, x='date_ordinal', y='price_rub', scatter=False, label='Линейный тренд', color='red')
plt.xticks(
    ticks=df['date_ordinal'][::len(df)//10],
    labels=df['date'][::len(df)//10].dt.strftime('%Y-%m-%d'),
    rotation=45
)
plt.title('Линейный тренд цены золота')
plt.xlabel('Дата')
plt.ylabel('Цена за грамм (₽)')
plt.legend()
plt.show()

plt.figure(figsize=(12, 6))
sns.histplot(df['price_change_pct'].dropna(), bins=20, kde=True)
plt.title('Распределение дневных процентных изменений цен на золото')
plt.xlabel('Процентное изменение (%)')
plt.ylabel('Частота')
plt.show()