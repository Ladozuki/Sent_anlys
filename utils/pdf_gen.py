from fpdf import FPDF
import pandas as pd
import os
from sqlalchemy import create_engine
from sqlalchemy import text
from datetime import datetime

# Database URL
DATABASE_URL = "postgresql://postgres:Lazooki1797#@localhost:5432/maritime"

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pdf_output_path = os.path.join(BASE_DIR, "../reports/freight_market_insights.pdf")

# Database Connection
engine = create_engine(DATABASE_URL)

class PDFReport(FPDF):
        
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Maritime Per Week", align="C", ln=True)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.ln(5)

    def chapter_body(self, body):
        self.set_font("Arial", "", 8)
        self.multi_cell(0, 8, body)
        self.ln()
        
    # def add_compact_table(self, group_title, dataframe):
    #     self.set_font("Arial", "B", 9)
    #     self.cell(0, 8, group_title, ln=True)

    #     # Add compact rows
    #     self.set_font("Arial", "", 8)
    #     for _, row in dataframe.iterrows():
    #         self.cell(0, 6, f"{row['Route Code']}: {row['Potential Dangote Impact']}", ln=True)
    #     self.ln(5)


    # Add group title
    

    def add_route_section_with_table(self, route_title, dataframe):
        # Add route title
        self.set_font("Arial", "B", 10)
        self.cell(0, 8, route_title, ln=True)
        self.ln(3)

        # Add table headers
        self.set_font("Arial", "B", 9)
        col_widths = [50, 100]  # Adjust column widths
        headers = dataframe.columns.tolist()
        for col, width in zip(headers, col_widths):
            self.cell(width, 8, col, border=1, ln=0, align="C")
        self.ln()

        # Add table rows
        self.set_font("Arial", "", 9)
        for _, row in dataframe.iterrows():
            self.cell(col_widths[0], 8, str(row.iloc[0]), border=1, ln=0, align="C")
            self.cell(col_widths[1], 8, str(row.iloc[1]), border=1, ln=0, align="C")
            self.ln()



    def add_table(self, data):
        # Add table headers
        self.set_font("Arial", "B", 10)
        col_widths = [40, 50, 50, 30]  # Adjust column widths
        for col in data.columns:
            self.cell(col_widths[data.columns.get_loc(col)], 10, col, border=1, ln=0, align="C")
        self.ln()

        # Add table rows
        self.set_font("Arial", "", 10)
        for row in data.itertuples(index=False):
            for col_idx, value in enumerate(row):
                self.cell(col_widths[col_idx], 10, str(value), border=1, ln=0, align="C")
            self.ln()

# Combined data for the table

# Grouped data for the routes
routes_data = {
    "West Coast India to Japan (Naphtha Condensate Exports)": {
        "route_code": "TC12",
        "potential_impact": "Increased competition for Asian markets due to Dangote's export capabilities."
    },
    "West Africa to China (Nigeria Crude Exports)": {
        "route_code": "TD15",
        "potential_impact": "Potential diversion of refined products to Asia, reducing crude exports."
    },
    "West Africa to Europe (Bonny Crude Exports)": {
        "route_code": "TD20",
        "potential_impact": "Shift towards refined products impacting crude shipments to Europe."
    },
    "Middle East Gulf to China (Crude Oil Imports)": {
        "route_code": "TD3C",
        "potential_impact": "Reduced reliance on Middle Eastern crude as Dangote meets regional needs."
    },
    "North African Crude to Europe (Black Sea Crude Exports)": {
        "route_code": "TD6",
        "potential_impact": "Minimal impact as focus shifts to refined product trade."
    },
    "North Sea to Continent (North Sea Shipping)": {
        "route_code": "TD7",
        "potential_impact": "Potential reduction in import demand from Africa due to Dangote's supply."
    },
    "Caribbean to US Gulf (Refined Product Flows)": {
        "route_code": "TD9",
        "potential_impact": "Increased competition in refined products market due to African exports."
    },
    "Middle East Gulf to Japan (Naphtha Condensate)": {
        "route_code": "TC5",
        "potential_impact": "Pressure on Middle Eastern naphtha exports due to alternative supplies."
    },
    "Middle East Gulf to UK (Refined Product Flows)": {
        "route_code": "TC8",
        "potential_impact": "Increased competition for European markets from Dangote refinery."
    },
    "Dangote to East Africa (Refined Products Exports)": {
        "route_code": "TC17",
        "potential_impact": "Establishment of new supply chains to East Africa."
    },
    "A-R-A to West Africa (Refined Product Flows)": {
        "route_code": "TC19",
        "potential_impact": "Reduced imports as Dangote replaces European refined products."
    },
    "CPP A-R-A / West Africa (Intra-African Trade)": {
        "route_code": "TC16",
        "potential_impact": "Enhanced intra-African trade supported by Dangote refinery."
    },
    "US Gulf to Brazil (Sanctions Impact on Shipping)": {
        "route_code": "TC18",
        "potential_impact": "Increased supply competition as African refined products enter market."
    }
}

    
    
    # query = text("""
    #     SELECT * FROM macro_data;
    # """)
    # try:
    #     with engine.connect() as connection:
    #         data = pd.read_sql_query(query, con=connection)
    #         return data
    # except Exception as e:
    #     print(f"Error fetching data from the database: {e}")
    #     return pd.DataFrame()

# Generate PDF Report
def generate_pdf(rundate: datetime.date):
    #fetch dat


    # Initialize PDF
    pdf = PDFReport()
    pdf.add_page()

    # Executive Summary
    pdf.chapter_title("Executive Summary")
    summary = (
        "Dangote Refinery is set to deliver 650,000 barrels daily, ~ 2 mil a month. \n"
        "This will impact the flow of the current ecosystem. Maritime Per Week will track these changes.\n\n"
        "Key Insights:\n"
        "- Freight Rate Trends: Aframax routes for Lagos to Rotterdam rose by 8% in the past two weeks.\n"
        "- VLCC rates for Angola to China dropped by 3%, reflecting lower refinery activity in China.\n"
        "- Sentiment Analysis: Positive sentiment in Angola due to stable governance.\n"
        "- Negative sentiment in Nigeria from political unrest.\n"
        "- Rising crude oil prices ($89/barrel) contributed to increased freight costs."
    )

    
    pdf.chapter_body(summary)

    for route_title, details in routes_data.items():
        df = pd.DataFrame({
            "Route Code": [details["route_code"]],
            "Potential Dangote Impact": [details["potential_impact"]]
        })
        pdf.add_route_section_with_table(route_title, df)


    # pdf.chapter_title("Key Routes")
    # pdf.add_combined_table(combined_data)
    
    #Add data as a table
    pdf.add_table(data)

    #Freight Market Trends
    pdf.chapter_title("Freight Market Trends ")
    trends = (
    "| **Route**             | **Current Rate ($/day)** | **% Change (2 weeks)** |\n"
    "|-----------------------|-------------------------|-------------------------|\n"
    "| Lagos to Rotterdam    | 23,000                 | +8%                    |\n"
)
    pdf.chapter_body("Image will probably go here")

    #Sentiment Analysis
    pdf.chapter_title("Sentiement Analysis")
    
    sentiment = (
    "- **Nigeria:** Negative sentiment driven by port delays and fuel shortages.\n"
    "- **Angola:** Positive sentiment as refinery upgrades increase export capacity."
)
    
    pdf.chapter_body(sentiment)

    
    # Save PDF
    os.makedirs(os.path.dirname(pdf_output_path), exist_ok=True)
    pdf.output(pdf_output_path)
    print(f"PDF report saved to {pdf_output_path}")


if __name__ == "__main__":
    rundate = datetime.today()
    try:
        print("Generating PDF report...")
        generate_pdf(rundate=rundate)
    except Exception as e:
        print(f"Error: {e}")

