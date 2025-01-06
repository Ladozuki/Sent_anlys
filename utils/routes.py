from sqlalchemy.orm import Session
from Sent_anlys.database.db_config import engine
from Sent_anlys.database.db_models import Route

# Define the data to be inserted

data = [
    ('TD2', 'Middle East Gulf to Singapore (Ras Tanura to Singapore).', '20/30 days', 'Crude Oil', 270000, 15, 3.75, True),
    ('TD3C', 'Middle East Gulf to China (Ras Tanura to Ningbo).', '15/30 days', 'Crude Oil', 270000, 15, 3.75, True),
    ('TD6', 'Black Sea to Mediterranean (CPC to Augusta).', '10/15 days', 'Crude Oil', 135000, 15, 3.75, True),
    ('TD7', 'North Sea to Continent (Hound Point to Wilhelmshaven).', '7/14 days', 'Crude Oil', 80000, 15, 3.75, True),
    ('TD8', 'crude and/or DPP, heat 135F. Kuwait to Singapore (Mina Al Ahmadi to Singapore).', '20/25 days', 'Crude Oil', 80000, 15, 3.75, True),
    ('TD9', 'Caribbean to US Gulf (Covenas to Corpus Christi).', '7/14 days', 'Crude Oil', 70000, 15, 3.75, True),
    ('TD14', 'South East Asia to east coast Australia (Seria to Brisbane).', '21/25 days', 'Crude Oil', 80000, 15, 3.75, True),
    ('TD15', 'West Africa to China (Serpentina FPSO and Bonny Offshore Terminal to Ningbo).', '20/30 days', 'Crude Oil', 260000, 15, 3.75, True),
    ('TD18', 'fuel oil. Baltic to UK-Cont (Tallinn to Amsterdam).', '10/15 days', 'Fuel Oil', 30000, 15, 3.75, True),
    ('TD19', 'Cross Mediterranean (Ceyhan to Lavera).', '10/15 days', 'Crude Oil', 80000, 15, 3.75, True),
    ('TD20', 'West Africa to UK-Continent (Bonny to Rotterdam).', '15/20 days', 'Crude Oil', 130000, 15, 3.75, True),
    ('TD21', 'fuel oil, Caribbean to US Gulf (Mamonal to Houston).', '7/14 days', 'Fuel Oil', 50000, 15, 3.75, True),
    ('TD22', 'crude Galveston O/S lightering area to Ningbo.', '25/35 days', 'Crude Oil', 270000, 15, 3.75, True),
    ('TD23', 'Light crude Basrah to Lavera.', '20/30 days', 'Crude Oil', 140000, 15, 3.75, True),
    ('TD25', 'crude Corpus Christi-Beaumont / A-R-A (Houston to Rotterdam).', '10/20 days', 'Crude Oil', 70000, 15, 3.75, True),
    ('TD26', 'EC Mexico to US Gulf (Dos Bocas or Cayo Arcas to Houston).', '5/10 days', 'Crude Oil', 70000, 15, 3.75, True),
    ('TC1', 'CPP/naphtha condensate. Middle East Gulf to Japan (Ras Tanura to Yokohama).', '30/35 days', 'Clean Petroleum Products', 75000, 15, 3.75, True),
    ('TC2', 'CPP/UNL. Continent to US Atlantic coast (Rotterdam to New York).', '10/14 days', 'Clean Petroleum Products', 37000, 15, 3.75, True),
    ('TC5', 'CPP/UNL naphtha condensate. Middle East Gulf to Japan (Ras Tanura to Yokohama).', '30/35 days', 'Clean Petroleum Products', 55000, 15, 3.75, True),
    ('TC6', 'CPP/UNL. Algeria to European Mediterranean (Skikda to Lavera).', '7/14 days', 'Clean Petroleum Products', 30000, 15, 3.75, True),
    ('TC7', 'CPP. Singapore to east coast Australia (Singapore to Sydney).', '17/23 days', 'Clean Petroleum Products', 35000, 15, 3.75, True),
    ('TC8', 'CPP/UNL middle distillate. Middle East Gulf to UK-Cont (Jubail to Rotterdam).', '20/30 days', 'Clean Petroleum Products', 65000, 15, 3.75, True),
    ('TC10', 'CPP/UNL. South Korea to west coast North Pacific (South Korea to Vancouver).', '14/21 days', 'Clean Petroleum Products', 40000, 15, 3.75, True),
    ('TC11', 'CPP. South Korea to Singapore.', '10/17 days', 'Clean Petroleum Products', 40000, 15, 3.75, True),
    ('TC12', 'naphtha condensate. West coast India to Japan (Sikka to Chiba).', '7/14 days', 'Clean Petroleum Products', 35000, 15, 3.75, True),
    ('TC14', 'CPP/UNL/diesel. US Gulf to Continent (Houston to Amsterdam).', '6/12 days', 'Clean Petroleum Products', 38000, 15, 3.75, True),
    ('TC15', 'naphtha. Med / Far East (Skikda to Chiba).', '15/25 days', 'Clean Petroleum Products', 80000, 15, 3.75, True),
    ('TC16', 'CPP. A-R-A / West Africa (Amsterdam to Lome).', '10/14 days', 'Clean Petroleum Products', 60000, 15, 3.75, True),
    ('TC17', 'CPP. Jubail to Dar es Salaam.', '10/20 days', 'Clean Petroleum Products', 35000, 15, 3.75, True),
    ('TC18', 'CPP/UNL US Gulf to Brazil (Houston to Santos).', '6/12 days', 'Clean Petroleum Products', 38000, 15, 3.75, True),
    ('TC19', 'CPP, A-R-A to West Africa (Amsterdam to Lagos).', '5/10 days', 'Clean Petroleum Products', 37000, 15, 3.75, True),
    ('TC20', 'CPP/UNL middle distillate. Middle East Gulf to UK-Cont (Jubail to Rotterdam).', '15/20 days', 'Clean Petroleum Products', 90000, 15, 3.75, True),
    ('TC21', 'CPP US Gulf to Caribbean (Houston to Pozos Colorados).', '5/10 days', 'Clean Petroleum Products', 38000, 15, 3.75, True),
    ('TC22', 'CPP/UNL. South Korea to Australia (Yeosu to Botany Bay).', '17/23 days', 'Clean Petroleum Products', 35000, 15, 3.75, True),
    ('TC23', 'CPP/UNL/ULSD middle distillate. ARA to UK-Cont (Amsterdam to Le Havre).', '5/10 days', 'Clean Petroleum Products', 30000, 15, 3.75, True),
]


# Create a session
session = Session(bind=engine)

try:
    # Insert data into the route table
    for row in data:
        route = Route(
            route=row[0],
            description=row[1],
            laydays=row[2],
            cargo_type=row[3],
            volume=row[4],
            hull_type=row[5],
            age_max=row[6],
            commission=float(row[7])
        )
        session.add(route)
    
    # Commit the transaction
    session.commit()
    print("Data inserted successfully into routes table.")
except Exception as e:
    print(f"Error inserting data: {e}")
    session.rollback()  # Rollback in case of error
finally:
    session.close()


