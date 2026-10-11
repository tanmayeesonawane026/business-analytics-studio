# Business Analytics Studio

An automated business analytics platform built with Python and Streamlit that helps users explore datasets, identify data quality issues, clean data, analyse revenue, and generate downloadable business reports.

## Overview

Business Analytics Studio simplifies the initial stages of business data analysis by providing an interactive interface for uploading datasets, reviewing their structure, identifying missing values and duplicates, cleaning data, and exploring business metrics.

## Features

- **Dataset Overview:** View dataset dimensions, duplicate counts, and data previews.
- **Data Quality Analysis:** Review column data types, missing values, unique values, and missing-value percentages.
- **Data Cleaning:** Remove duplicate records, remove rows with missing values, or fill missing values using appropriate strategies.
- **Automated Insights:** Explore basic insights from numeric columns.
- **Revenue Analytics:** Calculate revenue metrics and explore product-level revenue when the required columns are available.
- **Visual Analytics:** View charts and summaries to support business analysis.
- **Downloadable Reports:** Export business analysis summaries as text files and PDF reports.
- **CSV and Excel Support:** Upload CSV and Excel datasets for analysis.

## Technology Stack

- Python
- Streamlit
- Pandas
- ReportLab
- OpenPyXL
- Git and GitHub

## Getting Started

### Prerequisites

- Python installed on your computer
- Git (optional, for cloning the repository)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/tanmayeesonawane026/business-analytics-studio.git
   ```

2. Navigate to the project directory:

   ```bash
   cd business-analytics-studio
   ```

3. Create and activate a virtual environment.

   **Windows PowerShell:**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install the required dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Run the application:

   ```bash
   python -m streamlit run app.py
   ```

6. Open the local URL displayed in your terminal.

## Usage

1. Upload a CSV or Excel dataset.
2. Explore the dataset overview and data quality report.
3. Choose a data cleaning option.
4. Explore available analytics and revenue metrics.
5. Download the generated business report as a text file or PDF.

**Note:** Revenue analytics depend on the columns available in the uploaded dataset. Different datasets may support different analyses.

## Future Enhancements

- Support for more business datasets and analysis types.
- Additional interactive visualisations.
- More flexible data cleaning options.
- Expanded business KPIs and reporting capabilities.

## Author

**Tanmayee Sonawane**

GitHub: [tanmayeesonawane026](https://github.com/tanmayeesonawane026)

---

*Built as a portfolio project to explore practical business analytics and data quality workflows.*

## Screenshots

### Dashboard Overview

![Business Analytics Studio Dashboard](Screenshot 2026-10-11 234754.png)
