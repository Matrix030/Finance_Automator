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

def get_required_detail(details):
    if 'mta' in details:
        return 'mta'
    if 'path' in details:
        return 'path'


def categorize_transaction(df):
    df['Category'] = "Uncategorized"
    
    # Define keyword-to-category mapping
    keyword_categories = {
        "TRAVEL": ["MTA", "PATH", "OMNY"],
        "Shopping": ["FIVE BELO", "AMAZON MKTPL", "INSTACART", "TARGET", "PRIMARK", "RED APPLE", "Amazon.com", "99 CENT"],
        "Food": ["2 BROS", "UBER *EATS", "McDonalds", "PAPA JOHNS", "BALADY", "FRESH PIZZA", "HORUS MEDIA", "KARIM", 
                "99 CENT", "GOURMET FRESH", "Patel", "SUPER FRE", "FOOD Brooklyn NY", "DOORDASH", "DD", 
                "SUPERIOR $1 PIZZA", "DUNKIN", "BIRRIA LES", "HALAL MUNCHIES", "PATELS", "STARBUCKS", 
                "PINE APPLE FARM", "NUOVO YORK", "SHAKE SHACK", "SOMETHING GREEK", "CENTRAL VALLEY DELI NEW YORK NY"],
        "Subscription": ["AMAZON PRIME", "Spectrum Mobile", "CLAUDE.AI", "OPENAI", "APPLE.COM", "MINT MOBILE", "Spectrum"],
        "Groceries": ["FRESH JENNY'S", "WEEE"],
        "Personal": ["Zelle", "BUBBLES", "NYU", "UBER *TRIP", "ATM WITHDRAWAL", "Microsoft", "MICRO ELECTRONIC", "BBPBOATHOUSE"],
        "Wire Fee": ["WIRE FEE"],
        "Internet": ["Spectrum"]
    }
    
    # First apply category mapping from session state
    for category, keywords in st.session_state.categories.items():
        if category == 'Uncategorized' or not keywords:
            continue
            
        lowered_keywords = [keyword.lower().strip() for keyword in keywords]
        for idx, row in df.iterrows():
            if row["Category"] != "Uncategorized":
                continue  # Skip already categorized rows
                
            details = row["Description"].lower()
            
            if any(keyword in details for keyword in lowered_keywords):
                df.at[idx, "Category"] = category
    
    # Then apply the predefined keyword categories
    for idx, row in df.iterrows():
        if row["Category"] != "Uncategorized":
            continue  # Skip already categorized rows
            
        details = row["Description"].upper()  # Convert to uppercase for case-insensitive matching
        
        # Check each category's keywords
        for category, keywords in keyword_categories.items():
            if any(keyword.upper() in details for keyword in keywords):
                df.at[idx, "Category"] = category
                break
                
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
            
            # Calculate total amounts
            total_debits = debits_df['Amount'].sum()
            total_credits = credits_df['Amount'].sum()
            
            # Display totals
            st.header("Financial Summary")
            st.info(f"💰 Total Income: ${total_credits:.2f}")
            st.warning(f"💸 Total Expenses: ${total_debits:.2f}")
            st.success(f"🏦 Net Balance: ${total_credits - total_debits:.2f}")
            
            st.markdown("---")

            tab1, tab2 = st.tabs(['Expenses (Debits)', 'Payments (Credits)'])

            with tab1:
                st.subheader(f"Total Expenses: ${total_debits:.2f}")
                
                # Add new category section
                col1, col2 = st.columns([3, 1])
                with col1:
                    new_category = st.text_input("New Category Name")
                with col2:
                    add_button = st.button("Add Category")

                if add_button and new_category:
                    if new_category not in st.session_state.categories:
                        st.session_state.categories[new_category] = []
                        save_categories()
                        st.rerun()
                
                # Create editable dataframe with category dropdown
                st.subheader("Categorize Expenses")
                
                # Create a copy to avoid modifying the original during iteration
                edited_debits = debits_df.copy()
                
                # Initialize session state for edits if not present
                if "edited_categories" not in st.session_state:
                    st.session_state.edited_categories = {}
                
                # Add category dropdown to each row
                for idx, row in edited_debits.iterrows():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
                    
                    with col1:
                        st.text(f"{row['Description']}")
                    
                    with col2:
                        st.text(f"${row['Amount']:.2f}")
                    
                    with col3:
                        # Get all available categories and add "Add New..." option
                        category_options = list(st.session_state.categories.keys())
                        category_options.append("➕ Add New Category")
                        
                        # Key for this specific dropdown
                        dropdown_key = f"cat_dropdown_{idx}"
                        
                        # Default to current category or previous selection
                        default_index = 0
                        if idx in st.session_state.edited_categories:
                            default_index = category_options.index(st.session_state.edited_categories[idx])
                        elif row['Category'] in category_options:
                            default_index = category_options.index(row['Category'])
                        
                        selected_category = st.selectbox(
                            label="Category",
                            options=category_options,
                            index=default_index,
                            key=dropdown_key,
                            label_visibility="collapsed"
                        )
                        
                        # Handle "Add New" selection
                        if selected_category == "➕ Add New Category":
                            new_cat_name = st.text_input(f"New category for row {idx}", key=f"new_cat_{idx}")
                            if st.button("Add", key=f"add_btn_{idx}"):
                                if new_cat_name and new_cat_name not in st.session_state.categories:
                                    st.session_state.categories[new_cat_name] = []
                                    save_categories()
                                    st.session_state.edited_categories[idx] = new_cat_name
                                    st.rerun()
                        else:
                            # Store selected category
                            st.session_state.edited_categories[idx] = selected_category
                            edited_debits.at[idx, 'Category'] = selected_category
                    
                    with col4:
                        # Display date or additional info
                        st.text(f"{row['Posting Date'].strftime('%Y-%m-%d')}")
                
                # Add a button to save all category changes
                if st.button("Save All Category Changes"):
                    # Update the original dataframe with new categories
                    for idx, category in st.session_state.edited_categories.items():
                        debits_df.at[idx, 'Category'] = category
                    
                    # Optionally save to file or update database here
                    st.success("Categories updated successfully!")
                
                # Show the original table below
                st.subheader("All Expenses")
                st.write(debits_df)
                
            with tab2:
                st.subheader(f"Total Income: ${total_credits:.2f}")
                st.write(credits_df)


main()