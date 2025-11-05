import streamlit as st
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

# Import the main app
from working_enhanced_app import main

if __name__ == "__main__":
    main()