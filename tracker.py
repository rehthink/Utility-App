import streamlit as st
import pandas as pd
import requests

# Function to fetch data from a public Google Sheet
@st.cache_data(show_spinner="Please be patience, Loading data...")  # Cache data but allow clearing
def get_sheet_data():
    url = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vRQRxRRMDN4KnkEX3W1EwF8lbyPyCCtUm12Cr9laFY_lufeyYUxnsd4vqy8CiBeaya0XQBgY5VCbzQL/pub?gid=2016442985&single=true&output=csv"

    try:
        # Read CSV data
        df = pd.read_csv(url, on_bad_lines="skip", encoding="utf-8", header=None)

        # Drop completely empty rows
        df.dropna(how="all", inplace=True)

        # Extract A1 as the app title
        app_title = df.iloc[0, 0] if not pd.isna(df.iloc[0, 0]) else "Electricity & Maintenance Tracker"

        # Extract A2:K2 as column headers
        column_headers = df.iloc[1].dropna().tolist()

        # Ensure column headers are valid
        if not column_headers or all(pd.isna(column_headers)):
            column_headers = [f"Column {i+1}" for i in range(df.shape[1])]

        # Extract actual data (A3 onwards)
        df = df[2:].reset_index(drop=True)
        df.columns = column_headers  # Assign column names

        # Drop completely empty columns
        df.dropna(axis=1, how="all", inplace=True)

        return df, app_title.strip()

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), "Data Not Available"

# Streamlit UI
st.set_page_config(layout="wide")  # Wide layout for better table display

# # Apply Light Theme in UI elements
# light_theme_css = """
#     <style>
#         /* Force Light Mode */
#         body {
#             color: black !important;
#             background-color: white !important;
#         }
#         [data-testid="stAppViewContainer"] {
#             background-color: white !important;
#         }
#         [data-testid="stSidebar"] {
#             background-color: #f8f9fa !important;
#         }
#         [data-testid="stHeader"] {
#             background-color: white !important;
#         }
#     </style>
# """
# st.markdown(light_theme_css, unsafe_allow_html=True)

# **🔄 Add a Refresh Button**
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()  # **Clear cached data**
    st.rerun()  # **Force UI refresh**

df, app_title = get_sheet_data()

# **📌 Center Align Title using HTML & CSS**
st.markdown(
    f"""
    <h1 style="text-align: center; font-size: 36px; color: #1F4E79;">
        📊 {app_title}
    </h1>
    """,
    unsafe_allow_html=True
)

# **📌 Create Tabs**
tab1, tab2 = st.tabs(["📋 Preview Data", "📊 Summary"])

### **🔹 Tab 1: Preview Data**
# with tab1:
#     st.subheader("Meter Readings & Bills")

#     if not df.empty:
#         valid_columns = df.columns.tolist()  # A2:K2 used as column names

#         # Let user select valid columns
#         selected_columns = st.multiselect("Select columns to display:", valid_columns, default=valid_columns)

#         # Display selected columns with auto-fit width and **HIDE index**
#         st.dataframe(df[selected_columns], use_container_width=True, hide_index=True)
#     else:
#         st.error("⚠ Failed to load data. Please check the Google Sheet settings.")

with tab1:
    st.subheader("Meter Readings & Bills")

    if not df.empty:
        valid_columns = df.columns.tolist()

        # **Default Selected Columns**
        default_columns = [
            "Floors",
            "Previous Reading",
            "Current Reading",
            "Outstanding Readings",
            "Outstanding Due",
            "Payment",
            "Amount Per Meter",
        ]

        # **Ensure only valid columns are pre-selected**
        selected_columns = st.multiselect(
            "Select columns to display:", valid_columns, 
            default=[col for col in default_columns if col in valid_columns]
        )

        # **Display selected columns (Hiding index)**
        st.dataframe(df[selected_columns], use_container_width=True, hide_index=True)
    else:
        st.error("⚠ Failed to load data. Please check the Google Sheet settings.")


### **🔹 Tab 2: Summary**
with tab2:
    st.subheader("Summary of Usage for Month of March, 2025")

    if not df.empty:
        try:
            # Identify columns dynamically
            outstanding_due_col = next((col for col in df.columns if "Outstanding Due" in str(col)), None)
            total_amount_col = next((col for col in df.columns if "Amount Per Meter" in str(col)), None)

            # Ensure columns exist
            if not outstanding_due_col:
                st.error("⚠ Could not find 'Outstanding Due' column.")
            if not total_amount_col:
                st.error("⚠ Could not find 'Total Amount Per Meter' column.")

            # **Filter only floor rows (excluding Total row)**
            floor_data = df[~df.iloc[:, 0].str.contains("Readings", na=False, case=False)]

            # Calculate Total Outstanding Due (only for floors)
            if outstanding_due_col:
                floor_data[outstanding_due_col] = floor_data[outstanding_due_col].astype(str).str.replace(r"[^\d.]", "", regex=True)
                floor_data[outstanding_due_col] = pd.to_numeric(floor_data[outstanding_due_col], errors="coerce")
                total_outstanding_due = floor_data[outstanding_due_col].sum()
            else:
                total_outstanding_due = 0

            # **Get Rate per Unit from the bottom-most cell in 'Total Amount Per Meter'**
            rate_per_unit = df[total_amount_col].dropna().iloc[-1] if total_amount_col else "Not Available"

            # Display Summary
            st.metric(label="💰 Total Outstanding Due (Floors Only)", value=f"₹{total_outstanding_due:,.2f}")
            st.metric(label="⚡ Rate per Unit", value=f"{rate_per_unit}")

        except Exception as e:
            st.error(f"⚠ Error in summary calculation: {e}")

    else:
        st.error("⚠ No data available for summary.")

st.warning("🔹 This method only allows reading data. To update the sheet, consider using Google Sheets API.")
