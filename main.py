import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from passlib.context import CryptContext

from database import db, create_document, get_documents

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Request models
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

@app.get("/")
def read_root():
    return {"message": "SaaS Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# Auth Endpoints (simple hashed password, sessionless)
@app.post("/auth/register")
def register_user(payload: RegisterRequest):
    # Check existing
    existing = db["saasuser"].find_one({"email": payload.email}) if db else None
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    password_hash = pwd_context.hash(payload.password)
    user_doc = {
        "name": payload.name,
        "email": payload.email,
        "password_hash": password_hash,
        "plan": "free",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    result = db["saasuser"].insert_one(user_doc)
    return {"id": str(result.inserted_id), "email": payload.email, "name": payload.name}

@app.post("/auth/login")
def login_user(payload: LoginRequest):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    user = db["saasuser"].find_one({"email": payload.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not pwd_context.verify(payload.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"email": user["email"], "name": user["name"], "plan": user.get("plan", "free")}

# Public blog endpoints
@app.get("/blog", response_model=List[dict])
def list_blog_posts(limit: int = 10):
    if db is None:
        return []
    posts = db["blogpost"].find({}).sort("published_at", -1).limit(limit)
    res = []
    for p in posts:
        p["_id"] = str(p["_id"])  # convert ObjectId
        res.append(p)
    return res

# Contact form endpoint
@app.post("/contact")
def submit_contact(payload: ContactRequest):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    doc = {
        **payload.model_dump(),
        "created_at": datetime.utcnow()
    }
    result = db["contactmessage"].insert_one(doc)
    return {"success": True, "id": str(result.inserted_id)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
