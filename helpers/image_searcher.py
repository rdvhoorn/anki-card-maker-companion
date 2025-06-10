from pydantic_ai import Agent
import os
import requests

class ImageSearcher:

    def __init__(self):
        self.query_finetuning_agent = Agent(
            'openai:gpt-4o-mini',
            system_prompt="""
        You are an image search assistant.
        Given an input sentence or word, generate a concise image search query in English (a word or short sentence) that best captures the core visual concept or essence of the input.
        - Your output must be a natural-sounding search phrase.
        - It should be no more than 100 characters.
        - Focus on clarity and relevance to ensure useful search results.
        - Return only the query — no explanations.
        """)

    def do_google_image_search(self, query, num=10):
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "key": os.getenv("GOOGLE_API_KEY"),
            "cx": os.getenv("GOOGLE_CSE_ID"),
            "searchType": "image",
            "num": num
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json()

        def is_valid_image(link):
            # Very basic filtering, extend if needed
            return all(domain not in link for domain in [
                "instagram.com", "facebook.com", "lookaside", "media_id"
            ])

        return [item['link'] for item in results.get("items", []) if is_valid_image(item['link'])]

    def search_images(self, query):
        search_query = self.query_finetuning_agent.run_sync(query).output
        image_results = self.do_google_image_search(search_query)
        return image_results, search_query
    
    def search_images_without_finetuning(self, search_query):
        image_results = self.do_google_image_search(search_query)
        return image_results, search_query

