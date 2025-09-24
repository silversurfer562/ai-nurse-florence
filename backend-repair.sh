#!/bin/bash
echo "=== AI Nurse Florence Backend Repair ==="

# Fix PubMed JSON serialization error
echo "Step 1: Fixing PubMed JSON serialization..."
if [ -f "routers/pubmed.py" ]; then
    echo "Creating backup of pubmed.py..."
    cp routers/pubmed.py routers/pubmed.py.backup
    
    # Use Python to fix the serialization issue
    python3 << 'PYTHON_SCRIPT'
# Read the current pubmed.py file
with open('routers/pubmed.py', 'r') as f:
    content = f.read()

# Find and replace the problematic line
if 'return create_success_response(paginated_data)' in content:
    print("Found problematic line - applying fix...")
    
    # Replace with fixed version
    fixed_content = content.replace(
        'return create_success_response(paginated_data)',
        '''# Fixed JSON serialization issue for Page objects
        try:
            # Handle Page object by converting to dict
            if hasattr(paginated_data, 'items'):
                response_data = {
                    "items": paginated_data.items,
                    "total": getattr(paginated_data, 'total', len(paginated_data.items) if hasattr(paginated_data, 'items') else 0),
                    "page": getattr(paginated_data, 'page', page),
                    "size": getattr(paginated_data, 'size', size),
                    "links": {
                        "self": f"{request.base_url}api/v1/pubmed/search?page={page}&size={size}",
                        "first": f"{request.base_url}api/v1/pubmed/search?page=1&size={size}",
                    }
                }
                # Add next/prev links if available
                if hasattr(paginated_data, 'has_next') and paginated_data.has_next:
                    response_data["links"]["next"] = f"{request.base_url}api/v1/pubmed/search?page={page + 1}&size={size}"
                if hasattr(paginated_data, 'has_prev') and paginated_data.has_prev:
                    response_data["links"]["prev"] = f"{request.base_url}api/v1/pubmed/search?page={page - 1}&size={size}"
            else:
                # Handle direct dict/list objects
                response_data = paginated_data
            
            return create_success_response(response_data)
        except Exception as e:
            print(f"Error serializing PubMed response: {e}")
            return create_error_response("Failed to serialize PubMed response", 500)'''
    )
    
    # Write the fixed content back
    with open('routers/pubmed.py', 'w') as f:
        f.write(fixed_content)
    
    print("PubMed serialization fix applied successfully!")
else:
    print("PubMed router appears to already be fixed or uses different pattern")
PYTHON_SCRIPT

else
    echo "Warning: routers/pubmed.py not found!"
fi

# Fix OpenAI client missing chat function
echo ""
echo "Step 2: Checking OpenAI client for missing chat function..."
if [ -f "services/openai_client.py" ]; then
    if ! grep -q "async def chat" services/openai_client.py; then
        echo "Adding missing chat function..."
        cat >> services/openai_client.py << 'OPENAI_ADDITION'

# Added for education router compatibility
async def chat(messages, model="gpt-4o-mini", **kwargs):
    """
    Chat completion wrapper for education router
    Compatible with OpenAI API v1.0+
    """
    if not client:
        raise Exception("OpenAI client not configured - check OPENAI_API_KEY")
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI chat error: {e}")
        raise Exception(f"OpenAI chat failed: {str(e)}")
OPENAI_ADDITION
        echo "Chat function added to OpenAI client"
    else
        echo "Chat function already exists in OpenAI client"
    fi
else
    echo "Warning: services/openai_client.py not found!"
fi

echo ""
echo "=== Backend Repair Complete ==="
echo "Next: Test locally, then deploy to Railway"
