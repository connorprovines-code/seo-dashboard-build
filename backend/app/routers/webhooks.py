"""
Webhook router for external integrations like n8n for email outreach.
Allows triggering outreach campaigns via HTTP webhooks.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from pydantic import BaseModel, HttpUrl
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


class OutreachWebhookPayload(BaseModel):
    """Payload to send to external webhook for email outreach"""
    campaign_name: str
    target_domain: str
    target_email: str | None = None
    context: Dict[str, Any]  # SEO data, backlink opportunities, etc.
    template_vars: Dict[str, Any] | None = None


class TriggerOutreachRequest(BaseModel):
    """Request to trigger outreach campaign"""
    webhook_url: HttpUrl
    competitor_ids: List[UUID] | None = None
    custom_targets: List[Dict[str, str]] | None = None
    campaign_name: str = "Link Building Outreach"
    include_backlink_data: bool = True


@router.post("/outreach/trigger")
async def trigger_outreach_campaign(
    project_id: UUID,
    request: TriggerOutreachRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger outreach campaign by sending data to external webhook (e.g., n8n).

    This endpoint prepares SEO context data and sends it to your n8n webhook,
    which can then handle email sending, follow-ups, tracking, etc.

    **Example n8n Workflow:**
    1. Webhook trigger receives this payload
    2. Enrich with company data (Clearbit, etc.)
    3. Generate personalized email (AI or template)
    4. Send via SMTP/Gmail/SendGrid
    5. Track opens/replies
    6. Schedule follow-ups

    **Payload Structure:**
    ```json
    {
      "campaign_name": "Link Building Q4 2024",
      "targets": [
        {
          "target_domain": "competitor.com",
          "target_email": "editor@competitor.com",
          "context": {
            "your_domain": "yourdomain.com",
            "backlink_opportunity": true,
            "shared_keywords": 15,
            "their_domain_rank": 42
          }
        }
      ]
    }
    ```
    """
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    targets = []

    # Build targets from competitor list
    if request.competitor_ids:
        competitors = db.query(CompetitorDomain).filter(
            CompetitorDomain.id.in_(request.competitor_ids),
            CompetitorDomain.project_id == project_id
        ).all()

        for competitor in competitors:
            context = {
                "your_domain": project.domain,
                "target_domain": competitor.domain,
                "notes": competitor.notes,
            }

            # Optionally include backlink data
            if request.include_backlink_data:
                # You could fetch backlink data here from DataForSEO
                # For now, just placeholder
                context["backlink_opportunity"] = True

            targets.append({
                "target_domain": competitor.domain,
                "target_email": None,  # n8n can enrich this
                "context": context,
                "template_vars": {
                    "your_site": project.name,
                    "their_site": competitor.domain,
                }
            })

    # Add custom targets
    if request.custom_targets:
        for custom in request.custom_targets:
            targets.append({
                "target_domain": custom.get("domain"),
                "target_email": custom.get("email"),
                "context": {
                    "your_domain": project.domain,
                    "custom_data": custom
                },
                "template_vars": custom.get("template_vars", {})
            })

    # Prepare webhook payload
    webhook_payload = {
        "campaign_name": request.campaign_name,
        "project": {
            "id": str(project.id),
            "name": project.name,
            "domain": project.domain,
        },
        "targets": targets,
        "total_targets": len(targets),
        "triggered_by": current_user.email,
    }

    # Send to webhook
    import httpx
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                str(request.webhook_url),
                json=webhook_payload,
                timeout=30.0
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Webhook request failed: {str(e)}"
            )

    return {
        "success": True,
        "message": f"Outreach campaign triggered for {len(targets)} targets",
        "targets_sent": len(targets),
        "webhook_status": response.status_code,
    }


@router.post("/incoming/{webhook_id}")
async def incoming_webhook(
    webhook_id: str,
    payload: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Receive incoming webhooks from external services.

    Use this for:
    - Email reply notifications from n8n
    - Link placement confirmations
    - Outreach campaign status updates

    **Example: Email Reply Notification**
    ```json
    {
      "event": "email_reply",
      "campaign_name": "Link Building Q4",
      "from_domain": "competitor.com",
      "reply_text": "Sure, we'd love to collaborate!",
      "timestamp": "2024-01-15T10:30:00Z"
    }
    ```

    You can store this data or trigger follow-up actions.
    """
    # Log the webhook (you could store in a webhooks table)
    # For now, just return success

    return {
        "success": True,
        "webhook_id": webhook_id,
        "received": True,
        "message": "Webhook received successfully"
    }


@router.get("/test")
async def test_webhook():
    """Test endpoint to verify webhooks router is working"""
    return {
        "status": "ok",
        "message": "Webhooks router is working",
        "endpoints": [
            "POST /api/webhooks/outreach/trigger - Trigger outreach to n8n",
            "POST /api/webhooks/incoming/{webhook_id} - Receive incoming webhooks"
        ]
    }
