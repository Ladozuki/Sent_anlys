# utils/pdf_gen.py
from fpdf import FPDF
import pandas as pd
import os
import matplotlib.pyplot as plt

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR, "../merged.csv")  # Updated to merged data
pdf_output_path = os.path.join(BASE_DIR, "../reports/freight_market_insights.pdf")

class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Freight Market Insights", align="C", ln=True)
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
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_chart(self, chart_path):
        self.image(chart_path, x=10, w=190)
        self.ln(10)

# Generate Charts
def generate_chart(df, feature, output_path):
    if feature not in df.columns:
        print(f"Feature '{feature}' not found in dataset. Skipping chart generation.")
        return False  # Indicate failure

    plt.figure(figsize=(10, 6))
    for vessel_type, group in df.groupby("Vessel Type"):
        plt.plot(group["Charter Date"], group[feature], label=vessel_type)
        plt.xlabel("Date")
        plt.ylabel(feature)
        plt.title(f"{feature} Trends")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        return True  # Indicate success


# Generate PDF Report
def generate_pdf():
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")

    # Load Data
    df = pd.read_csv(data_path)

    # Preprocessing for Charts
    if "Charter Date" in df.columns:
        df["Charter Date"] = pd.to_datetime(df["Charter Date"])
    else:
        print("Column 'Charter Date' not found in dataset. Skipping date conversion.")

    # Initialize PDF
    pdf = PDFReport()
    pdf.add_page()

    # Executive Summary
    pdf.chapter_title("Executive Summary")
    summary = (
        "This report provides an overview of the freight market trends, including "
        "charter prices, demand-supply dynamics, and sentiment analysis insights "
        "based on recent data."
    )
    pdf.chapter_body(summary)

    # Add Charts
    charts = {
        "Charter Price ($/day)": "../reports/charter_price_trend.png",
        "Sentiment Score": "../reports/sentiment_trend.png",
    }

    for feature, chart_path in charts.items():
        chart_path_full = os.path.join(BASE_DIR, chart_path)
        success = generate_chart(df, feature, chart_path_full)
        if success:
            pdf.chapter_title(f"{feature} Trends")
            pdf.add_chart(chart_path_full)
        else:
            pdf.chapter_body(f"Feature '{feature}' not found. Skipping chart.")

    # Save PDF
    os.makedirs(os.path.dirname(pdf_output_path), exist_ok=True)
    pdf.output(pdf_output_path)
    print(f"PDF report saved to {pdf_output_path}")


if __name__ == "__main__":
    try:
        print("Generating PDF report...")
        generate_pdf()
    except Exception as e:
        print(f"Error: {e}")
