import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

#Load the data
category_file = "categories.json"
st.set_page_config(page_title="Personalized_Finance_Automation", page_icon="🪙", layout="wide")

if "categories" not in st.session_state:
    st.session_state.categories = {
        "Uncategorized": [],
    }

if os.path.exists(category_file):
    with open(category_file, 'r') as file:
        st.session_state.categories = json.load(file)

def save_categories():
    with open(category_file, 'w') as file:
        json.dump(st.session_state.categories, file)

def categorize_transaction(df):
    df['Category'] = "Uncategorized"

    for category, keywords in st.session_state.categories.items():
        if category == 'Uncategorized' or not keywords:
            continue

        lowered_keywords = [keyword.lower().strip() for keyword in keywords]  
        for idx, row in df.iterrows():
            details = row["Description"].lower()
            if details in lowered_keywords:
                df.at[idx, "Category"] = category
    
    return df

def load_transactions(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df["Posting Date"] = pd.to_datetime(df['Posting Date'], format='%m/%d/%Y')
        df.drop(columns=[col for col in df.columns if "Unnamed" in col], axis=1, inplace=True)
        st.write(df)
        return categorize_transaction(df)

    except Exception as e:
        st.error(f'Error processing file: {str(e)}')
        return None

def add_keyword_to_category(category, keyword):
    keyword = keyword.strip()
    if keyword and keyword not in st.session_state.categories[category]:
        st.sesion_state.categories[category].append(keyword)    
        save_categories()
        return True

    return False
def main():
    st.title("Finance Dashboard")
    uploaded_file = st.file_uploader("Upload your CSV file here", type=['csv'])

    if uploaded_file is not None:
        df = load_transactions(uploaded_file)

        if df is not None:
            debits_df = df[df['Details'] == "DEBIT"].copy()
            credits_df = df[df['Details'] == "CREDIT"].copy()

            tab1, tab2 = st.tabs(['Expenses (Debits)', 'Payments (Credits)'])

            with tab1:
                new_category = st.text_input("New Category Name")
                add_button = st.button("Add Category")

                if add_button and new_category:
                    if new_category not in st.session_state.categories:
                        st.session_state.categories[new_category] = []
                        save_categories()
                        st.rerun()

                st.write(debits_df)
                #minute 42
            with tab2:
                st.write(credits_df)


main()