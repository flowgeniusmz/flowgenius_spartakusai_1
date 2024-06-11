import streamlit as st
from openai import OpenAI
from tavily import TavilyClient
from typing import Literal
from classes import clsPageSetup as ps
import time
import json
import pandas as pd
from googlemaps import places, geocoding, addressvalidation
from googlemaps import Client
from yelpapi import YelpAPI

client = OpenAI(api_key=st.secrets.openai.api_key)
tavClient = TavilyClient(api_key=st.secrets.tavily.api_key)
googleClient = Client(key=st.secrets.google.maps_api_key)
yelpClient = YelpAPI(api_key=st.secrets.yelp.api_key)

class Assistant:
    def __init__(self, assistant_id, thread_id):
        self.assistantid = assistant_id
        self.threadid = thread_id
        self.messages = AssistantUtilities.retrieve_messages(thread_id=thread_id)
        self.prompt = None
        self.response = None
        self.initialize_display()

    def initialize_display(self):
        self.chatcontainer = AssistantUtilities.get_chat_container(height=400, border=False)
        self.prompt = AssistantUtilities.get_prompt_input(placeholder="Enter your message here...")
        with self.chatcontainer:
            for message in self.messages:
                AssistantUtilities.add_message_to_display(chat_container=self.chatcontainer, role=message.role, content=message.content[0].text.value)

        if self.prompt:
            AssistantUtilities.add_message_to_display(self.chatcontainer, role="user", content=self.prompt)
            self.run_assistant()

    def run_assistant(self):
        self.promptmessage = AssistantUtilities.create_message(thread_id=self.threadid, role="user", content=self.prompt)
        self.run = AssistantUtilities.create_run(thread_id=self.threadid, assistant_id=self.assistantid)
        while self.run.status == "in_progress" or self.run.status == "queued":
            st.toast("processing")
            time.sleep(2)
            self.run = AssistantUtilities.retrieve_run(run_id=self.run.id, thread_id=self.threadid)
            if self.run.status == "completed":
                st.toast("completed")
                self.messages = AssistantUtilities.retrieve_messages(thread_id=self.threadid)
                for message in self.messages:
                    if message.role == "assistant" and message.run_id == self.run.id:
                        self.response = message.content[0].text.value
                        self.response_json = json.loads(self.response)
                        self.displayresponse = self.response_json['response_to_user']
                        self.suggested_prompts = self.response_json['suggested_prompts']
                        #self.fannotations = message.content[0].text.annotations
                        #self.adfads = f"{self.response} | {self.fannotations}"
                AssistantUtilities.add_message_to_display(chat_container=self.chatcontainer, role="assistant", content=self.displayresponse, suggestions=self.suggested_prompts)
            elif self.run.status == "requires_action":
                st.toast("running tool outputs")
                self.tool_outputs = AssistantUtilities.run_tool_calls(run=self.run)
                self.run = AssistantUtilities.submit_tool_outputs(run_id=self.run.id, thread_id=self.threadid, tool_outputs=self.tool_outputs)




class AssistantUtilities:
    @staticmethod
    def create_thread():
        thread = client.beta.threads.create()
        return thread
    
    @staticmethod
    def create_run(thread_id: str, assistant_id: str):
        run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
        return run
    
    @staticmethod
    def create_message(thread_id: str, role: Literal["user", "assistant"], content: str):
        message = client.beta.threads.messages.create(thread_id=thread_id, role=role, content=content)
        return message
    
    @staticmethod
    def retrieve_run(run_id: str, thread_id: str):
        run = client.beta.threads.runs.retrieve(run_id=run_id, thread_id=thread_id)
        return run
    
    @staticmethod
    def retrieve_messages(thread_id: str):
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        return messages
    
    @staticmethod
    def get_chat_container(height: int=None, border: bool=False):
        container = ps.PageUtilities.get_styled_container(height=height, border=border)
        return container
    
    @staticmethod
    def get_prompt_input(placeholder: str):
        container = st.container(border=False, height=100)
        with container:
            prompt = st.chat_input(placeholder=placeholder)
        return prompt
    
    @staticmethod
    def add_message_to_display(chat_container, role, content, suggestions=None):
        with chat_container:
            with st.chat_message(name=role):
                st.markdown(body=content)
            
            if suggestions is not None:
                suggestion_container = st.container(border=False)

                with suggestion_container:
                    suggestionpop = st.popover(label="Suggested Prompts", use_container_width=True)
                    with suggestionpop:
                        for key, value in suggestions.items():
                            st.button(label=f"{value}", use_container_width=True)

    @staticmethod
    def run_tool_calls(run):
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []
        for tool_call in tool_calls:
            tool_id = tool_call.id
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            tool_output = getattr(Tools, tool_name)(**tool_args)
            tool_outputs.append({"tool_call_id": tool_id, "output": tool_output})
        return tool_outputs
    
    @staticmethod
    def submit_tool_outputs(run_id, thread_id, tool_outputs):
        run = client.beta.threads.runs.submit_tool_outputs(run_id=run_id, thread_id=thread_id, tool_outputs=tool_outputs)
        return run

    @staticmethod
    def get_suggested_prompts(prompt: str, response: str):
        content = f"prompt: {prompt} response: {response}"
        message_base = [{"role":"system","content":[{"type":"text","text":"Return 4 suggested prompts based on the provided user prompt and assistant response. \n\nOUTPUT: \n {\"suggestedprompt1\": \"prompt1\", \"suggestedprompt2\": \"prompt2\", \"suggestedprompt3\": \"prompt3\", \"suggestedprompt4\": \"prompt4\"}"}]},{"role":"user","content":[{"type":"text","text":"{\"prompt\": \"Research about calling someone a \\\"chad\\\" means. Then explain why you are a chad\", \"response\": \"Calling someone a \\\"Chad\\\" typically refers to a stereotypical alpha male characterized as attractive, successful, muscular, cocky, and popular among women. The term originated as a pejorative for an airheaded alpha male who excelled with women. In online communities like incel forums, a Chad is viewed as a sexually active, genetically superior man, often representing the pinnacle of genetic fitness. The term can carry both positive and negative connotations in internet culture, symbolizing confidence, charisma, and social prowess.\nWhy I am a \\\"Chad\\\":\nAs your research assistant, I embody the positive aspects of a \\\"Chad\\\" by being confident, knowledgeable, and efficient in providing you with the information you need. My capabilities allow me to navigate the vast expanse of the internet with ease, ensuring that I deliver accurate and relevant results, much like how a \\\"Chad\\\" would confidently handle any situation.\"}"}]},{"role":"assistant","content":[{"type":"text","text":"{\"suggestedprompt1\": \"Can you provide more examples of popular Chad memes?\", \"suggestedprompt2\": \"What are some other internet slang terms similar to 'Chad'?\", \"suggestedprompt3\": \"How has the term 'Chad' evolved over time in internet culture?\", \"suggestedprompt4\": \"Can you explain the 'Virgin vs. Chad' meme in more detail?\"}"}]}, {"role": "user", "content": content}]
        model = "gpt-4o"
        temp = 0
        max = 1000
        responseformat = {"type": "json_object"}
        response1 = client.chat.completions.create(messages=message_base, max_tokens=max, temperature=temp, model=model, response_format=responseformat)
        rcontent = response1.choices[0].message.content
        return rcontent

class Tools:
    def tavily_search(query: str):
        """
        Performs an advanced search using the Tavily client to gather comprehensive information about a business.
        
        Parameters:
            query (str): The search query describing the business or related information.
        
        Returns:
            dict: The search results including raw content and answers.
        """
        response = tavClient.search(query=query, search_depth="advanced", include_raw_content=True, include_answer=True, max_results=7)
        return response
    
    def google_places_search(query: str):
        """
        Searches for business information using Google Places to gather details on location, ratings, and more.
        
        Parameters:
            query (str): The search query describing the business.
        
        Returns:
            dict: The search results with detailed information about the business.
        """
        response = places.places(client=googleClient, query=query, region="US")
        return response
    
    def google_address_validation(address_lines: list):
        """
        Validates business addresses using Google Address Validation to ensure accuracy for insurance documentation.
        
        Parameters:
            address_lines (list): The address lines to be validated.
        
        Returns:
            dict: The validation results including any corrections or standardizations.
        """
        response = addressvalidation.addressvalidation(client=googleClient, addressLines=address_lines, regionCode="US", enableUspsCass=True)
        return response

    def google_geocode(address_lines: list):
        """
        Geocodes business addresses using Google Geocoding to obtain latitude and longitude for location verification.
        
        Parameters:
            address_lines (list): The address lines to be geocoded.
        
        Returns:
            dict: The geocoding results with latitude and longitude coordinates.
        """
        response = geocoding.geocode(client=googleClient, address=address_lines, region="US")
        return response
    
    def yelp_query_search(query: str, zipcode: str):
        """
        Performs a search query using Yelp to find businesses based on term and location, useful for insurance research.
        
        Parameters:
            query (str): The search query describing the type of business.
            zipcode (str): The zipcode of the business location.
        
        Returns:
            list: A list of businesses with basic information.
        """
        response = yelpClient.search_query(term=query, location=zipcode)
        businesses = response['businesses']
        return businesses

    def yelp_business_search(business_id: str):
        """
        Searches for detailed information about a business using its Yelp ID to gather in-depth data for insurance purposes.
        
        Parameters:
            business_id (str): The Yelp ID of the business.
        
        Returns:
            dict: The detailed information about the business.
        """
        response = yelpClient.business_query(id=business_id)
        return response

    def yelp_search(query: str, zipcode: str):
        """
        Performs a search query using Yelp and retrieves detailed information for each business, aggregating useful data for insurance analysis.
        
        Parameters:
            query (str): The search query describing the type of business.
            zipcode (str): The zipcode of the business location.
        
        Returns:
            pd.DataFrame: A DataFrame containing detailed information about the businesses.
        """
        business_records = []
        businesses = yelpClient.search_query(term=query, location=zipcode)['businesses']
        
        for business in businesses:
            business_id = business.get('id')
            detailed_info = yelpClient.business_query(id=business_id)
            business_record = {
                'id': business.get('id'),
                'alias': business.get('alias'),
                'name': business.get('name'),
                'image_url': business.get('image_url'),
                'is_closed': business.get('is_closed'),
                'url': business.get('url'),
                'review_count': business.get('review_count'),
                'rating': business.get('rating'),
                'latitude': business['coordinates'].get('latitude') if business.get('coordinates') else None,
                'longitude': business['coordinates'].get('longitude') if business.get('coordinates') else None,
                'phone': business.get('phone'),
                'display_phone': business.get('display_phone'),
                'distance': business.get('distance'),
                'address1': business['location'].get('address1') if business.get('location') else None,
                'address2': business['location'].get('address2') if business.get('location') else None,
                'address3': business['location'].get('address3') if business.get('location') else None,
                'city': business['location'].get('city') if business.get('location') else None,
                'zip_code': business['location'].get('zip_code') if business.get('location') else None,
                'country': business['location'].get('country') if business.get('location') else None,
                'state': business['location'].get('state') if business.get('location') else None,
                'display_address': ", ".join(business['location'].get('display_address', [])) if business.get('location') else None,
                'is_claimed': detailed_info.get('is_claimed'),
                'cross_streets': detailed_info['location'].get('cross_streets') if detailed_info.get('location') else None,
                'photos': ", ".join(detailed_info.get('photos', [])),
                'hours': detailed_info.get('hours', [{}])[0].get('open', []),
                'is_open_now': detailed_info.get('hours', [{}])[0].get('is_open_now'),
                'transactions': ", ".join(detailed_info.get('transactions', []))
            }
            
            # Add categories to the record
            categories = business.get('categories', [])
            category_aliases = [cat['alias'] for cat in categories]
            category_titles = [cat['title'] for cat in categories]
            business_record['categories_alias'] = ", ".join(category_aliases)
            business_record['categories_title'] = ", ".join(category_titles)

            business_records.append(business_record)
        yelp_business_records_df = pd.DataFrame(business_records)
        return yelp_business_records_df
    
    


# client.beta.threads.runs.cancel(thread_id="thread_TAzJIkW9YIXcDGExBU92YOwj", run_id="run_6txxNXEm1O0dKuZgVZE9PrMu")