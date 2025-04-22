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
        return df
    


def categorize_function(df):
    categorized_df = df.copy()
    categorized_df['category'] = None
    for key, items in st.session_state.categories.items():
        for item in items:
            mask = categorized_df['Description'].str.contains(item.lower(), na=False, case=False) |  categorized_df['Type'].str.contains(item.lower(), na=False, case=False)
            # & categorized_df['category'].isna()
            categorized_df.loc[mask, 'category'] = key.upper()
    st.header('All Transcations - Categorized')
    if st.checkbox("Show Categorized Data"):
        if st.toggle("Enable Editing"):
            categorized_df = st.data_editor(categorized_df)
            return categorized_df
            # st.write(categorized_df)
        else:
            st.dataframe(categorized_df)
    return categorized_df

def check_balance_status(balance):
    if balance <= 0:
        return 'owes'
    else:
        return 'is owed'


def main():
    st.title("Simple Finance Dashboard")
    
    df = load_transactions('Rishikesh Gharat Chase Statement.csv')
    splitwise_df = load_transactions('Rishikesh Gharat Splitwise.csv')

    if st.checkbox("Show Splitwise Data"):
        st.write(splitwise_df)
    rishi_balance = splitwise_df['Rishikesh gharat'].iloc[-1]

    if check_balance_status(rishi_balance) == 'owes':
        st.text(f'You owe: {rishi_balance}')
    else:
        st.text(f"You are owed: {rishi_balance}")


    if df is not None:
        debits_df = df[df["Details"] == "DEBIT"].copy()
        credits_df = df[df["Details"] == "CREDIT"].copy()
        
        st.session_state.debits_df = debits_df.copy()
        
        tab1, tab2 = st.tabs(["Expenses (Debits)", "Payments (Credits)"])
        with tab1:
            # st.write(debits_df)
            st.text(f'Debit Sum: {debits_df['Amount'].sum()}')
        with tab2:
            # st.write(credits_df)
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