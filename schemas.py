"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# SaaS App Schemas

class SaaSUser(BaseModel):
    """
    Users collection schema
    Collection name: "saasuser"
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    password_hash: str = Field(..., description="BCrypt password hash")
    plan: str = Field("free", description="Subscription plan: free, pro, business")
    is_active: bool = Field(True, description="Whether user is active")

class BlogPost(BaseModel):
    """
    Blog posts collection schema
    Collection name: "blogpost"
    """
    title: str = Field(..., description="Post title")
    slug: str = Field(..., description="URL-friendly slug")
    excerpt: str = Field(..., description="Short summary")
    content: str = Field(..., description="Full content (markdown)")
    author: str = Field(..., description="Author name")
    tags: List[str] = Field(default_factory=list, description="Tags")
    published_at: Optional[datetime] = Field(None, description="Publish date")

class ContactMessage(BaseModel):
    """
    Contact form submissions collection schema
    Collection name: "contactmessage"
    """
    name: str = Field(..., description="Sender name")
    email: EmailStr = Field(..., description="Sender email")
    subject: str = Field(..., description="Subject")
    message: str = Field(..., description="Message body")

# Example schemas kept for reference
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
