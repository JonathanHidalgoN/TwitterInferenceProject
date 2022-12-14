import streamlit as st
from tweets_pipeline.database import Database
from app_options import database_options, stop_words
from utils import app_functions 
from utils import text_processing_functions
from text_generation.text_generator import generate_text, load_model
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
    selected_user = st.selectbox("Select a user", users_df["username"])
    col1, col2 = st.columns(2)
    with col2:
        general_info = app_functions.examine_user(db, selected_user)
        st.dataframe(general_info, width=500)
    with col1:
        user_image = app_functions.get_image_of_user(db,selected_user)
        st.image(user_image, width=180)
    days_to_show = st.select_slider("Number of tweets to show", options=[100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])
    dashboard = app_functions.create_dates_dashboard(db,selected_user, days_to_show)
    st.pyplot(dashboard, width=500)
    col1, col2 = st.columns(2)
    with col1:
        tweets_to_count_words = st.slider("Select the number of tweets to count words", 1000, 10000, 1000)
    with col2:
        words_to_show = st.slider("Select the number of words to show", 10, 60, 10)
    common_words_chart = app_functions.create_common_words_graph(db, selected_user, tweets_to_count_words, stop_words, words_to_show)
    st.pyplot(common_words_chart, width=500, height=500)
    st.markdown("<h1 style='text-align: center;'>Some distributions</h1>", unsafe_allow_html=True)
    tweets_for_distributions = st.select_slider("Select the number of tweets to analyse", options=[1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000])
    col1, col2 = st.columns(2)
    with col1:
        text_option_1 = st.selectbox("Select the distribution to show", ("favs", "Retweets","quotes","number of words per tweet"), index=0)
        app_functions._add_space(8)
        text_option_2 = st.selectbox("Select the distribution to show", ("favs", "Retweets","quotes","number of words per tweet"), index=1)
    with col2:
        dist1 = app_functions.display_distribution_1 = app_functions.display_distribution(db, text_option_1, tweets_for_distributions)
        st.pyplot(dist1, width=500, height=500)
        dist2 = app_functions.display_distribution_2 = app_functions.display_distribution(db, text_option_2, tweets_for_distributions)
        st.pyplot(dist2, width=500, height=500)
#input text
    prompt = st.text_input("Insert text to generate a tweet", "Insert text here")
    col1, col2 = st.columns(2)
    with col1:
        generate_tweet_button = st.button("Generate tweet")
    with col2:
        words_to_generate = st.slider("Select the number of words to generate", 10, 100, 10)
    model = load_model("app/text_generation/model2022-11-13 22_35_35.364060.h5")
    #box to show the generated text
    if generate_tweet_button:
        text = generate_text(model,prompt ,words_to_generate,0.7)
        st.text_area("Generated text", text)
