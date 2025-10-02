import os
import streamlit as st
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Add src folder to path if needed
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from excel_analyser import excel_analyser_app
from emi_calculator import emi_calculator_app

# Sidebar page selector
page = st.sidebar.selectbox("Select App", ["Excel/CSV Analyzer", "EMI Calculator"])

if page == "Excel/CSV Analyzer":
    excel_analyser_app()
elif page == "EMI Calculator":
    emi_calculator_app()

