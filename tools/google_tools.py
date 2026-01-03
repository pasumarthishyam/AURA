from googlesearch import search
from typing import List

class GoogleSearchTool:
    """
    Performs Google searches.
    """
    def __init__(self):
        self.name = "SEARCH_GOOGLE"

    def run(self, query: str, num_results: int = 3) -> str:
        try:
            results = []
            # advanced=True returns objects with title, url, description
            # But the basic library might just return URLs. 
            # safe assumption: list of strings (urls) or use advanced=True if supported by the specific version installed.
            # We'll use the basic iterator for safety and just return URLs for now, 
            # or try to simple-scrape if we had libraries. 
            # For "Advanced" agent, URLs + snippet is better.
            # Let's assume standard behavior:
            for i, url in enumerate(search(query, num_results=num_results, advanced=True)):
                results.append(f"{i+1}. {url.title} - {url.url}\n   {url.description}")
            
            if not results:
                return "No results found."
            
            return "\n".join(results)
        except Exception as e:
            return f"Error executing Google Search: {str(e)}"
