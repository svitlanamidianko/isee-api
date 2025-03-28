import pandas as pd

# Read the current cards.csv
df = pd.read_csv('data/cards.csv')

# Use localhost for local development
deployed_url = 'http://localhost:7777'
df['image_path'] = df['image_path'].str.replace('http://localhost:7777', deployed_url)

# Save the updated CSV
df.to_csv('data/cards.csv', index=False) 