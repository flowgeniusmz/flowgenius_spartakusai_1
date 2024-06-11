import streamlit as st

class SessionState:
    def __init__(self):
        self.initial_state = dict(st.secrets.sessionstate)
        self.query_params = bool(st.query_params)
        self._initialize_attributes()
        self._initialize_state()

    def _initialize_attributes(self):
        self.initial_state['queryparams'] = self.query_params
        self.initial_state['termscontent'] = self.set_file_content(key="termscontent", filepath=st.secrets.paths.terms)
        self.initial_state['userstatecomplete'] = False
        if not self.query_params:
            self.initial_state['userstate'] = 0
            self.initial_state['usertype'] = "guest"
        else:
            self.initial_state['userstate'] = 4
            self.initial_state['usertype'] = "existing"
        
    def _initialize_state(self):
        for key, value in self.initial_state.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @classmethod
    def get(cls):
        if 'session_state_instance' not in st.session_state:
            st.session_state.session_state_instance = cls()
        return st.session_state.session_state_instance

    def update(self, **kwargs):
        for key, value in kwargs.items():
            st.session_state[key] = value

    def get_value(self, key):
        return st.session_state.get(key, None)

    def set_file_content(self, key, filepath):
        try:
            with open(filepath, 'r') as file:
                content = file.read()
            st.session_state[key] = content
        except FileNotFoundError:
            st.session_state[key] = "File not found."


# class SessionState1:
#     def __init__(self, **kwargs):
#         for key, value in kwargs.items():
#             if key not in st.session_state:
#                 st.session_state[key] = value

#     @classmethod
#     def get(cls, **kwargs):
#         if 'session_state_instance' not in st.session_state:
#             st.session_state.session_state_instance = cls(**kwargs)
#         return st.session_state.session_state_instance

#     def update(self, **kwargs):
#         for key, value in kwargs.items():
#             st.session_state[key] = value

#     def get_value(self, key):
#         return st.session_state.get(key, None)



### EXAMPLE USAGE
# import streamlit as st
# from classes.class0_pagesetup import PageSetup
# from classes.class1_payment import Payment
# from session_state import SessionState  # Adjust the import path as needed

# 1. Set ST PAGE CONFIG
# st.set_page_config(
#     page_icon=st.secrets.app.icon,
#     page_title=st.secrets.app.title,
#     layout=st.secrets.app.layout,
#     initial_sidebar_state=st.secrets.app.sidebar
# )

# # 2. Initialize Session State with values from st.secrets.sessionstate
# initial_state = dict(st.secrets.sessionstate)
# query_params = st.experimental_get_query_params()
# initial_state['userstate'] = 0 if not query_params else 4

# session_state = SessionState.get(**initial_state)

# # 3. Set Page Setup
# PageSetup(pagenumber=session_state.get_value('userstate')).display_manual()

# c = st.checkbox("proceed")
# if c:
#     Payment().display_payment()
#     # Update session state if needed
#     session_state.update(userstate=1)  # Example update
