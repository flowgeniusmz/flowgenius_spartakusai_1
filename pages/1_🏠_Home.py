import streamlit as st
from classes import clsSessionState as ss, clsPageSetup as ps, clsUtilities as ut, clsAssistant as asst1, clsAssistant1 as asst
from openai import OpenAI

client = OpenAI(api_key=st.secrets.openai.api_key)
# Set Background
#ps.PageUtilities.display_background_page1(type="logo", style="background_page")
# Set Page
pagenumber = 0
pagesetup = ps.PageSetup(page_number=pagenumber)
threadid = client.beta.threads

asst = asst.Assistant(assistant_id=st.secrets.openai.assistant_id, thread_id=st.secrets.openai.thread_id)