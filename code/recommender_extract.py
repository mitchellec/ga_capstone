#!/usr/bin/env python
# coding: utf-8

# In[1]:

import streamlit as st
st. set_page_config(layout="wide")
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import h5py
# this setting widens how many characters pandas will display in a column:
pd.options.display.max_colwidth = 100

if 'main' not in st.session_state:
    st.session_state['main'] = pd.read_csv("../data/details_data_extract.csv")

if 'rev_map' not in st.session_state:
    st.session_state['rev_map'] = pd.Series(st.session_state['main'].index, index=st.session_state['main']['name'])

if 'cos_sim' not in st.session_state:
    # st.session_state['cos_sim'] = cosine_similarity(pd.read_csv("../data/cos_sim_data_extract.csv"))
    st.session_state['cos_sim'] = pd.read_csv("../data/cos_sim_extract.csv").to_numpy()


# In[2]:
st.title('Simple Steam Games recommender')
st.markdown("By Mitchelle ([GitHub](https://github.com/mitchellec/ga_capstone))")
st.markdown("Content-Based recommender build using **cosine similarity** for an extract of steam games.")
    

# In[3]:
# get user input
with st.form(key='recommender_form'):
    list_check = st.multiselect('Select only 1 of game title that you want check', options = st.session_state['main']['name'], default="Counter-Strike")

    int_return = st.number_input('Select number between 1 to 20 of recommendations you would like', min_value=1, max_value=20, step=1)
    
    per_row = st.select_slider('Number of recommendations per row', options=[1,2,3,4,5], value=5)
    
    submitted = st.form_submit_button("Get Recommendations")

# In[4]:

# convert the input

int_return = int(int_return)
per_row=int(per_row)

# In[5]:
@st.cache
def get_recommendations(df=st.session_state['main'], indices=st.session_state['rev_map'], title=list_check[0], cosine_sim=st.session_state['cos_sim'], num=int_return):
# def get_recommendations(df=df_main, indices=list_rev_map, title=list_check[0], cosine_sim = cos_sim):
    # Get the index of the game that matches the title
    idx = indices[title]

    # Get the pairwsie similarity scores of all movies with that movie
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the games based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the num most similar titles
    sim_scores = sim_scores[1:(num+1)]

    # Get the titles indices
    name_indices = [i[0] for i in sim_scores]

    # create dataframe
    df_ret = pd.DataFrame(df['name'].iloc[name_indices])
    
    # attach score
    # df_ret['Similarity_percentage'] = pd.DataFrame(cosine_sim).iloc[name_indices,idx]
    
    # attach description
    df_ret['description'] = df['about_the_game'].iloc[name_indices]
    # df_ret['description'] = df['about_the_game'].iloc[name_indices].apply(lambda x: '<a width="248px" height="80px">{}</a>'.format(x, x))
    
    # attach image
    df_ret['image'] = df['header_image'].iloc[name_indices]
    # df_ret['image'] = df['header_image'].iloc[name_indices].apply(lambda x: '<img src="{}" alt="{}" width="248px" height="80px">'.format(x, x))
    
    # Return the top num most similar games
    return df_ret
    #return df_ret.style.hide(axis='index')


# In[ ]:

if submitted:
    with st.container():
        # check if possible to run function
        if len(list_check) > 1:
            st.header("Error")
            st.write("There is **more than 1** game selected!")
            st.write("Please only choose 1 game at a time.")            
        else:
            #st.markdown(get_recommendations().to_html(escape=False), unsafe_allow_html=True)
            # store recommendations
            rec = get_recommendations()
            loop = int_return // per_row
            left = int_return % per_row
            
            # create outer loop
            if loop>0:
                for time in range(loop):
                    # set number of columns
                    cols = st.columns(per_row)
                    # create loop for output
                    for i in range(per_row):
                        with cols[i]:
                            st.header(f"#{i+1+(per_row*time)}")
                            st.write(f"Name : {rec.iloc[i+(per_row*time)]['name']}")
                            st.image(f"{rec.iloc[i+(per_row*time)]['image']}", caption=rec.iloc[i+(per_row*time)]['name'])

                            with st.expander("Game Description"):
                                st.write(rec.iloc[i+(per_row*time)]['description'], unsafe_allow_html=True)

            # print for remaining if any
            if left>0:
                # set number of columns
                cols = st.columns(per_row)
                # create loop for output
                for i in range(left):
                    with cols[i]:
                        st.header(f"#{i+1+(per_row*loop)}")
                        st.write(f"Name : {rec.iloc[i+(per_row*loop)]['name']}")
                        st.image(f"{rec.iloc[i+(per_row*loop)]['image']}", caption=rec.iloc[i+(per_row*loop)]['name'])

                        with st.expander("Game Description"):
                            st.markdown(rec.iloc[i+(per_row*loop)]['description'], unsafe_allow_html=True)

#st.button('Get Recommendations', on_click = get_recommendations)
#st.dataframe(get_recommendations())