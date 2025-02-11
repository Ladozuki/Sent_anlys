import yfinance as yf
import pandas as pd

# List of maritime stocks and commodities
symbols = [
    'FRO', 'GLNG', 'TK', 'CL=F', 'BZ=F', 'STNG', 'GC=F', 'SI=F', 'SHEL.L', 'BP', 'NMM', 'SBLK', 'GSL', 
    'DAC', 'GOGL', 'HO=F', 'BDRY', 'NAT'
]

# Function to fetch data for a given period
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

# Fetch data for 2025 (YTD), 2024, 2023, and 2022
print("Fetching data for 2025 YTD (Jan 1 - Feb 10)...")
data_2025 = fetch_data(symbols, '2025-01-01', '2025-02-10')

print("Fetching data for 2024...")
data_2024 = fetch_data(symbols, '2024-01-01', '2024-12-31')

print("Fetching data for 2023...")
data_2023 = fetch_data(symbols, '2023-01-01', '2023-12-31')

print("Fetching data for 2022...")
data_2022 = fetch_data(symbols, '2022-01-01', '2022-12-31')

# Function to calculate yearly averages
def calculate_yearly_average(data, year):
    return data.groupby('Symbol')['Close'].mean().round(2).reset_index().rename(columns={'Close': f'Average_{year}'})

# Compute yearly averages for 2024, 2023, and 2022
avg_2024 = calculate_yearly_average(data_2024, 2024)
avg_2023 = calculate_yearly_average(data_2023, 2023)
avg_2022 = calculate_yearly_average(data_2022, 2022)

# Compute YTD average for 2025
avg_2025_YTD = calculate_yearly_average(data_2025, 2025)
avg_2025_YTD.rename(columns={'Average_2025': 'Average_2025_YTD'}, inplace=True)

# Merge all data into a single DataFrame
merged_data = (
    data_2025  # Use 2025 YTD as base
    .merge(avg_2025_YTD, on='Symbol', how='left')
    .merge(avg_2024, on='Symbol', how='left')
    .merge(avg_2023, on='Symbol', how='left')
    .merge(avg_2022, on='Symbol', how='left')
)

# Save to CSV
output_file = "maritime_data_2025.csv"
merged_data.to_csv(output_file, index=False)
print(f"Data saved to {output_file}")
