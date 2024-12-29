from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database URL with client encoding
DATABASE_URL = "postgresql://postgres:Lazooki1797#@localhost:5432/maritime?options=-c%20client_encoding=UTF8"

# Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def get_session():
    return Session()



# Fetch Freight Rates
# def fetch_freight_rates():
#     url = "https://api.balticexchange.com/rates"  # Replace with the actual API endpoint
#     response = requests.get(url)
#     if response.status_code == 200:
#         rates = response.json()
#         for rate in rates:
#             session.add(FreightRate(route=rate["route"], date=rate["date"], rate=rate["value"]))
#         session.commit()
#         print("Freight rates saved to database.")
#     else:
#         print(f"Error fetching freight rates: {response.status_code} - {response.text}")


# Scheduler for Regular Data Fetching
# def schedule_data_fetching():
#     from apscheduler.schedulers.blocking import BlockingScheduler
#     scheduler = BlockingScheduler()
#     scheduler.add_job(fetch_freight_rates, "interval", days=1)
#     scheduler.add_job(lambda: fetch_news("freight rates", "2024-11-24", "2024-12-22"), "interval", days=1)
#     scheduler.add_job(fetch_oil_prices, "interval", days=1)
#     scheduler.start()

    # Uncomment below to start the scheduler
    # schedule_data_fetching()
