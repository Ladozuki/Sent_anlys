# Bi-Weekly Freight Market Insights

## Overview

This project provides an end-to-end pipeline for analyzing maritime freight market trends. The system integrates **news sentiment analysis**, **macroeconomic data collection**, and **freight rate modeling** to generate actionable insights for the maritime industry. The output includes data visualizations, PDF reports, and a dashboard for interactive exploration.

## Project Structure




## Features

1. **Data Collection**:
   - Fetches maritime-related news articles using the **NewsAPI**.
   - Collects macroeconomic indicators (e.g., oil prices, trade volumes) from **Alpha Vantage**.

2. **Sentiment Analysis**:
   - Analyzes the sentiment of news articles using **VADER**.
   - Classifies articles as positive, neutral, or negative.

3. **Freight Rate Modeling**:
   - [Planned] Predicts freight rates based on sentiment and macroeconomic data.

4. **Report Generation**:
   - Generates PDF summaries with data insights and visualizations.

5. **Interactive Dashboard**:
   - [Planned] Provides an interface for exploring trends and predictions.

## Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL (for database storage)
- Virtual environment (recommended)

### Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd bi_weekly_report
