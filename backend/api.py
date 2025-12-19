from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# 1. FastAPI App Initialize
app = FastAPI(title="AI Agent Backend")

# 2. CORS Settings (Taaki aapka frontend isse connect kar sake)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production mein yahan apni frontend URL dalein
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. FIX: Health Check Routes (Ye Render ko shut down hone se rokega)
@app.get("/")
@app.head("/")
async def health_check():
    return {"status": "active", "message": "AI Agent is running successfully"}

# 4. Aapka AI Logic Route (Example)
@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_query = data.get("query", "")
    
    # Yahan aapka AI model logic aayega
    return {
        "status": "success",
        "response": f"AI Agent processed: {user_query}"
    }

# 5. Server Start Logic
if __name__ == "__main__":
    # Port Render provide karta hai, default 10000
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("backend.api:app", host="0.0.0.0", port=port, reload=True)
