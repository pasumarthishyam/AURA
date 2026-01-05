"""
Search Tools - DuckDuckGo (primary) with Google (fallback)
"""
from tools.base_tool import BaseTool
import logging

logger = logging.getLogger("AURA.Tools.Search")


class WebSearchTool(BaseTool):
    """
    Web search tool using DuckDuckGo as primary and Google as fallback.
    """
    name = "SEARCH_WEB"

    def run(self, query: str, num_results: int = 5) -> str:
        """
        Search the web. Tries DuckDuckGo first, falls back to Google.
        """
        logger.info(f"Searching for: {query}")
        
        # Try DuckDuckGo first (primary)
        result = self._search_duckduckgo(query, num_results)
        if result:
            logger.info("DuckDuckGo search successful")
            return result
        
        # Fallback to Google
        logger.warning("DuckDuckGo failed, trying Google fallback...")
        result = self._search_google(query, num_results)
        if result:
            logger.info("Google fallback successful")
            return result
        
        return "No search results found from any search engine."

    def _search_duckduckgo(self, query: str, num_results: int) -> str:
        """Search using DuckDuckGo."""
        try:
            from ddgs import DDGS
            
            results = []
            with DDGS() as ddgs:
                for i, r in enumerate(ddgs.text(query, max_results=num_results)):
                    results.append(
                        f"{i+1}. {r.get('title', 'No title')}\n"
                        f"   URL: {r.get('href', 'No URL')}\n"
                        f"   {r.get('body', 'No description')}"
                    )
            
            if results:
                return "\n\n".join(results)
            return None
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return None

    def _search_google(self, query: str, num_results: int) -> str:
        """Search using Google (fallback)."""
        try:
            from googlesearch import search
            
            results = []
            for i, url in enumerate(search(query, num_results=num_results, advanced=True)):
                results.append(
                    f"{i+1}. {url.title}\n"
                    f"   URL: {url.url}\n"
                    f"   {url.description}"
                )
            
            if results:
                return "\n\n".join(results)
            return None
            
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return None


# Keep legacy GoogleSearchTool for backwards compatibility
class GoogleSearchTool(BaseTool):
    """
    Legacy Google search tool - redirects to WebSearchTool.
    """
    name = "SEARCH_GOOGLE"

    def __init__(self):
        self._web_search = WebSearchTool()

    def run(self, query: str, num_results: int = 3) -> str:
        """Redirect to unified web search."""
        return self._web_search.run(query, num_results)
