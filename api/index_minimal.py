"""
Minimal Vercel Python test - no external dependencies
"""

def handler(event, context):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": '{"message": "Hello from Vercel Python", "status": "working"}'
    }
