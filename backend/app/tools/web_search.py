"""
Web Search Tool — Multi-provider real-time web search.

Provider priority:
  1. Tavily AI Search API  (when SEARCH_PROVIDER=tavily + SEARCH_API_KEY set)
  2. Serper.dev Google API (when SEARCH_PROVIDER=serper + SEARCH_API_KEY set)
  3. DuckDuckGo via duckduckgo-search library (free, no key, robust)
  4. DuckDuckGo Instant Answer API (lightweight fact lookup fallback)
"""

import re
import asyncio
import logging
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

import httpx

# Support both package names (ddgs is the renamed successor to duckduckgo_search)
try:
    from ddgs import DDGS
    _DDGS_AVAILABLE = True
except ImportError:
    try:
        from duckduckgo_search import DDGS  # type: ignore
        _DDGS_AVAILABLE = True
    except ImportError:
        _DDGS_AVAILABLE = False

from app.tools.base import BaseTool
from app.config import settings

logger = logging.getLogger("nova.tools.web_search")

# ---------------------------------------------------------------------------
# Provider helpers
# ---------------------------------------------------------------------------

async def _search_tavily(query: str, api_key: str, max_results: int = 5) -> Optional[List[Dict]]:
    """Query Tavily AI Search API — returns rich snippets with sources."""
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(
                "https://api.tavily.com/search",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "query": query,
                    "search_depth": "basic",
                    "include_answer": True,
                    "max_results": max_results,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                results = []
                # Tavily provides a synthesized answer — put it first
                if data.get("answer"):
                    results.append({
                        "title": "Summary",
                        "snippet": data["answer"],
                        "url": "",
                    })
                for r in data.get("results", []):
                    results.append({
                        "title": r.get("title", ""),
                        "snippet": r.get("content", r.get("snippet", "")),
                        "url": r.get("url", ""),
                    })
                if results:
                    logger.info(f"Tavily: {len(results)} results for '{query}'")
                    return results
    except Exception as e:
        logger.warning(f"Tavily search failed: {e}")
    return None


async def _search_serper(query: str, api_key: str, max_results: int = 5) -> Optional[List[Dict]]:
    """Query Serper.dev Google Search API."""
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
                json={"q": query, "num": max_results},
            )
            if resp.status_code == 200:
                data = resp.json()
                results = []
                # Answer box
                if data.get("answerBox", {}).get("answer"):
                    results.append({
                        "title": data["answerBox"].get("title", "Answer"),
                        "snippet": data["answerBox"]["answer"],
                        "url": data["answerBox"].get("link", ""),
                    })
                for r in data.get("organic", []):
                    results.append({
                        "title": r.get("title", ""),
                        "snippet": r.get("snippet", ""),
                        "url": r.get("link", ""),
                    })
                if results:
                    logger.info(f"Serper: {len(results)} results for '{query}'")
                    return results
    except Exception as e:
        logger.warning(f"Serper search failed: {e}")
    return None


async def _search_duckduckgo_library(query: str, max_results: int = 5) -> Optional[List[Dict]]:
    """
    Use the duckduckgo_search library for reliable DDG search.
    Runs in a thread pool since DDGS is synchronous.
    """
    if not _DDGS_AVAILABLE:
        logger.warning("duckduckgo_search library not available.")
        return None

    def _sync_search():
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "url": r.get("href", ""),
                })
        return results

    try:
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=1) as pool:
            results = await loop.run_in_executor(pool, _sync_search)
        if results:
            logger.info(f"DuckDuckGo library: {len(results)} results for '{query}'")
            return results
    except Exception as e:
        logger.warning(f"DuckDuckGo library search failed: {e}")

    return None


async def _search_duckduckgo_instant(query: str) -> Optional[List[Dict]]:
    """DuckDuckGo Instant Answer API — quick factual lookup (Wikipedia-backed)."""
    try:
        encoded = urllib.parse.quote_plus(query)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                abstract = data.get("AbstractText", "").strip()
                if abstract:
                    return [{
                        "title": data.get("Heading", query),
                        "snippet": abstract,
                        "url": data.get("AbstractURL", ""),
                    }]
    except Exception as e:
        logger.warning(f"DuckDuckGo Instant failed: {e}")
    return None


# ---------------------------------------------------------------------------
# Tool class
# ---------------------------------------------------------------------------

class WebSearchTool(BaseTool):
    """
    Real-time web search using a tiered multi-provider strategy.

    Priority:
      1. Tavily AI API  (SEARCH_PROVIDER=tavily + SEARCH_API_KEY)
      2. Serper.dev API (SEARCH_PROVIDER=serper + SEARCH_API_KEY)
      3. DuckDuckGo via duckduckgo-search library (no key required)
      4. DuckDuckGo Instant Answer API (lightweight fallback)
    """

    name = "web_search"
    description = (
        "Search the internet for current news, facts, tutorials, people, "
        "events, and any real-time information."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "The search query string. Be specific and natural, "
                    "e.g. 'latest developments in quantum computing 2024', "
                    "'who is the CEO of Tesla', 'Python asyncio tutorial'"
                ),
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return (1–10). Default is 5.",
                "default": 5,
            },
        },
        "required": ["query"],
    }
    requires_confirmation = False

    async def execute(self, query: str, max_results: int = 5, **kwargs) -> Any:
        max_results = max(1, min(10, int(max_results)))
        provider = getattr(settings, "SEARCH_PROVIDER", "duckduckgo").lower().strip()
        api_key = getattr(settings, "SEARCH_API_KEY", "").strip()

        results = None

        # 1. Tavily
        if provider == "tavily" and api_key:
            results = await _search_tavily(query, api_key, max_results)

        # 2. Serper
        elif provider == "serper" and api_key:
            results = await _search_serper(query, api_key, max_results)

        # 3. DDG library (free, no key, robust)
        if not results:
            results = await _search_duckduckgo_library(query, max_results)

        # 4. Last resort: DDG Instant Answer
        if not results:
            results = await _search_duckduckgo_instant(query)

        # 5. Graceful degradation
        if not results:
            logger.error(f"All web search providers failed for query: '{query}'")
            return {
                "query": query,
                "results": [{
                    "title": f"Search: {query}",
                    "snippet": (
                        f"I wasn't able to retrieve live search results for '{query}' right now. "
                        "Please try again or check your internet connection."
                    ),
                    "url": "",
                }],
                "source": "fallback",
            }

        return {
            "query": query,
            "results": results[:max_results],
            "result_count": len(results[:max_results]),
            "source": provider if (provider != "duckduckgo" and api_key) else "duckduckgo",
        }
