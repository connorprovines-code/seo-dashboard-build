"""Claude AI service for SEO insights"""
import httpx
from typing import List, Dict, Optional
import json

from app.core.config import settings


class ClaudeAIService:
    """Service for interacting with Anthropic Claude API"""

    BASE_URL = "https://api.anthropic.com/v1"
    MODEL = "claude-3-5-sonnet-20241022"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

    async def test_credentials(self) -> Dict:
        """Test if API key is valid"""
        try:
            # Simple test with minimal tokens
            response = await self.chat(
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10
            )
            return {"success": True, "message": "API key is valid"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2000,
        temperature: float = 1.0,
        system: Optional[str] = None
    ) -> Dict:
        """
        Send chat message to Claude.

        Args:
            messages: List of {"role": "user"|"assistant", "content": "..."}
            max_tokens: Maximum tokens in response
            temperature: Randomness (0-1)
            system: System prompt
        """
        payload = {
            "model": self.MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        if system:
            payload["system"] = system

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/messages",
                headers=self.headers,
                json=payload,
                timeout=60.0
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Claude API error: {response.status_code} - {response.text}")

    async def analyze_keyword_opportunities(
        self,
        keywords: List[Dict],
        project_domain: str
    ) -> Dict:
        """
        Analyze keywords and suggest opportunities.

        Args:
            keywords: List of keyword data with volume, difficulty, etc.
            project_domain: User's domain
        """
        keywords_text = "\n".join([
            f"- {k['keyword_text']}: Volume {k.get('search_volume', 'N/A')}, "
            f"Difficulty {k.get('keyword_difficulty', 'N/A')}, "
            f"CPC ${k.get('cpc', 'N/A')}"
            for k in keywords[:50]  # Limit to top 50
        ])

        system_prompt = f"""You are an expert SEO consultant analyzing keywords for {project_domain}.
Provide actionable insights on:
1. Best keyword opportunities (high volume, low difficulty)
2. Quick wins (keywords likely to rank quickly)
3. Content gaps (keywords that need new content)
4. Strategic recommendations

Be specific and data-driven."""

        messages = [{
            "role": "user",
            "content": f"Analyze these keywords and provide SEO recommendations:\n\n{keywords_text}"
        }]

        response = await self.chat(
            messages=messages,
            system=system_prompt,
            max_tokens=1500
        )

        return {
            "success": True,
            "analysis": response["content"][0]["text"],
            "usage": response.get("usage", {})
        }

    async def analyze_serp_competition(
        self,
        keyword: str,
        serp_results: List[Dict],
        our_domain: str
    ) -> Dict:
        """
        Analyze SERP competition for a keyword.

        Args:
            keyword: The keyword
            serp_results: Top SERP results
            our_domain: User's domain
        """
        top_10 = serp_results[:10]
        serp_text = "\n".join([
            f"{i+1}. {r['domain']} - {r['title']}"
            for i, r in enumerate(top_10)
        ])

        system_prompt = f"""You are an SEO expert analyzing SERP competition for '{keyword}' for the domain {our_domain}.
Analyze the top 10 results and provide:
1. Competitive difficulty assessment
2. Content strategy to outrank competitors
3. Specific gaps in existing content
4. Technical SEO considerations"""

        messages = [{
            "role": "user",
            "content": f"Analyze this SERP for '{keyword}':\n\n{serp_text}\n\nHow can {our_domain} rank better?"
        }]

        response = await self.chat(
            messages=messages,
            system=system_prompt,
            max_tokens=1200
        )

        return {
            "success": True,
            "analysis": response["content"][0]["text"],
            "usage": response.get("usage", {})
        }

    async def generate_content_brief(
        self,
        keyword: str,
        search_volume: int,
        competitor_titles: List[str]
    ) -> Dict:
        """Generate content brief for a keyword"""

        competitors_text = "\n".join([f"- {title}" for title in competitor_titles[:5]])

        system_prompt = f"""You are an SEO content strategist. Create a detailed content brief for ranking for '{keyword}'.
Include:
1. Recommended title (optimized for CTR and SEO)
2. Content structure (H2s, H3s)
3. Key topics to cover
4. Word count recommendation
5. Internal linking opportunities"""

        messages = [{
            "role": "user",
            "content": f"Create a content brief for '{keyword}' (Volume: {search_volume}/month).\n\nCompetitor titles:\n{competitors_text}"
        }]

        response = await self.chat(
            messages=messages,
            system=system_prompt,
            max_tokens=1500
        )

        return {
            "success": True,
            "brief": response["content"][0]["text"],
            "usage": response.get("usage", {})
        }

    async def chat_assistant(
        self,
        user_message: str,
        conversation_history: List[Dict],
        project_context: Optional[Dict] = None
    ) -> Dict:
        """
        Interactive chat with SEO context.

        Args:
            user_message: User's question
            conversation_history: Previous messages
            project_context: Project data for context
        """
        system_prompt = """You are an expert SEO assistant helping users improve their search rankings.
You have access to their keyword data, rankings, and competitor information.

Rules:
- Provide actionable, specific advice
- Reference data when available
- Be encouraging but honest about difficulty
- Suggest next steps
- Never recommend black-hat SEO tactics"""

        if project_context:
            context_text = f"""
Project: {project_context.get('name', 'Unknown')}
Domain: {project_context.get('domain', 'Unknown')}
Keywords tracked: {project_context.get('keyword_count', 0)}
Average position: {project_context.get('avg_position', 'N/A')}
"""
            system_prompt += f"\n\nProject Context:\n{context_text}"

        messages = conversation_history + [{
            "role": "user",
            "content": user_message
        }]

        response = await self.chat(
            messages=messages,
            system=system_prompt,
            max_tokens=1000
        )

        return {
            "success": True,
            "message": response["content"][0]["text"],
            "usage": response.get("usage", {})
        }

    @staticmethod
    def estimate_cost(input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for Claude API call.
        Sonnet 3.5: $3/MTok input, $15/MTok output
        """
        input_cost = (input_tokens / 1_000_000) * 3.0
        output_cost = (output_tokens / 1_000_000) * 15.0
        return input_cost + output_cost
