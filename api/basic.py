def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': '{"status": "success", "message": "Basic Python function working", "service": "ai-nurse-florence-basic"}'
    }
