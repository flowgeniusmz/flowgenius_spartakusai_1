import streamlit as st
import base64
from datetime import datetime


class Utilities:
    @staticmethod
    def encode_image(image_path: str):
        with open(file=image_path, mode="rb") as file:
            encoded_string = base64.b64encode(file.read()).decode()
        return encoded_string
    
    @staticmethod
    def get_datetime():
        value = datetime.now().isoformat()
        return value