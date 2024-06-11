import streamlit as st
from streamlit.components.v1 import html
from streamlit_extras.stylable_container import stylable_container as sc
from typing import Literal
from classes import clsUtilities as ut
import time
from datetime import datetime
import json
from tempfile import NamedTemporaryFile
import base64

class PageSetup:
    def __init__(self, page_number: int):
        self.pagenumber = page_number
        self.initialize()
    
    def initialize(self):
        self._initialize_page_attributes()
        self._initialize_page_config()
        self._initialize_page_display()

    def _initialize_page_attributes(self):
        self.page_count = st.secrets.app.pagecount
        self.attributes = st.secrets.lists.pageattributes
        self.pages = dict(st.secrets.pages)
        for attr in self.attributes:
            setattr(self, attr[:-1], self.pages[attr][self.pagenumber])         
            
    def _initialize_page_config(self):
        self.pageconfig = {
            'title': self.title,
            'subtitle': self.subtitle,
            'path': self.path,
            'icon': self.icon,
            'header': self.header,
            'description': self.description,
            'about': self.about,
            'backgroundtype': self.backgroundtype,
            'backgroundstyle': self.backgroundstyle
            }
    
    def _initialize_page_display(self):
        PageUtilities.display_page_styling()
        PageUtilities.display_background_page1(type=self.backgroundtype, style=self.backgroundstyle)
        PageUtilities.get_title_page(title=self.title, subtitle=self.subtitle, pagenumber=self.pagenumber, div=True)

class PageUtilities:
    @staticmethod
    def display_background_page(type: Literal["logo", "coach", "wrestler"], style: Literal["background_page", "background_dialog", "styling_page"]="background_page"):
        style_template = PageUtilities.get_style_template(style_type=style)
        paths = dict(st.secrets.paths)
        default = st.secrets.paths.logo
        image_path = paths.get(type, default)
        encoded_image = AppUtilities.encode_image(image_path=image_path)
        background = style_template.format(encoded_image)
        st.markdown(body=background, unsafe_allow_html=True)

    @staticmethod
    def display_background_dialog(type: Literal["dialog1", "dialog2", "dialog3", "dialog4"], style: Literal["background_page", "background_dialog", "styling_page"]="background_dialog"):
        style_template = PageUtilities.get_style_template(style_type=style)
        paths = dict(st.secrets.paths)
        default = st.secrets.paths.dialog1
        image_path = paths.get(type, default)         
        encoded_image = AppUtilities.encode_image(image_path=image_path)
        background = style_template.format(encoded_image)
        st.markdown(body=background, unsafe_allow_html=True)

    @staticmethod
    def display_background_page1(type: Literal["logo", "coach", "wrestler"], style: Literal["background_page", "background_dialog", "styling_page"]="background_page"):
        """
        Displays the background dialog with the specified type and style.

        Args:
            type (Literal["dialog1", "dialog2", "dialog3", "dialog4"]): The type of dialog to display.
            style (Literal["background_page", "background_dialog", "styling_page"], optional): The style template to use. Defaults to "background_dialog".
        """
        style_template = "<div style='background-image: url(data:image/png;base64,{});'></div>"
        encoded_key = f'encoded{type}'

        # Ensure the images are encoded and stored in session state
        if encoded_key not in st.session_state:
            ImageUtilities.get_encoded_images()

        # Retrieve the encoded image from session state
        encoded_image = st.session_state.get(encoded_key, '')

        background = style_template.format(encoded_image)
        st.markdown(body=background, unsafe_allow_html=True)


    @staticmethod
    def display_background_dialog1(type: Literal["dialog1", "dialog2", "dialog3", "dialog4"], style: Literal["background_page", "background_dialog", "styling_page"] = "background_dialog"):
        """
        Displays the background dialog with the specified type and style.

        Args:
            type (Literal["dialog1", "dialog2", "dialog3", "dialog4"]): The type of dialog to display.
            style (Literal["background_page", "background_dialog", "styling_page"], optional): The style template to use. Defaults to "background_dialog".
        """
        style_template = "<div style='background-image: url(data:image/png;base64,{});'></div>"
        encoded_key = f'encoded{type}'

        # Ensure the images are encoded and stored in session state
        if encoded_key not in st.session_state:
            ImageUtilities.get_encoded_images()

        # Retrieve the encoded image from session state
        encoded_image = st.session_state.get(encoded_key, '')

        background = style_template.format(encoded_image)
        st.markdown(body=background, unsafe_allow_html=True)

    @staticmethod
    def display_page_styling(style: Literal["background_page", "background_dialog", "styling_page"]="styling_page"):
        styling_path = st.secrets.paths.css
        style_template = PageUtilities.get_style_template(style_type=style)
        styling_content = AppUtilities.get_file_content(file_path=styling_path)
        styling = style_template.format(styling_content)
        st.markdown(body=styling, unsafe_allow_html=True)

    @staticmethod
    def get_style_template(style_type: Literal["background_page", "background_dialog", "styling_page", "title_app", "title_page"]):
        styles = dict(st.secrets.styles)
        default = st.secrets.styles.background_page
        style_template = styles.get(style_type, default)
        return style_template
    
    @staticmethod
    def get_styled_container(height: int=None, border: bool=False):
        styleouter = st.secrets.styles.style_container1
        styleinner = st.secrets.styles.style_container2
        outer = sc(key="outer", css_styles=styleouter)
        with outer:
            inner = sc(key="inner", css_styles=styleinner)
            with inner:
                if height is not None:
                    container = st.container(height=height, border=border)
                else:
                    container = st.container(border=border)
        return container
    
    @staticmethod
    def get_title_app(div: bool=True):
        title = st.secrets.app.title
        subtitle = st.secrets.app.subtitle
        style_template = PageUtilities.get_style_template(style_type="title_app")
        style = style_template.format(title, subtitle)
        title_container = st.container()
        with title_container:
            title_cols = st.columns([10, 3])
            with title_cols[0]:
                st.markdown(body=style, unsafe_allow_html=True)
            with title_cols[1]:
                PageUtilities.get_usertype_menu()
        if div:
            st.divider()

    @staticmethod
    def get_title_page(title: str, subtitle: str, pagenumber: int, div: bool=True):
        style_template = PageUtilities.get_style_template(style_type="title_page")
        style = style_template.format(title, subtitle)
        title_container = st.container()
        with title_container:
            title_cols = st.columns([10,3])
            with title_cols[0]:
                st.markdown(body=style, unsafe_allow_html=True)
            with title_cols[1]:
                PageUtilities.get_nav_menu(pagenumber=pagenumber)
        if div:
            st.divider()


    @staticmethod
    def get_nav_menu(pagenumber: int):
        pages = dict(st.secrets.pages)
        pagecount = st.secrets.app.pagecount
        nav_menu = st.popover(label="Menu", use_container_width=True)
        with nav_menu:
            for i in range(pagecount):
                st.page_link(page=pages['paths'][i], label=pages['subtitles'][i], disabled=(pagenumber == i))
        return nav_menu
    
    @staticmethod
    def get_usertype_menu():
        usertype_menu = st.popover(label="Try It Now", use_container_width=True)
        with usertype_menu:
            existuser_button = st.button(label="Login", key="existuser_button", type="primary", use_container_width=True)
            newuser_button = st.button(label="Sign Up", key="newuser_button", type="primary", use_container_width=True)
            if existuser_button:
                st.session_state.userstate = 4
                st.rerun()
            if newuser_button:
                st.session_state.userstate = 2
                st.rerun()
    
    @staticmethod
    def get_header(type: Literal["blue", "gray", "green"], text: str):
        if type == "blue":
            content = st.secrets.styles.style_header3_blue.format(text)
        elif type == "gray":
            content = st.secrets.styles.style_header2_gray.format(text)
        elif type == "green":
            content = st.secrets.styles.style_header1_green.format(text)
        header = st.markdown(body=content, unsafe_allow_html=True)
        return header

    

class AppUtilities:
    @staticmethod
    def encode_image(image_path: str):
        with open(file=image_path, mode="rb") as image_file:
            encoded_image = base64.b64encode(s=image_file.read()).decode()
        return encoded_image
    
    @staticmethod
    def get_file_content(file_path: str):
        with open(file=file_path, mode="rb") as file:
            content = file.read()
        return content


class ImageUtilities:
    @staticmethod
    @st.cache_data
    def get_encoded_images():
        """
        Encodes images from the paths specified in st.secrets.imagepaths
        and sets them in the session state.
        """
        imagepaths = dict(st.secrets.imagepaths)
        
        for key, path in imagepaths.items():
            encoded_image = AppUtilities.encode_image(path)
            st.session_state[f'encoded{key}'] = encoded_image
        



### NOTES
# [:-1] in setattr removes the trailing s from the attributes list (titleS--> title)
# setattr syntax setattr(object, name, value) object is the pageset instance, name is the trailing attribute, and value is that value for the page number
# You end up with a dynamic loop that will automaticall create self.title, self.subtitle, etc
#In the PageSetup Class
# In the PageSetup class example, setattr is used to dynamically set multiple attributes based on the contents of the st.secrets.pages dictionary. Here's the relevant part:

# python
# Copy code
# def _initialize_page_attributes(self):
#     attributes = ['titles', 'subtitles', 'paths', 'icons', 'headers', 'descriptions', 'abouts']
#     for attr in attributes:
#         setattr(self, attr[:-1], self.pages[attr][self.page_num])
# This loop does the following for each attribute name in attributes:

# attr: Holds the current attribute name from the list (e.g., "titles").
# attr[:-1]: Removes the last character from the attribute name (e.g., "titles" becomes "title").
# self.pages[attr][self.page_num]: Retrieves the value for the current page number from the dictionary (e.g., self.pages['titles'][0]).
# setattr(self, attr[:-1], self.pages[attr][self.page_num]): Sets the attribute on the instance (e.g., self.title).
# So, if attr is "titles", attr[:-1] becomes "title", and setattr(self, 'title', value) sets self.title to the value retrieved from the dictionary.






#
#
#