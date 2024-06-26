import streamlit as st
import requests
from bs4 import BeautifulSoup
import streamlit_nested_layout
import google.generativeai as genai
# """
# # YumSum!!
# In the meantime, below is an example of what you can do with just a few lines of code:
# """

st.set_page_config(layout = "wide")

class Restaurant:
  def __init__(self, name, image_url, url, review_count, rating, price, address, phone, reviewsum):
    self.name = name
    self.image_url = image_url
    self.url = url
    self.review_count = review_count
    self.rating = rating
    self.price = price
    self.address = address
    self.phone = phone
    self.reviewsum = reviewsum

def clear_form():
	st.session_state["cuisine"] = ""
	st.session_state["location"] = ""
	st.session_state["results"] = 1
	st.session_state["cost"] = ""

def callback():
	show_review = True

c1, c2, c3 = st.columns([1, 4, 1], gap="small")
with c2:
    st.image('yumsum(3).png')
    st.write("\n")
    st.write('What is YumSum? Its a tool that conveniently recommends restaurants for you, gives key details, and summarize its reviews for you! Recognizing most terms, like "AYCE BBQ", "Boba", or "Japanese Food" at "Goleta", "NYC", or "Hawaii", YumSum is the easiest and quickest way to choose what to eat!')
    st.divider()
    header = st.container()
    cuisine, location, results, cost = st.columns(4)

    # text input 
    with cuisine:
        cuisine = st.text_input("Cuisine or Type of Food", key="cuisine")

    with location:
        location = st.text_input("Location", key="location")

    with results:
        results = st.number_input("Results", min_value=1, max_value=5, key= "results")

    with cost:
        c = [1]
        temp = st.select_slider("Maximum Cost", options=('$', '$$', '$$$', '$$$$'))
        if temp == '$':
            c = [1]
        if temp == '$$':
            c = [1,2]
        if temp == '$$$':
            c = [1,2,3]
        if temp == '$$$$':
            c = [1,2,3,4]
    # generate and reset buttons
    if "show_review" not in st.session_state:
        st.session_state.show_review = False

    generate = st.button("Generate", use_container_width = True, on_click = callback)
    reset = st.button("Reset", use_container_width = True, on_click = clear_form)
    st.divider()
    userOffset = 1

    GOOGLE_API_KEY=st.secrets["key1"]

    genai.configure(api_key=GOOGLE_API_KEY)


    # -------- #
    API_KEY = st.secrets["key2"]
    API_KEY = 'JDeGQl7ZVg9fTkGXDMxvcklYnFZY4Rtu4hmC8zlyRLHcUqzYbiAQUOBQl3EzmF7QoymQiGXim9NF-kI7REJ0fZxIJJTLUaJTTELIZQ-q99WnYZfwuWf3cBE9MHNBZnYx'

    ENDPOINT = 'https://api.yelp.com/v3/businesses/search'
    HEADERS = {'Authorization': 'bearer %s' % API_KEY}


    def summarize(text, name):
        model = genai.GenerativeModel('gemini-pro')
        nameText = "Also state the name of the restaurant which is " + name
        prompt = "Write a new review summarizing these reviews in 2-3 sentences in a professional tone without any point of view. Be specific to the restaurant. If applicable, recommend some dishes. Mention some positives and negatives." + nameText

        response = model.generate_content(prompt + text )

        return(response.text)

    def getReviews(business_url,name):
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
        #st.write(len(bigString.split()))
        summarizedReview = summarize(bigString,name)
        return summarizedReview


    restaurantList = []

    def search(term, limit, offset, location, price):
        PARAMETERS = {'term': term,
                    'limit': limit,
                    'offset': offset,
                    'radius': 16093, # 10 miles 
                    'location': location,
                    'price': price
                    }
        response = requests.get(url = ENDPOINT,
                                params = PARAMETERS,
                                headers = HEADERS)
        st.write(response.status_code)
        st.write(term)
        st.write(limit)
        st.write(offset)
        st.write(location)
        st.write(price)
        business_data = response.json()
        restaurantList.clear()
        for i in business_data['businesses']:
            reviewsum = getReviews(i['url'],i['name'])
            restaurantList.append(Restaurant(i['name'], i['image_url'], i['url'], i['review_count'], i['rating'], i['price'], i['location']['address1'] + ", " + i['location']['city'], i['phone'], reviewsum))

    # reviews
    review1 = st.container(border = True)
    review2 = st.container(border = True)
    review3 = st.container(border = True)
    review4 = st.container(border = True)
    review5 = st.container(border = True)

    arr = [review1, review2, review3, review4, review5]

    # if generate is pressed
    if generate or st.session_state.show_review:
        #try:
            search(cuisine, results, 0, location, c)
            #try:
            for i in range(0, results):
                with arr[i]:
                    with st.container(border=True):
                        #st.header(restaurantList[i].name)
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(restaurantList[i].image_url)

                        with col2:
                            st.header("⠀" + restaurantList[i].name, divider='gray')
                            st.write("⠀⠀" + str(restaurantList[i].rating) + ' :star:⠀(' + str(restaurantList[i].review_count) + ' reviews)' + '⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀' + str(restaurantList[i].price))
                            st.write("⠀⠀" + restaurantList[i].phone + ', ' + restaurantList[i].address)
                            mc1, mc2 = st.columns(2)
                            mapsaddr = restaurantList[i].name + "+" + restaurantList[i].address
                            mapsaddr = mapsaddr.replace(" ", "+")
                            mapsaddr = mapsaddr.replace(",", "")
                            googlemaps = "https://www.google.com/maps/search/" + mapsaddr
                            applemaps = "http://maps.apple.com/?q=" + mapsaddr
                            with mc1:
                                st.link_button("Open in Google Maps", googlemaps, help=None, type="secondary", disabled=False, use_container_width=True)
                            with mc2:
                                st.link_button("Open in Apple Maps", applemaps, help=None, type="secondary", disabled=False, use_container_width=True)

                            sc1, sc2, sc3 = st.columns([1,20,1])
                            with sc2:
                                st.write(restaurantList[i].reviewsum)
                                    #st.write(len(restaurantList[i].reviewsum.split()))

            #except:
            #    st.write('Uh oh! Your search gave no results. Press reset, change your entries, and try again! ')  
        #except:
        #   st.write('Uh oh! Your search gave no results. Press reset, change your entries, and try again! ')
        #test 
                        
                    # st.write(restaurantList[i].name)
                    # st.image(restaurantList[i].image_url, width=200)
                    # with st.expander("Review"):
                    # 	st.write(restaurantList[i].reviewsum)

