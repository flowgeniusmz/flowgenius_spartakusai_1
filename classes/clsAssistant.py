import streamlit as st
from classes.clsTools import Tools
from openai import OpenAI
from typing import Literal, List
import json
import time

oaiClient = OpenAI(api_key=st.secrets.openai.api_key)

class Assistant:
    def __init__(self):
        self._initialize_attributes()
        self._initialize_display()

    def _initialize_attributes(self):
        self.assistantid = st.secrets.openai.assistant_id
        self.threadid = st.secrets.openai.thread_id
        self.thread_messages = AssistantUtilities.get_thread_messages(thread_id=self.threadid)
    
    def _initialize_display(self):
        self.chat_container = st.container(border=True, height=400)
        self.prompt_container = st.container(border=False, height=100)
        with self.chat_container:
            AssistantUtilities.display_chat_messages(container=self.chat_container, messages=self.thread_messages)
        with self.prompt_container:
            self.prompt = st.chat_input("Enter request here...")
            if self.prompt:
                self.prompt_message(content=self.prompt)

    def prompt_message(self, content: str):
        self.prompt_message = AssistantUtilities.create_thread_message(threadid=self.threadid, role="user", content=content)
        self.run = AssistantUtilities.create_run(thread_id=self.threadid, assistant_id=self.assistantid)
        self.run = AssistantUtilities.wait_on_run(run=self.run)
        self.thread_messages = AssistantUtilities.get_thread_messages(thread_id=self.threadid)
        self.get_response_message(run_id=self.run.id)

    def get_response_message(self, run_id: str):
        for thread_message in self.thread_messages:
            if thread_message.role == "assistant" and thread_message.run_id == run_id:
                self.response_message_id = thread_message.id
                self.response_message = thread_message.content[0].text.value
                AssistantUtilities.display_chat_message(container=self.chat_container, role="assistant", content=self.response_message)
                



class AssistantUtilities:
    @staticmethod
    def create_thread_message(threadid: str, role: Literal["user", "assistant"], content: str):
        thread_message = oaiClient.beta.threads.messages.create(thread_id=threadid, role=role, content=content)
        return thread_message
    
    @staticmethod
    def create_file(filepath: str):
        file = open(file=filepath, mode="rb")
        new_file = oaiClient.files.create(file=file, purpose="assistants")
        return file
    
    @staticmethod
    def get_attachment_object(fileid: str, tooltype: Literal["file_search", "code_interpreter"]):
        attachment_object = {"file_id": fileid, "tools": [{"type": tooltype}]}
        return attachment_object
    
    @staticmethod
    def create_thread():
        thread = oaiClient.beta.threads.create()
        threadid = thread.id
        return thread
    
    @staticmethod
    def create_run(thread_id: str, assistant_id: str):
        run = oaiClient.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
        return run
    
    @staticmethod
    def retrieve_run(run_id: str, thread_id: str):
        run = oaiClient.beta.threads.runs.retrieve(run_id=run_id, thread_id=thread_id)
        return run
    
    @staticmethod
    def get_thread_messages(thread_id: str, run_id: str=None):
        thread_messages = oaiClient.beta.threads.messages.list(thread_id=thread_id)
        return thread_messages
    
    @staticmethod
    def wait_on_run(run):
        while run.status == "queued" or run.status == "in_progress":
            time.sleep(2)
            st.toast("processing")
            run = AssistantUtilities.retrieve_run(run_id=run.id, thread_id=run.thread_id)
            if run.status == "completed":
                st.toast("complete")
                return run
            if run.status == "requires_action":
                st.toast("run tools")
                tool_outputs = []
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                for tool_call in tool_calls:
                    toolid = tool_call.id
                    toolname = tool_call.function.name
                    toolargs = json.loads(tool_call.function.arguments)
                    tooloutput = getattr(Tools, toolname)(**toolargs)
                    tool_outputs.append({"tool_call_id": toolid, "output": tooloutput})
                run = oaiClient.beta.threads.runs.submit_tool_outputs(run_id=run.id, thread_id=run.thread_id, tool_outputs=tool_outputs)

    @staticmethod
    def display_chat_messages(container, messages):
        with container:
            for message in messages:
                with st.chat_message(name=message.role):
                    st.markdown(body=message.content[0].text.value)

    @staticmethod
    def display_chat_message(container, content, role):
        with container:
            with st.chat_message(name=role):
                st.markdown(body=content)
    





