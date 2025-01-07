import streamlit as st
import pandas as pd

# Updated account ranges
account_ranges = {
    "Inuvo GDN APD1": range(336466, 336601),
    "Inuvo GDN APD2": range(264800, 264971),
    "Inuvo GDN APD4": range(336183, 336301),
    "Inuvo GDN APD5": range(327781, 336114),
    "Inuvo GDN APD6": range(265100, 265251),
    "Inuvo GDN APD7": range(265700, 265774),
    "Inuvo GDN APPD8": range(336301, 336351),
    "Inuvo GDN APPD9": range(336351, 336401),
    "Inuvo GDN APD10": range(336676, 336726),
    "Inuvo GDN APD11": range(336901, 336968),
    "Inuvo INR 008 (PST)": range(266001, 266406),  # New range
    "Inuvo INR 009 (PST)": range(336601, 336676),  # New range
}

# Function to assign campaigns to accounts
def assign_account(campid):
    for account, camp_range in account_ranges.items():
        if campid in camp_range:
            return account
    return "Unassigned"

# Function to process uploaded files
def process_revenue_files(uploaded_files):
    # Combine all uploaded files
    all_data = pd.concat([pd.read_csv(file) for file in uploaded_files], ignore_index=True)
    all_data['Date'] = pd.to_datetime(all_data['Date'], format='%m/%d/%Y')
    
    # Assign campaigns to accounts
    all_data['Account'] = all_data['Campid'].apply(assign_account)
    
    # Aggregate revenue by account
    account_summary = all_data.groupby('Account').agg({'Revenue': 'sum'}).reset_index()
    
    # Aggregate revenue by account and date
    account_date_summary = all_data.groupby(['Account', 'Date']).agg({'Revenue': 'sum'}).reset_index()
    
    return all_data, account_summary, account_date_summary

# Streamlit app
st.title("GDN Revenue Dashboard")
st.write("Upload your revenue files to analyze revenues.")

# Upload files
uploaded_files = st.file_uploader("Upload Revenue Files", accept_multiple_files=True, type=['csv'])

if uploaded_files:
    # Process the files
    all_data, account_summary, account_date_summary = process_revenue_files(uploaded_files)
    
    # Dynamic date filtering
    st.write("### Filter by Date Range")
    min_date = all_data['Date'].min()
    max_date = all_data['Date'].max()
    start_date, end_date = st.date_input(
        "Select Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date,
    )
    
    # Filter the data based on the selected date range
    filtered_data = all_data[(all_data['Date'] >= pd.Timestamp(start_date)) & (all_data['Date'] <= pd.Timestamp(end_date))]
    
    # Recompute summaries for the filtered data
    filtered_account_summary = filtered_data.groupby('Account').agg({'Revenue': 'sum'}).reset_index()
    filtered_account_date_summary = filtered_data.groupby(['Account', 'Date']).agg({'Revenue': 'sum'}).reset_index()
    
    # Display filtered account-wise revenue
    st.write("### Account-wise Revenue Summary for Selected Date Range")
    st.dataframe(filtered_account_summary)
    
    # Display filtered account-per-day revenue
    st.write("### Account per Day Revenue Summary for Selected Date Range")
    st.dataframe(filtered_account_date_summary)
    
    # Display unassigned campaigns
    st.write("### Unassigned Campaign IDs")
    unassigned_data = filtered_data[filtered_data['Account'] == "Unassigned"]
    if not unassigned_data.empty:
        st.dataframe(unassigned_data[['Campid', 'Date', 'Revenue']].drop_duplicates())
    else:
        st.write("All campaigns have been assigned to accounts.")
    
    # Download options for filtered data
    st.download_button(
        label="Download Account-wise Revenue CSV",
        data=filtered_account_summary.to_csv(index=False),
        file_name="filtered_account_wise_revenue.csv",
        mime="text/csv"
    )
    
    st.download_button(
        label="Download Account per Day Revenue CSV",
        data=filtered_account_date_summary.to_csv(index=False),
        file_name="filtered_account_per_day_revenue.csv",
        mime="text/csv"
    )
    
    if not unassigned_data.empty:
        st.download_button(
            label="Download Unassigned Campaign IDs CSV",
            data=unassigned_data[['Campid', 'Date', 'Revenue']].drop_duplicates().to_csv(index=False),
            file_name="unassigned_campaign_ids.csv",
            mime="text/csv"
        )