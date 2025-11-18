"""DataForSEO API service wrapper"""
import httpx
import base64
from typing import List, Dict, Optional
from decimal import Decimal

from app.core.config import settings


class DataForSEOService:
    """Service for interacting with DataForSEO APIs"""

    BASE_URL = "https://api.dataforseo.com/v3"

    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password
        self.auth = self._get_auth_header()

    def _get_auth_header(self) -> str:
        """Generate Basic Auth header"""
        credentials = f"{self.login}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    async def test_credentials(self) -> Dict:
        """Test if credentials are valid"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/dataforseo_labs/google/available_filters",
                    headers={"Authorization": self.auth},
                    timeout=30.0
                )

                if response.status_code == 200:
                    return {"success": True, "message": "Credentials valid"}
                else:
                    return {
                        "success": False,
                        "error": f"Invalid credentials: {response.status_code}"
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_keyword_data(
        self,
        keywords: List[str],
        location_code: int = 2840,  # USA
        language_code: str = "en"
    ) -> Dict:
        """
        Get keyword data (volume, difficulty, CPC, competition)
        Cost: $0.07 per 1,000 keywords
        """
        try:
            payload = {
                "keywords": keywords,
                "location_code": location_code,
                "language_code": language_code
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/dataforseo_labs/google/bulk_keyword_difficulty/live",
                    json=[payload],
                    headers={
                        "Authorization": self.auth,
                        "Content-Type": "application/json"
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_keyword_response(data)
                else:
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}",
                        "details": response.text
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_keyword_response(self, data: Dict) -> Dict:
        """Parse DataForSEO keyword response"""
        try:
            results = []
            tasks = data.get("tasks", [])

            for task in tasks:
                if task.get("status_code") == 20000:
                    task_results = task.get("result", [])
                    for result in task_results:
                        items = result.get("items", [])
                        for item in items:
                            keyword_info = item.get("keyword_info", {})
                            keyword_properties = item.get("keyword_properties", {})

                            results.append({
                                "keyword": item.get("keyword"),
                                "search_volume": keyword_info.get("search_volume"),
                                "cpc": keyword_info.get("cpc"),
                                "competition": keyword_info.get("competition"),
                                "keyword_difficulty": keyword_properties.get("keyword_difficulty"),
                            })

            return {
                "success": True,
                "keywords": results,
                "count": len(results)
            }
        except Exception as e:
            return {"success": False, "error": f"Parse error: {str(e)}"}

    async def get_serp_results(
        self,
        keyword: str,
        location_code: int = 2840,
        language_code: str = "en",
        depth: int = 100
    ) -> Dict:
        """
        Get SERP results for rank tracking
        Cost: $0.002 (live) or $0.0006 (standard)
        """
        try:
            payload = {
                "keyword": keyword,
                "location_code": location_code,
                "language_code": language_code,
                "device": "desktop",
                "depth": depth
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/serp/google/organic/live/advanced",
                    json=[payload],
                    headers={
                        "Authorization": self.auth,
                        "Content-Type": "application/json"
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_serp_response(data)
                else:
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_serp_response(self, data: Dict) -> Dict:
        """Parse DataForSEO SERP response"""
        try:
            results = []
            tasks = data.get("tasks", [])

            for task in tasks:
                if task.get("status_code") == 20000:
                    task_results = task.get("result", [])
                    for result in task_results:
                        items = result.get("items", [])
                        for item in items:
                            if item.get("type") == "organic":
                                results.append({
                                    "position": item.get("rank_absolute"),
                                    "url": item.get("url"),
                                    "domain": item.get("domain"),
                                    "title": item.get("title"),
                                    "description": item.get("description"),
                                })

            return {
                "success": True,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {"success": False, "error": f"Parse error: {str(e)}"}

    @staticmethod
    def estimate_keyword_research_cost(keyword_count: int) -> Decimal:
        """Estimate cost for keyword research"""
        # $0.07 per 1,000 keywords
        return Decimal(str(keyword_count * 0.00007))

    @staticmethod
    def estimate_rank_check_cost(check_count: int, live: bool = False) -> Decimal:
        """Estimate cost for rank checks"""
        cost_per_check = Decimal("0.002") if live else Decimal("0.0006")
        return cost_per_check * check_count
