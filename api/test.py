"""Minimal test endpoint for Vercel"""

def handler(request):
    """Simple test handler"""
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": '{"status": "ok", "message": "Python is working on Vercel"}'
    }
