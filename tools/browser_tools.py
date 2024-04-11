import json

import requests
import streamlit as st
from crewai import Agent, Task
from langchain.tools import tool
from unstructured.partition.html import partition_html


class BrowserTools():

  @tool("Scrape website content")
  def scrape_and_summarize_website(website):
    """Useful to scrape and summarize a website content"""
    url = "https://api.scraperapi.com/"
    payload = {
        'api_key': st.secrets['SCRAPER_API_KEY'],
        'url': website
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.get(url, params=payload, headers=headers)

    # Check for successful response
    if response.status_code == 200:
      data = json.loads(response.text)
      if 'error' not in data:
        # Process the HTML content
        elements = partition_html(text=data['html'])
        content = "\n\n".join([str(el) for el in elements])
        content = [content[i:i + 8000] for i in range(0, len(content), 8000)]

        summaries = []
        for chunk in content:
          agent = Agent(
              role='Principal Researcher',
              goal=
              'Do amazing researches and summaries based on the content you are working with',
              backstory=
              "You're a Principal Researcher at a big company and you need to do a research about a given topic.",
              allow_delegation=False)
          task = Task(
              agent=agent,
              description=
              f'Analyze and summarize the content bellow, make sure to include the most relevant information in the summary, return only the summary nothing else.\n\nCONTENT\n----------\n{chunk}'
          )
          summary = task.execute()
          summaries.append(summary)
        return "\n\n".join(summaries)
      else:
        return f"Error: {data['error']}"  # Handle potential errors from ScraperAPI
    else:
      return f"Error: Failed to scrape website (status code: {response.status_code})"

