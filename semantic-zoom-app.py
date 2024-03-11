import streamlit as st
import os
import argparse
import pyperclip
import re
from groq import Groq
import json
from openai import OpenAI


SYSTEM_PROMPT = """
You are a summarization engine that outputs in markdown style. Users will feed you a piece of text, and you will return ONLY a summary of the content provided at a specified level of detail. Below are the allowed levels for your summaries:
- Summary Level 1: Headline Summary - Provide a 10-20 words with a 
single sentence bullet point headline that captures the overarching 
theme or main point for the content for each paragraph.

- Summary Level 2: Sentence-Level Summary - Provide a 20-30 words summary with 1-2 simple sentences that capture the main point in the text. 

- Summary Level 3: Paragraph Level-Summary - Provide a bullet points 
summary where each bullet points is a single sentence or headline 
(10-15 words) that captures the overarching theme or main point for 
each paragraph in the text.

- Summary Level 4: One-Paragraph Summary - Provide a 30-50 words summary 
where you introduce the main point, key arguments, or narrative arc 
in a short paragraph, adding context to the headline.

- Summary Level 5: Executive Summary - Provide a 50-80 words summary with 
the key points, findings, and implications in a high-level overview 
suitable for decision-making. 

- Summary Level 6: Structured Summary - Provide a 80-100 words summary 
where you break down the content into predefined relevant sections 
(one example would be: Introduction, Methods, Results, Conclusion if its a paper), 
providing a clear overview of each major component.

- Summary Level 7: Detailed Summary - Summarize in 100-120 words 
covering all main points and supporting arguments or evidence in a 
comprehensive summary that conveys a thorough understanding. 

Inputs from the user will always follow this structure:

'''
text input:
<user text input>
Summary level: <the summary level as a number from 1-10>
output:
'''"""


def save_to_json(summary_name, summary_content, filename):
    # Load existing data
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
    else:
        data = {}

    # Append new summary
    data[summary_name] = summary_content

    # Write back to the file
    with open(filename, 'w+') as f:
        json.dump(data, f)

    st.success('Summary saved successfully!')

@st.cache_data
def hierarchical_summarizer(text, summary_level,model_type="",model_name="mixtral-8x7b-32768"):
    """Generates summaries at different levels using an LLM"""
    if model_type=="chatgpt":
        client = OpenAI()
    else:
        client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),)
    
    chat_completion = client.chat.completions.create(
    messages=[
        {   
            "role": "system",
            "content": SYSTEM_PROMPT
         },
        {
            "role": "user",
            "content": f"""
            text input:
            {text}
            Summary level: {summary_level}
            output:
            """
        }
    ],
    model=model_name,
)
    return chat_completion.choices[0].message.content


st.title('Semantic Zoom Summarization')

if st.sidebar.checkbox('Prototype'):
    text = st.text_area('Enter your text here')
    summary_level = st.slider('Choose your summary level (1-10)', min_value=1, max_value=10, value=1)

    result = st.empty()  # Placeholder for the result


    # Update the summary in real time when the slider is changed
    if st.session_state.get('previous_summary_level', None) != summary_level:
        result.text('Updating summary...')
        transformed_text = hierarchical_summarizer(text, summary_level)
        st.session_state['transformed_text'] = transformed_text
        st.write(summary_level)
        st.write(f"{transformed_text}")

    st.session_state['previous_summary_level'] = summary_level
    summary_name = st.text_input('Enter the name of the summary', value=f'Summary {summary_level}')
    # Save summary button
    if st.button('Save Summary'):
        # Define the summary name and content
        summary_content = st.session_state['transformed_text']
        save_to_json(summary_name, summary_content, 'pdf_contents.json')
        
        
elif st.sidebar.checkbox("Bulk Generate"):
    model_type = st.selectbox('Choose the model type', ['groq', 'chatgpt'])
    text = st.text_area('Enter your text here')
    json_file = st.text_input('Enter the name of the JSON file to save the summaries', value='pdf_contents.json')
    if st.button("Bulk Generate Summaries"):
        save_to_json('original', text, json_file)
        for summary_level in range(1, 8):
            if model_type=="groq":
                transformed_text = hierarchical_summarizer(text, summary_level)
                st.markdown(f"{transformed_text}")
                save_to_json(f'Summary {summary_level}', transformed_text, json_file)
            elif model_type=="chatgpt":    
                transformed_text = hierarchical_summarizer(text, summary_level,model_type="chatgpt",model_name="gpt-4-turbo-preview")
                st.markdown(f"{transformed_text}")
                save_to_json(f'Summary {summary_level}', transformed_text, json_file)
            else:
                st.write("Please select a model type")
                
    
