import streamlit as st
from tweets_pipeline.database import Database
from app_options import database_options, stop_words
from utils import app_functions 
#Create a database object and connect to the database
db = Database(database_options)
db.connect()

st.title("Tweets project")
st.header("You can select users in the database or scrape new ones")
#Select users from the database or scrape new ones
option = st.selectbox("Select users from the database insert or scrape new ones", ("Existing users", "Scrape new users"))

if option == "Existing users":
    users_to_show = st.slider("Select the number of users to show", 1, 100, 10)
    users_df = app_functions.users_with_most_tweets(db, users_to_show)
    st.dataframe(users_df)
    #select a user from the dataframe
    selected_user = st.selectbox("Select a user", users_df["username"])
    
