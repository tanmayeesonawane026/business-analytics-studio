import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(
    page_title="Business Analytics Studio",
    page_icon="📊",
    layout="wide",
)



st.title("Business Analytics Studio")
st.markdown(
    "<div style='height:4px; width:70px; "
    "background:#3B82F6; border-radius:4px; "
    "margin-top:-8px; margin-bottom:16px;'></div>",
    unsafe_allow_html=True
)
st.caption(
    "Upload your business data, assess data quality, "
    "clean datasets, and discover useful insights."
)
st.divider()

uploaded_file = st.file_uploader(
    "Upload a CSV or Excel file",
    type=["csv", "xlsx"],
)

with st.sidebar:
    st.title("Navigation")
    st.caption("Business Analytics Studio")
    st.divider()

    selected_section = st.radio(
        "Go to section",
        [
            "Dataset Overview",
            "Data Quality",
            "Data Cleaning",
            "Analytics",
        ],
    )

    st.divider()
    st.subheader("Dataset Status")
    if uploaded_file is not None:
        st.success("File uploaded")
        st.caption(f"File: {uploaded_file.name}")
    else:
        st.info("Upload a file to begin.")

if uploaded_file is None:
    st.info("Upload a CSV or Excel file to get started.")
    st.stop()

if st.session_state.get("current_file") != uploaded_file.name:
    st.session_state["current_file"] = uploaded_file.name
    st.session_state.pop("cleaned_df", None)
    st.session_state.pop("removed_duplicates", None)
    st.session_state.pop("original_rows", None)
    st.session_state.pop("cleaning_option", None)

try:
    if uploaded_file.name.lower().endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Could not read the uploaded file: {e}")
    st.stop()

if df.empty:
    st.warning("The uploaded file has no data rows.")
    st.stop()

st.success("File uploaded successfully!")

numeric_columns = df.select_dtypes(include="number").columns.tolist()

date_columns = []
for column in df.columns:
    name_suggests_date = (
        "date" in str(column).lower()
        or "time" in str(column).lower()
    )
    if not name_suggests_date:
        continue

    parsed_dates = pd.to_datetime(df[column], errors="coerce")
    if df[column].notna().any() and parsed_dates.notna().mean() >= 0.8:
        date_columns.append(column)

categorical_columns = [
    column
    for column in df.select_dtypes(
        include=["object", "category", "string"]
    ).columns.tolist()
    if column not in date_columns
]

if selected_section == "Dataset Overview":
    st.header("1. Dataset Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rows", f"{len(df):,}")
    col2.metric("Total Columns", f"{len(df.columns):,}")
    col3.metric("Duplicate Rows", f"{df.duplicated().sum():,}")

    st.subheader("Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    st.header("Automatic Column Detection")
    col1, col2, col3 = st.columns(3)
    col1.write("**Numeric Columns**")
    col1.write(numeric_columns or "None found")
    col2.write("**Categorical Columns**")
    col2.write(categorical_columns or "None found")
    col3.write("**Likely Date/Time Columns**")
    col3.write(date_columns or "None found")

    st.subheader("Numeric Statistics")
    numeric_df = df.select_dtypes(include="number")
    if not numeric_df.empty:
        st.dataframe(numeric_df.describe().T.round(2), use_container_width=True)
    else:
        st.info("No numeric columns found in this dataset.")

elif selected_section == "Data Quality":
    st.header("Data Quality Report")
    quality_report = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Missing Values": df.isna().sum().values,
        "Missing (%)": df.isna().mean().mul(100).round(2).values,
        "Unique Values": df.nunique().values,
    })

    col1, col2, col3 = st.columns(3)
    col1.metric("Missing Cells", f"{int(df.isna().sum().sum()):,}")
    col2.metric("Columns With Missing Values", f"{int(df.isna().any().sum()):,}")
    col3.metric("Duplicate Rows", f"{int(df.duplicated().sum()):,}")

    st.dataframe(quality_report, use_container_width=True)
    st.download_button(
        label="Download Data Quality Report",
        data=quality_report.to_csv(index=False).encode("utf-8"),
        file_name="data_quality_report.csv",
        mime="text/csv",
    )

elif selected_section == "Data Cleaning":
    st.header("Data Cleaning")
    st.write(
        "Exact duplicate rows will be removed automatically. "
        "Choose how you want to handle missing values."
    )

    missing_option = st.selectbox(
        "How should missing values be handled?",
        [
            "Keep missing values",
            "Remove rows with missing values",
            "Fill missing values",
        ],
    )

    if st.button("Clean Data"):
        cleaned_df = df.drop_duplicates().copy()

        if missing_option == "Remove rows with missing values":
            cleaned_df = cleaned_df.dropna()
        elif missing_option == "Fill missing values":
            for column in cleaned_df.columns:
                if cleaned_df[column].isna().any():
                    if pd.api.types.is_numeric_dtype(cleaned_df[column]):
                        mean_value = cleaned_df[column].mean()
                        if pd.notna(mean_value):
                            cleaned_df[column] = cleaned_df[column].fillna(mean_value)
                    else:
                        mode_values = cleaned_df[column].mode()
                        if not mode_values.empty:
                            cleaned_df[column] = cleaned_df[column].fillna(
                                mode_values.iloc[0]
                            )

        st.session_state["cleaned_df"] = cleaned_df
        st.session_state["removed_duplicates"] = len(df) - len(df.drop_duplicates())
        st.session_state["original_rows"] = len(df)
        st.session_state["cleaning_option"] = missing_option

    if "cleaned_df" in st.session_state:
        cleaned_df = st.session_state["cleaned_df"]
        st.subheader("Cleaning Summary")

        col1, col2, col3 = st.columns(3)
        col1.metric("Original Rows", st.session_state["original_rows"])
        col2.metric("Cleaned Rows", len(cleaned_df))
        col3.metric("Duplicates Removed", st.session_state["removed_duplicates"])

        st.caption(
            "Missing-value strategy: "
            + st.session_state.get("cleaning_option", "Not specified")
        )
        st.write("Missing values remaining by column:")
        st.dataframe(
            cleaned_df.isna().sum().rename("Missing Values").to_frame(),
            use_container_width=True,
        )
        st.subheader("Cleaned Data Preview")
        st.dataframe(cleaned_df.head(10), use_container_width=True)
        st.download_button(
            label="Download Cleaned CSV",
            data=cleaned_df.to_csv(index=False).encode("utf-8"),
            file_name="cleaned_data.csv",
            mime="text/csv",
        )

else:  # Analytics
    st.header("Analytics")
    numeric_df = df.select_dtypes(include="number")

    st.subheader("Automatic Insights")
    if not numeric_df.empty:
        for column in numeric_df.columns:
            if numeric_df[column].notna().any():
                st.write(
                    f"**{column}**: Highest value = {numeric_df[column].max()}, "
                    f"Lowest value = {numeric_df[column].min()}"
                )
    else:
        st.info("No numeric columns available for insights.")

    st.divider()
    st.subheader("Revenue Analysis")

    if "price" not in df.columns:
        st.info(
            "Revenue analysis requires columns named 'quantity' and 'price'. "
            "You can still use the other sections with this dataset."
        )
    else:
        
        revenue_df = df.copy()
        revenue_df["price"] = pd.to_numeric(
            revenue_df["price"], errors="coerce"
        )

        if "quantity" in revenue_df.columns:
            revenue_df["quantity"] = pd.to_numeric(
                revenue_df["quantity"], errors="coerce"
            )
            revenue_df["revenue"] = (
                revenue_df["quantity"] * revenue_df["price"]
            )
            total_units = revenue_df["quantity"].sum()
        else:
            revenue_df["revenue"] = revenue_df["price"]
            total_units = len(revenue_df)

        total_revenue = revenue_df["revenue"].sum()
        average_price = revenue_df["price"].mean()
        product_count = (
            revenue_df["product"].nunique()
            if "product" in revenue_df.columns else 0
        )


        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Revenue", f"{total_revenue:,.2f}",
                  help="Sum of quantity multiplied by price across all rows.")
        k2.metric("Units Sold", f"{total_units:,.0f}",
                  help="Total quantity sold across all rows.")
        k3.metric("Average Price",
                  f"{average_price:,.2f}" if pd.notna(average_price) else "N/A",
                  help="Average value in the price column.")
        k4.metric("Unique Products", f"{product_count:,}",
                  help="Number of distinct product names, if a product column exists.")

        if "product" in revenue_df.columns:
            st.subheader("Revenue by Product")
            product_revenue = (
                revenue_df.groupby("product", dropna=False)["revenue"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )
            st.dataframe(product_revenue, use_container_width=True)
            st.caption("Compare total revenue generated by each product, ranked from highest to lowest.")
            st.bar_chart(product_revenue.set_index("product")["revenue"])
        else:
            st.info("Add a 'product' column to see revenue by product.")

        if "order_date" in revenue_df.columns:
            trend_df = revenue_df.copy()
            trend_df["order_date"] = pd.to_datetime(trend_df["order_date"], errors="coerce")
            trend_df = trend_df.dropna(subset=["order_date"])
            if not trend_df.empty:
                daily_revenue = (
                    trend_df.groupby(trend_df["order_date"].dt.date)["revenue"]
                    .sum()
                    .reset_index()
                )
                daily_revenue.columns = ["Date", "Revenue"]
                st.subheader("Sales Trend Over Time")
                st.caption("Track how total revenue changes across dates in the uploaded dataset.")
                st.line_chart(daily_revenue.set_index("Date")["Revenue"])
            else:
                st.info("No valid dates were found in the 'order_date' column.")
        else:
            st.info("Add an 'order_date' column to see the sales trend over time.")

            
        st.divider()
        st.subheader("Download Business Report")

        report = f"""
BUSINESS ANALYTICS STUDIO — BUSINESS REPORT

Dataset: {uploaded_file.name}
Rows analysed: {len(df):,}
Columns analysed: {len(df.columns):,}
Duplicate rows in current dataset: {int(df.duplicated().sum()):,}
Missing values in current dataset: {int(df.isna().sum().sum()):,}

REVENUE SUMMARY
Total revenue: {total_revenue:,.2f}
Units sold: {total_units:,.0f}
Average price: {average_price:,.2f}
Unique products: {product_count:,}
"""

        st.download_button(
            label="Download Business Report",
            data=report,
            file_name="business_analysis_report.txt",
            mime="text/plain"
        )
        
        # Generate a downloadable PDF report
        pdf_buffer = BytesIO()
        pdf_doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph(
            "Business Analytics Studio",
            styles["Title"]
        ))
        story.append(Spacer(1, 12))
        story.append(Paragraph(
            "Business Analysis Report",
            styles["Heading2"]
        ))
        story.append(Spacer(1, 12))

        
        report_data = [
            ["Metric", "Value"],
            ["Dataset", str(uploaded_file.name)],
            ["Rows analysed", f"{len(df):,}"],
            ["Columns analysed", f"{len(df.columns):,}"],
            ["Duplicate rows", f"{int(df.duplicated().sum()):,}"],
            ["Missing values", f"{int(df.isna().sum().sum()):,}"],
        ]

        if "price" in df.columns:
            report_data.extend([
                ["Total revenue", f"{total_revenue:,.2f}"],
                ["Units sold", f"{total_units:,.0f}"],
                ["Average price", f"{average_price:,.2f}"],
                ["Unique products", f"{product_count:,}"],
            ])


        report_table = Table(
            report_data,
            colWidths=[220, 250]
        )
        report_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2457C5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DCE5F2")),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))

        story.append(report_table)
        
        if "product" in revenue_df.columns and "revenue" in revenue_df.columns:
            story.append(Spacer(1, 18))
            story.append(Paragraph(
                "Top 5 Products by Revenue",
                styles["Heading2"]
            ))

            top_products = (
                revenue_df.groupby("product")["revenue"]
                .sum()
                .sort_values(ascending=False)
                .head(5)
                .reset_index()
            )

            product_data = [["Product", "Revenue"]]
            for _, row in top_products.iterrows():
                product_data.append([
                    str(row["product"]),
                    f"{row['revenue']:,.2f}"
                ])

            product_table = Table(
                product_data,
                colWidths=[270, 200]
            )
            product_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2457C5")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DCE5F2")),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]))

            story.append(product_table)

        pdf_doc.build(story)
        pdf_buffer.seek(0)

        st.download_button(
            label="Download PDF Report",
            data=pdf_buffer.getvalue(),
            file_name="business_analysis_report.pdf",
            mime="application/pdf"
        )


