import yfinance as yf
import pandas as pd

# List of maritime stocks and commodities
symbols = [
    'FRO', 'GLNG', 'TK', 'CL=F', 'BZ=F', 'STNG', 'GC=F', 'SI=F', 'SHEL.L', 'BP', 'NMM', 'SBLK', 'GSL', 
    'DAC', 'GOGL','HO=F', 'BDRY', 'NAT', 'BZ=F'
]

# Function to fetch data for a given year
def fetch_data(symbols, start_date, end_date):
    data = []
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            hist = hist[['Close']]
            hist.reset_index(inplace=True)
            hist['Symbol'] = symbol
            data.append(hist)
            print(f"Fetched data for {symbol}")
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
    return pd.concat(data) if data else pd.DataFrame()

# Fetch data for 2024, 2023, and 2022
print("Fetching data for 2024...")
data_2024 = fetch_data(symbols, '2024-01-01', '2024-12-31')

print("Fetching data for 2023...")
data_2023 = fetch_data(symbols, '2023-01-01', '2023-12-31')

print("Fetching data for 2022...")
data_2022 = fetch_data(symbols, '2022-01-01', '2022-12-31')

# Calculate yearly averages for 2023 and 2022
def calculate_yearly_average(data, year):
    return data.groupby('Symbol')['Close'].mean().reset_index().rename(columns={'Close': f'Average_{year}'})

avg_2023 = calculate_yearly_average(data_2023, 2023)
avg_2022 = calculate_yearly_average(data_2022, 2022)

# Merge all data into a single DataFrame
merged_data = data_2024.merge(avg_2023, on='Symbol', how='left').merge(avg_2022, on='Symbol', how='left')

# Save to CSV
output_file = "maritime_data_2024.csv"
merged_data.to_csv(output_file, index=False)
print(f"Data saved to {output_file}")
