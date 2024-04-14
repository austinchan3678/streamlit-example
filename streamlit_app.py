import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import requests
from transformers import pipeline
from bs4 import BeautifulSoup

import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown
"""
# YumSum!!



In the meantime, below is an example of what you can do with just a few lines of code:
"""

cuisine = st.text_input('Cuisine')
location = st.text_input('Location')
numberOfResults = st.number_input('Results', min_value = 1, max_value = 5, value = 1)
cost = st.number_input('Cost', min_value = 1, max_value = 4, value = 1)


done = st.button("Done", use_container_width= True)
reset = st.button("Reset", use_container_width=True) 



userOffset = 0
# summarizer.search(cuisine, numberOfResults, userOffset, location, cost)




def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

GOOGLE_API_KEY='AIzaSyCbZYpjDDZoGwJ5RC7RHwz4v5_6d43LuS8'

genai.configure(api_key=GOOGLE_API_KEY)





# -------- #
API_KEY = '1LmNDpXKm1aNSwK2HCThD4C5v_cQtVxpEio3smS4i5G4-hHbI1DQiFU6Ysa6_ymVvpKIkTCNCGHT1mHKDMGyLh1GHhWklAlFTGBtBx6tm8F8BlNow6F-Z9pEmMrOZXYx'


ENDPOINT = 'https://api.yelp.com/v3/businesses/search'
HEADERS = {'Authorization': 'bearer %s' % API_KEY}


def summarize(text):
    model = genai.GenerativeModel('gemini-pro')
    prompt = "Write a new review summarizing these reviews in 2-3 sentences in a professional tone without any point of view. Be specific to the restaurant. If applicable, recommend some dishes. Mention some positives and negatives:"
    response = model.generate_content(prompt + text )
    to_markdown(response.text)
    st.write(response.text)


def getReviews(business_url):
   url = business_url
   response = requests.get(url)
   html_content = response.text

   soup = BeautifulSoup(html_content, 'html.parser')

   target_spans = soup.find_all('span', class_='raw__09f24__T4Ezm')

   bigString = ""
   for span in target_spans:
       text_content = span.text.strip()
       lang_attribute = span.attrs.get('lang', None)
       if lang_attribute != 'en':
           continue
       bigString += text_content
       # Print the text content
   summarize(text_content)
       # st.write(text_content)


def search(term, limit, offset, location, price):
   PARAMETERS = {'term': term,
               'limit': limit,
               'offset': offset,
               'radius': 16093, # 10 miles already set
               'location': location,
               'price': price
           }
   response = requests.get(url = ENDPOINT,
                           params = PARAMETERS,
                           headers = HEADERS)

   business_data = response.json()


   for i in business_data['businesses']:
        getReviews(i['url'])





if(done):
    st.write("You want ", numberOfResults)
    st.write(location)
    st.write(cuisine)
    search(cuisine, numberOfResults, 0, location, cost)