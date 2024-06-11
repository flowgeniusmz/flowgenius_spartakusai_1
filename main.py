import streamlit as st
from classes import clsSessionState as ss, clsPageSetup as ps, clsUserState as us


# 1. Set App Configuration (NOTE: Must be the first 'streamlit' or 'st' command in app)
st.set_page_config(page_icon=st.secrets.app.icon, page_title=st.secrets.app.title, layout=st.secrets.app.layout, initial_sidebar_state=st.secrets.app.sidebar)

# 2. Initialize Session State (NOTE: Uses values in st.secrets.sessionstate to initialize)(NOTE: Uses @classmethod in SessionState class to create an instance and manage not reinitializing)
session_state = ss.SessionState.get()

# 3. Run UserState class
if st.session_state.userstate == 5:
    st.switch_page(page=st.secrets.pages.paths[0])
else:
    user_state = us.UserState()

