import streamlit as st
from streamlit.components.v1 import html
from classes import clsPageSetup as ps, clsUtilities as ut
import base64

class UserState:
    def __init__(self):
        self._initialize_attributes()
        self._initialize_background()
        self._initialize_userstate()

    def _initialize_attributes(self):
        self.userstate = st.session_state.userstate
        self.userstatecomplete = st.session_state.userstatecomplete

    def _initialize_background(self):
        self.background = ps.PageUtilities.display_background_page(type="logo", style="background_page")
        self.header = ps.PageUtilities.get_title_app(div=True)

    def _initialize_userstate(self):
        if self.userstatecomplete:
            self.bypass()
        else:
            self.get()

    def get(self):
        if self.userstate == 1:
            self._userstate1()
        elif self.userstate == 2:
            self._userstate2()
        elif self.userstate == 3:
            self._userstate3()
        elif self.userstate == 4:
            self._userstate4()
        elif self.userstate == 5:
            self._userstate5()
        else:
            self._userstate1()
    
    def bypass(self):
        self._userstate5()

    
    def _userstate1(self):
        main_container = st.container(border=False)
        with main_container:
            buttoncontainer = ps.PageUtilities.get_styled_container()
            with buttoncontainer:
                newbtn = st.button("new", use_container_width=True)
                existbtn = st.button("exist", use_container_width=True)
            st.divider()
            chatcontainer = ps.PageUtilities.get_styled_container()
            with chatcontainer:
                dispcont = st.container(border=False, height=300)
                with dispcont:
                    with st.chat_message("assistant"):
                        st.markdown("Welcome to WrestleAI. Type below to try it out!")
            pcont = st.container(border=False, height=100)
            with pcont:
                guestprompt = st.chat_input(placeholder="Type here to try the assistant!")
            st.divider()
                
        if newbtn:
            st.session_state.usertype = "new"
            self._userstate_callback(next_userstate=2)
        if existbtn:
            st.session_state.usertype = "existing"
            self._userstate_callback(next_userstate=4)

    @st.experimental_dialog(title="New Account Information", width="large")
    def _userstate2(self):
        ps.PageUtilities.display_background_dialog1(type="dialog1", style="background_dialog")
        infoheader = ps.PageUtilities.get_header(type="blue", text="Please Complete Account Information Below")
        st.session_state.firstname = st.text_input(label="First Name", key="_firstname", type="default")
        st.session_state.lastname = st.text_input(label="Last Name", key="_lastname", type="default")
        st.session_state.email = st.text_input(label="Email Address", key="_email", type="default")
        st.session_state.userrole = st.radio(label="User Role", key="_userrole", options=st.secrets.lists.userroles, index=None, horizontal=True)
        create_button = st.button(label="Create Account", key="createbutton", type="primary")
        if create_button:
            st.session_state.fullname = f"{st.session_state.firstname} {st.session_state.lastname}"
            st.session_state.createddate = ut.Utilities.get_datetime()
            self._userstate_callback(next_userstate=3)
    
    @st.experimental_dialog(title="Terms, Conditions, and Payment", width="large")
    def _userstate3(self):
        ps.PageUtilities.display_background_dialog(type="dialog2", style="background_dialog")
        terms_container = st.container(border=False)
        payment_placeholder = st.empty()
        with terms_container:
            termsheader = ps.PageUtilities.get_header(type="blue", text="Terms and Conditions")
            terms_agree = st.checkbox(label="Please check this box to acknowledge and accept the WrestleAI terms and conditions before proceeding to payment.", value=False, key="_termstype")
            terms_pop = st.popover(label="View Terms and Conditions")
            with terms_pop:
                st.markdown(st.session_state.termscontent)
            if terms_agree:
                st.session_state.termstype = "acknowledged"
                with payment_placeholder.container(border=False):
                    payheader = ps.PageUtilities.get_header(type="blue", text="Proceed to Payment")
                    payproceed = html(st.secrets.stripe.stripejs.format(buy_button_id=st.secrets.stripe.buy_btn_dev, publisher_key=st.secrets.stripe.pub_key_dev, client_reference_id="testtest", customer_email="test@test.com"))

    @st.experimental_dialog(title="User Login", width="large")
    def _userstate4(self):
        ps.PageUtilities.display_background_dialog(type="dialog3", style="background_dialog")
        ps.PageUtilities.get_header(type="blue", text="Sign In to Your Account")
        st.session_state.username = st.text_input(label="Username", key="_username", type="default")
        st.session_state.password = st.text_input(label="Password", key="_password", type="password" )
        loginbutton = st.button(label="Login", key="loginbutton", type="primary")
        if loginbutton:
            st.session_state.logintype = "authenticated"
            self._userstate_callback(next_userstate=5)

    def _userstate5(self):
        st.session_state.userstatecomplete = True
        st.switch_page(page=st.secrets.pages.paths[0])

    def _userstate_callback(self, next_userstate):
        st.session_state.userstate = next_userstate
        st.rerun()