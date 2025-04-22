import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title="Simple Finance App", page_icon="💰", layout="wide")

category_file = "categories.json"
tab_names = ["Travel Expenses",
            "Personal Transfers",
            "Food Expenses",
            "Subscriptions",
            "Shopping Expenses",
            "Rent Payments",
            "wire transfer"]
if "categories" not in st.session_state:
    st.session_state.categories = {
        "Uncategorized": [],
    }
    
if os.path.exists(category_file):
    with open(category_file, "r") as f:
        st.session_state.categories = json.load(f)

@st.cache_data
def load_transactions(file):
    try:
        df = pd.read_csv(file)
        df = df.drop("Check or Slip #", axis= 1)
        df.columns = [col.strip() for col in df.columns]
        df["Posting Date"] = pd.to_datetime(df["Posting Date"], format="%m/%d/%Y")
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        # st.write(df)
        return df
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None
    


def categorize_function(df):
    categorized_df = df.copy()
    categorized_df['category'] = None
    for key, items in st.session_state.categories.items():
        for item in items:
            mask = categorized_df['Description'].str.contains(item.lower(), na=False, case=False) |  categorized_df['Type'].str.contains(item.lower(), na=False, case=False)
            # & categorized_df['category'].isna()
            categorized_df.loc[mask, 'category'] = key.upper()
    st.header('All Transcations - Categorized')
    st.write(categorized_df)
    return categorized_df

def display_tabs():
   pass


def main():
    st.title("Simple Finance Dashboard")
    
    uploaded_file = st.file_uploader("Upload your transaction CSV file", type=["csv"])
    
    if uploaded_file is not None:
        df = load_transactions(uploaded_file)
        
        if df is not None:
            debits_df = df[df["Details"] == "DEBIT"].copy()
            credits_df = df[df["Details"] == "CREDIT"].copy()
            
            st.session_state.debits_df = debits_df.copy()
            
            tab1, tab2 = st.tabs(["Expenses (Debits)", "Payments (Credits)"])
            with tab1:
                st.write(debits_df)
                st.text(f'Debit Sum: {debits_df['Amount'].sum()}')
            with tab2:
                st.write(credits_df)
                st.text(f'Credit Sum: {credits_df['Amount'].sum()}')
            
            categorized_df = categorize_function(df)
            
            travel_tab, personal_tab, food_tab, subscription_tab, shopping_tab, rent_tab, wire_transfers_tab = st.tabs(tab_names)

            with travel_tab:
             st.write(categorized_df[categorized_df['category'] == 'TRAVEL'])
             st.text(f"Total Travel Expenses: {categorized_df[categorized_df['category'] == 'TRAVEL']['Amount'].sum()}")

            with personal_tab:
             st.write(categorized_df[categorized_df['category'] == 'PERSONAL'])
             st.text(f"Total Personal Expenses: {categorized_df[categorized_df['category'] == 'PERSONAL']['Amount'].sum()}")

            with food_tab:
             st.write(categorized_df[categorized_df['category'] == 'FOOD'])
             st.text(f"Total Personal Expenses: {categorized_df[categorized_df['category'] == 'FOOD']['Amount'].sum()}")

            with subscription_tab:
             st.write(categorized_df[categorized_df['category'] == 'SUBSCRIPTION'])
             st.text(f"Total Subscription Expenses: {categorized_df[categorized_df['category'] == 'SUBSCRIPTION']['Amount'].sum()}")
            
            with rent_tab:
                rent_df = categorized_df[
                    (categorized_df['category'] == 'RENT') & (categorized_df['Amount'] == -725)
                                        ]
                st.write(rent_df)
                st.text(f"Total Personal Expenses: {rent_df['Amount'].sum()}")

            with shopping_tab:
                st.write(categorized_df[categorized_df['category'] == 'SHOPPING'])
                st.text(f"Total Personal Expenses: {categorized_df[categorized_df['category'] == 'SHOPPING']['Amount'].sum()}")
            
            with wire_transfers_tab:
               st.write(categorized_df[categorized_df['category'] == 'WIRE TRANSFER'])
               st.text(f"Total Wire Transfer Amount: {categorized_df[categorized_df['category'] == 'WIRE TRANSFER']['Amount'].sum()}")

main()      