import streamlit as st
from tweets_pipeline.database import Database
from app_options import database_options, stop_words

#Create a database object and connect to the database
db = Database(database_options)
db.connect()

