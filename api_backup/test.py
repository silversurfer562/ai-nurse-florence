from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create a minimal test app
app = FastAPI(title="Test App", version="1.0.0")

@app.get("/")
@app.get("/test")
async def test_endpoint():
    return JSONResponse({
        "status": "success",
        "message": "Test deployment working",
        "service": "ai-nurse-florence-test"
    })

# Export for Vercel
handler = app
