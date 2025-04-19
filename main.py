import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

#Load the data

st.set_page_config(page_title="Personalized_Finance_Automation", page_icon="🪙", layout="wide")


def load_transactions(uploaded_file):
    try:
        


def main():
    st.title("Finance Dashboard")
    uploaded_file = st.file_uploader("Upload your CSV file here", type=['csv'])

    if uploaded_file is not None:
        df = load_transactions(uploaded_file)

main()