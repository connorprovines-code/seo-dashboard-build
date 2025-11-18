"""Backlink analysis service using DataForSEO"""
import httpx
import base64
from typing import List, Dict, Optional
from decimal import Decimal


class BacklinkService:
    """Service for backlink analysis via DataForSEO"""

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

    async def get_backlink_summary(self, target_domain: str) -> Dict:
        """
        Get backlink summary for a domain.
        Cost: ~$0.01 per request
        """
        try:
            payload = {
                "target": target_domain,
                "include_subdomains": True,
                "limit": 1
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/backlinks/summary/live",
                    json=[payload],
                    headers={
                        "Authorization": self.auth,
                        "Content-Type": "application/json"
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_summary_response(data)
                else:
                    return {"success": False, "error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_summary_response(self, data: Dict) -> Dict:
        """Parse backlink summary response"""
        try:
            tasks = data.get("tasks", [])
            if not tasks or tasks[0].get("status_code") != 20000:
                return {"success": False, "error": "No data returned"}

            result = tasks[0].get("result", [{}])[0]

            return {
                "success": True,
                "summary": {
                    "total_backlinks": result.get("backlinks", 0),
                    "referring_domains": result.get("referring_domains", 0),
                    "referring_ips": result.get("referring_ips", 0),
                    "referring_subnets": result.get("referring_subnets", 0),
                    "domain_rank": result.get("rank", 0),
                    "first_seen": result.get("first_seen"),
                    "last_seen": result.get("last_seen")
                }
            }
        except Exception as e:
            return {"success": False, "error": f"Parse error: {str(e)}"}

    async def get_backlinks(
        self,
        target_domain: str,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """
        Get detailed backlink list.
        Cost: ~$0.02 per 100 backlinks
        """
        try:
            payload = {
                "target": target_domain,
                "limit": limit,
                "offset": offset,
                "include_subdomains": True,
                "order_by": ["rank,desc"]
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/backlinks/backlinks/live",
                    json=[payload],
                    headers={
                        "Authorization": self.auth,
                        "Content-Type": "application/json"
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_backlinks_response(data)
                else:
                    return {"success": False, "error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_backlinks_response(self, data: Dict) -> Dict:
        """Parse backlinks response"""
        try:
            tasks = data.get("tasks", [])
            if not tasks or tasks[0].get("status_code") != 20000:
                return {"success": False, "error": "No data returned"}

            items = tasks[0].get("result", [{}])[0].get("items", [])

            backlinks = []
            for item in items:
                backlinks.append({
                    "url_from": item.get("url_from"),
                    "url_to": item.get("url_to"),
                    "domain_from": item.get("domain_from"),
                    "page_from_rank": item.get("page_from_rank"),
                    "domain_from_rank": item.get("domain_from_rank"),
                    "anchor": item.get("anchor"),
                    "link_attribute": item.get("link_attribute"),
                    "first_seen": item.get("first_seen"),
                    "last_seen": item.get("last_seen")
                })

            return {
                "success": True,
                "backlinks": backlinks,
                "count": len(backlinks)
            }
        except Exception as e:
            return {"success": False, "error": f"Parse error: {str(e)}"}

    async def get_referring_domains(
        self,
        target_domain: str,
        limit: int = 100
    ) -> Dict:
        """Get list of referring domains"""
        try:
            payload = {
                "target": target_domain,
                "limit": limit,
                "order_by": ["rank,desc"]
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/backlinks/referring_domains/live",
                    json=[payload],
                    headers={
                        "Authorization": self.auth,
                        "Content-Type": "application/json"
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_referring_domains_response(data)
                else:
                    return {"success": False, "error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_referring_domains_response(self, data: Dict) -> Dict:
        """Parse referring domains response"""
        try:
            tasks = data.get("tasks", [])
            if not tasks or tasks[0].get("status_code") != 20000:
                return {"success": False, "error": "No data returned"}

            items = tasks[0].get("result", [{}])[0].get("items", [])

            domains = []
            for item in items:
                domains.append({
                    "domain": item.get("domain"),
                    "backlinks": item.get("backlinks"),
                    "rank": item.get("rank"),
                    "first_seen": item.get("first_seen"),
                    "last_seen": item.get("last_seen")
                })

            return {
                "success": True,
                "domains": domains,
                "count": len(domains)
            }
        except Exception as e:
            return {"success": False, "error": f"Parse error: {str(e)}"}

    @staticmethod
    def estimate_cost(operation: str, count: int = 1) -> Decimal:
        """Estimate API costs"""
        costs = {
            "summary": Decimal("0.01"),
            "backlinks": Decimal("0.0002"),  # per backlink
            "referring_domains": Decimal("0.0001")  # per domain
        }
        return costs.get(operation, Decimal("0.01")) * count
