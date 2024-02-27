import streamlit as st
import pandas as pd 
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy

# First some MPG Data Exploration
mpg_df = pd.read_csv("./data/mpg.csv")

# Add title and header
st.title("Introduction to Streamlit")
st.header("MPG Data Exploration")