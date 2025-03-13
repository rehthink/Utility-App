import streamlit as st
import pandas as pd
import requests

# **✅ Set Wide Layout**
st.set_page_config(layout="wide")

# **🔹 Function to Fetch Data from Google Sheet**
@st.cache_data(show_spinner="Loading data, please wait...")
def get_sheet_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRQRxRRMDN4KnkEX3W1EwF8lbyPyCCtUm12Cr9laFY_lufeyYUxnsd4vqy8CiBeaya0XQBgY5VCbzQL/pub?gid=2016442985&single=true&output=csv"

    try:
        df = pd.read_csv(url, on_bad_lines="skip", encoding="utf-8", header=None)
        df.dropna(how="all", inplace=True)  # Drop empty rows

        # Extract A1 as the app title
        app_title = df.iloc[0, 0] if not pd.isna(df.iloc[0, 0]) else "Electricity & Maintenance Tracker"

        # Extract A2:K2 as column headers
        column_headers = df.iloc[1].dropna().tolist()
        if not column_headers:
            column_headers = [f"Column {i+1}" for i in range(df.shape[1])]

        # Extract actual data (A3 onwards)
        df = df[2:].reset_index(drop=True)
        df.columns = column_headers
        df.dropna(axis=1, how="all", inplace=True)  # Drop empty columns

        return df, app_title.strip()

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), "Data Not Available"

# **🔄 Refresh Button**
with st.sidebar:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

df, app_title = get_sheet_data()

# **📌 Centered App Title**
st.markdown(f"<h1 style='text-align: center; font-size: 26px;'>{app_title}</h1>", unsafe_allow_html=True)

# **📌 Tabs: Summary First**
tab1, tab2 = st.tabs(["📊 Summary", "📋 Preview Data"])

### **🔹 Sidebar Column Selection**
with st.sidebar:
    st.header("⚙️ Configure Display")

    if not df.empty:
        valid_columns = df.columns.tolist()
        default_columns = ["Floors", "Previous Reading", "Current Reading", "Outstanding Readings", "Outstanding Due", "Payment", "Amount Per Meter"]
        selected_columns = st.multiselect("Select columns to display:", valid_columns, default=[col for col in default_columns if col in valid_columns])

### **🔹 Tab 1: Summary**
# with tab1:

#     # **📌 Move Summary Heading ABOVE Tabs**
#     st.markdown("<h2 style='text-align: left; font-size: 2px;'>Summary of Usage - March 2025</h2>", unsafe_allow_html=True)

#     if not df.empty:
#         try:
#             # **Identify Required Columns**
#             outstanding_due_col = next((col for col in df.columns if "Outstanding Due" in str(col)), None)
#             outstanding_readings_col = next((col for col in df.columns if "Outstanding Readings" in str(col)), None)
#             payment_col = next((col for col in df.columns if "Payment" in str(col)), None)
#             total_amount_col = next((col for col in df.columns if "Amount Per Meter" in str(col)), None)

#             if not all([outstanding_due_col, outstanding_readings_col, payment_col]):
#                 st.error("⚠ Some required columns are missing. Check sheet structure.")
#             else:
#                 # # **Filter Floor Rows Only**
#                 # floor_data = df[~df.iloc[:, 0].str.contains("Readings", na=False, case=False)]

#                 # **Filter Floor Rows Only (Excluding 'Collection Dated')**
#                 floor_data = df[
#                     (~df.iloc[:, 0].str.contains("Readings", na=False, case=False)) & 
#                     (~df.iloc[:, 0].str.contains("Collection Dated : 14th March 2025", na=False, case=False))
#                 ]

#                 # **Convert to Numeric**
#                 floor_data[outstanding_due_col] = floor_data[outstanding_due_col].astype(str).str.replace(r"[^\d.]", "", regex=True)
#                 floor_data[outstanding_readings_col] = floor_data[outstanding_readings_col].astype(str).str.replace(r"[^\d.]", "", regex=True)
#                 floor_data[outstanding_due_col] = pd.to_numeric(floor_data[outstanding_due_col], errors="coerce").fillna(0)
#                 floor_data[outstanding_readings_col] = pd.to_numeric(floor_data[outstanding_readings_col], errors="coerce").fillna(0)

#                 # ✅ **Total Outstanding Due**
#                 total_outstanding_due = floor_data[outstanding_due_col].sum()

#                 # ✅ **Rate per Unit**
#                 rate_per_unit = df[total_amount_col].dropna().iloc[-1] if total_amount_col else "Not Available"

#                 # **📌 Display Metrics (Centered, Lighter Text)**
#                 st.markdown(
#                     f"""
#                         <div style="display: flex; justify-content: center; gap: 50px;">
#                             <div style="text-align: center;">
#                                 <p style="font-weight: bold; font-size: 20px;">💰 Outstanding Due</p>
#                                 <p style="font-size: 16px; text-align: center;">₹{total_outstanding_due:,.2f}</p>
#                             </div>
#                             <div style="text-align: center;">
#                                 <p style="font-weight: bold; font-size: 20px;">⚡ Rate per Unit</p>
#                                 <p style="font-size: 16px; text-align: center;">{rate_per_unit}</p>
#                             </div>
#                         </div>
#                     """,
#                     unsafe_allow_html=True
#                 )

#                 # **📂 Categorize Flats by Payment**
#                 paid_flats = floor_data[floor_data[payment_col].notna() & (floor_data[payment_col] != "")]
#                 unpaid_flats = floor_data[floor_data[payment_col].isna() | (floor_data[payment_col] == "")]

#                 # **📂 Expandable Paid Flats**
#                 with st.expander("✅ Paid", expanded=False):
#                     if not paid_flats.empty:
#                         st.dataframe(paid_flats[[df.columns[0], outstanding_readings_col, outstanding_due_col]], use_container_width=True, hide_index=True)
#                     else:
#                         st.info("No paid flats available.")

#                 # **📂 Expandable Unpaid Flats**
#                 with st.expander("❌ Unpaid", expanded=False):
#                     if not unpaid_flats.empty:
#                         st.dataframe(unpaid_flats[[df.columns[0], outstanding_readings_col, outstanding_due_col]], use_container_width=True, hide_index=True)
#                     else:
#                         st.success("All flats have paid their dues! 🎉")

#         except Exception as e:
#             st.error(f"⚠ Error in summary calculation: {e}")

#     else:
#         st.error("⚠ No data available for summary.")

### **🔹 Tab 1: Summary**
with tab1:

    # **📌 Move Summary Heading ABOVE Tabs**
    st.markdown("<h2 style='text-align: left; font-size: 20px;'>Summary of Usage - March 2025</h2>", unsafe_allow_html=True)

    if not df.empty:
        try:
            # **Identify Required Columns**
            outstanding_due_col = next((col for col in df.columns if "Outstanding Due" in str(col)), None)
            outstanding_readings_col = next((col for col in df.columns if "Outstanding Readings" in str(col)), None)
            payment_col = next((col for col in df.columns if "Payment" in str(col)), None)
            total_amount_col = next((col for col in df.columns if "Amount Per Meter" in str(col)), None)
            utilized_units_col = next((col for col in df.columns if "Outstanding Readings" in str(col)), None)

            if not all([outstanding_due_col, outstanding_readings_col, payment_col, total_amount_col, utilized_units_col]):
                st.error("⚠ Some required columns are missing. Check sheet structure.")
            else:
                # **Filter Floor Rows Only (Excluding 'Collection Dated')**
                floor_data = df[
                    (~df.iloc[:, 0].str.contains("Readings", na=False, case=False)) & 
                    (~df.iloc[:, 0].str.contains("Collection Dated", na=False, case=False))
                ]

                # **Ensure Proper Numeric Conversion for Selected Columns**
                for col in [outstanding_due_col, outstanding_readings_col, total_amount_col, utilized_units_col]:
                    floor_data[col] = (
                        floor_data[col]
                        .astype(str)  # Convert to string first
                        .str.replace(r"[^\d.]", "", regex=True)  # Remove non-numeric characters
                        .replace("", "0")  # Replace empty strings with "0"
                        .astype(float)  # Convert to float
                    )

                # ✅ **Total Outstanding Due**
                total_outstanding_due = floor_data[outstanding_due_col].sum()

                # ✅ **Rate per Unit**
                rate_per_unit = df[total_amount_col].dropna().iloc[-1] if total_amount_col else "Not Available"

                # ✅ **Total Amount Per Meter**
                total_amount_per_meter = floor_data[total_amount_col].sum()

                # ✅ **Total Utilized Units**
                total_utilized_units = floor_data[utilized_units_col].sum(skipna=True) if utilized_units_col else 0

                # **📌 Display Metrics (Centered)**
                # **📌 Display Metrics in Two Rows**
                st.markdown(
                    f"""
                        <div style="display: flex; justify-content: center; gap: 80px;">
                            <div style="text-align: center;">
                                <p style="font-weight: bold; font-size: 20px;">💲 Total Due By Meter</p>
                                <p style="font-size: 16px; text-align: center;">₹{total_amount_per_meter:,.2f}</p>
                            </div>
                            <div style="text-align: center;">
                                <p style="font-weight: bold; font-size: 20px;">📊 Total Utilized Units</p>
                                <p style="font-size: 16px; text-align: center;">{total_utilized_units:,.2f} kWh</p>
                            </div>
                        </div>

                        <br>

                        <div style="display: flex; justify-content: center; gap: 80px;">
                            <div style="text-align: center;">
                                <p style="font-weight: bold; font-size: 20px;">💰 Outstanding Due</p>
                                <p style="font-size: 16px; text-align: center;">₹{total_outstanding_due:,.2f}</p>
                            </div>
                            <div style="text-align: center;">
                                <p style="font-weight: bold; font-size: 20px;">⚡ Rate per Unit</p>
                                <p style="font-size: 16px; text-align: center;">{rate_per_unit}</p>
                            </div>
                        </div>

                    """,
                    unsafe_allow_html=True
                )

                # **📂 Categorize Flats by Payment**
                paid_flats = floor_data[floor_data[payment_col].notna() & (floor_data[payment_col] != "")]
                unpaid_flats = floor_data[floor_data[payment_col].isna() | (floor_data[payment_col] == "")]

                # **📂 Expandable Paid Flats**
                with st.expander("✅ Paid", expanded=False):
                    if not paid_flats.empty:
                        st.dataframe(paid_flats[[df.columns[0], outstanding_readings_col, outstanding_due_col]], use_container_width=True, hide_index=True)
                    else:
                        st.info("No paid flats available.")

                # **📂 Expandable Unpaid Flats**
                with st.expander("❌ Unpaid", expanded=False):
                    if not unpaid_flats.empty:
                        st.dataframe(unpaid_flats[[df.columns[0], outstanding_readings_col, outstanding_due_col]], use_container_width=True, hide_index=True)
                    else:
                        st.success("All flats have paid their dues! 🎉")

        except Exception as e:
            st.error(f"⚠ Error in summary calculation: {e}")

    else:
        st.error("⚠ No data available for summary.")


### **🔹 Tab 2: Preview Data**
with tab2:
    st.subheader("Meter Readings & Bills")
    if not df.empty:
        st.dataframe(df[selected_columns], use_container_width=True, hide_index=True)
    else:
        st.error("⚠ Failed to load data. Please check the Google Sheet settings.")

st.warning("🔹 This method only allows reading data. To update the sheet, consider using Google Sheets API.")
