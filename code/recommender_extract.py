#!/usr/bin/env python
# coding: utf-8

# In[1]:

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import h5py

if 'main' not in st.session_state:
    st.session_state['main'] = pd.read_csv("../data/details_data_extract.csv")

if 'rev_map' not in st.session_state:
    st.session_state['rev_map'] = pd.Series(st.session_state['main'].index, index=st.session_state['main']['name'])

if 'cos_sim' not in st.session_state:
    st.session_state['cos_sim'] = cosine_similarity(pd.read_csv("../data/cos_sim_data_extract.csv"))


# In[2]:
st.title('Simple Steam Games recommender')

st.markdown("Simple recommender build using **cosine similarity** for an extract of steam games.")
    

# In[3]:
# get user input
with st.form(key='recommender_form'):
    list_check = st.multiselect('Select only 1 of game title that you want check', options = st.session_state['main']['name'], default="Counter-Strike")

    int_return = st.number_input('Select number of recommendations you would like', min_value=1, max_value=20, step=1)

    submitted = st.form_submit_button("Get Recommendations")

# In[4]:

# convert the input

int_return = int(int_return)


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
    df_ret['Similarity_percentage'] = pd.DataFrame(cosine_sim).iloc[name_indices,idx]
    
    # attach image
    df_ret['image'] = df['header_image'].iloc[name_indices].apply(lambda x: '<img src="{}" alt="{}" width="248px" height="80px">'.format(x, x))
    
    # Return the top num most similar games
    return df_ret


# In[ ]:

if submitted:
    with st.empty():
        #st.table(get_recommendations())
        st.markdown(get_recommendations().to_html(escape=False), unsafe_allow_html=True)

#st.button('Get Recommendations', on_click = get_recommendations)
#st.dataframe(get_recommendations())