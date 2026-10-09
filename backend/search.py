import os
import httpx
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class WebSearchProvider:
    def search(self, query: str) -> List[Dict]:
        raise NotImplementedError

class TavilySearchProvider(WebSearchProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://api.tavily.com/search"
        
    def search(self, query: str) -> List[Dict]:
        try:
            with httpx.Client() as client:
                response = client.post(
                    self.url,
                    json={"api_key": self.api_key, "query": query, "search_depth": "basic", "include_answer": False},
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                results = []
                for res in data.get("results", []):
                    # deduplicate urls
                    if not any(r["url"] == res.get("url") for r in results):
                        results.append({
                            "title": res.get("title", ""),
                            "url": res.get("url", ""),
                            "publisher": res.get("url", "").split("/")[2] if "//" in res.get("url", "") else "",
                            "snippet": res.get("content", ""),
                            "published_date": res.get("published_date")
                        })
                return results
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return []

class DDGSearchProvider(WebSearchProvider):
    def search(self, query: str) -> List[Dict]:
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                ddg_results = list(ddgs.text(query, max_results=5))
                results = []
                for res in ddg_results:
                    if not any(r["url"] == res.get("href") for r in results):
                        results.append({
                            "title": res.get("title", ""),
                            "url": res.get("href", ""),
                            "publisher": res.get("href", "").split("/")[2] if "//" in res.get("href", "") else "",
                            "snippet": res.get("body", ""),
                            "published_date": None
                        })
                return results
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return []

def get_search_provider() -> WebSearchProvider:
    provider = os.getenv("WEB_SEARCH_PROVIDER", "duckduckgo").lower()
    if provider == "tavily":
        key = os.getenv("TAVILY_API_KEY")
        if key:
            return TavilySearchProvider(key)
        else:
            logger.warning("TAVILY_API_KEY missing, falling back to DuckDuckGo")
            return DDGSearchProvider()
    
    return DDGSearchProvider()
