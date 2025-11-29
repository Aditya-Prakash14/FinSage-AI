"""
Authentication routes for user registration, login, and profile management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import hashlib
import secrets
import jwt

from database.mongo_config import mongodb_manager

router = APIRouter()
security = HTTPBearer()

# Configuration
SECRET_KEY = "your-secret-key-here-change-in-production"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Pydantic Models
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfileUpdate(BaseModel):
    userId: str
    onboarding_completed: Optional[bool] = None
    work_type: Optional[str] = None
    income_stability: Optional[str] = None
    monthly_income: Optional[int] = None
    monthly_expenses: Optional[int] = None
    financial_goals: Optional[list] = None
    biggest_challenge: Optional[str] = None
    current_savings: Optional[str] = None
    budget_experience: Optional[str] = None
    risk_tolerance: Optional[str] = None
    notification_preferences: Optional[str] = None

# Helper Functions
def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == hashed_password

def create_access_token(data: dict) -> str:
    """Create a JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token from Authorization header"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# Routes
@router.post("/register", tags=["Authentication"])
async def register_user(user_data: UserRegister):
    """
    Register a new user account
    
    Creates a new user with hashed password and returns user info with JWT token.
    """
    try:
        # Get users collection
        db = mongodb_manager.get_database()
        if not db:
            # Fallback mode - create in-memory user (for demo)
            user_id = f"user_{secrets.token_urlsafe(8)}"
            user = {
                "id": user_id,
                "name": user_data.name,
                "email": user_data.email,
                "created_at": datetime.utcnow().isoformat(),
                "onboarding_completed": False
            }
            token = create_access_token({"sub": user_id, "email": user_data.email})
            return {
                "success": True,
                "user": user,
                "token": token,
                "message": "Account created successfully (demo mode)"
            }
        
        users_collection = db.users
        
        # Check if user already exists
        existing_user = users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create user document
        user_id = f"user_{secrets.token_urlsafe(8)}"
        user_doc = {
            "id": user_id,
            "name": user_data.name,
            "email": user_data.email,
            "password_hash": hashed_password,
            "created_at": datetime.utcnow(),
            "onboarding_completed": False,
            "profile": {}
        }
        
        # Insert user
        users_collection.insert_one(user_doc)
        
        # Create JWT token
        token = create_access_token({"sub": user_id, "email": user_data.email})
        
        # Return user info (without password hash)
        user_response = {
            "id": user_id,
            "name": user_data.name,
            "email": user_data.email,
            "created_at": user_doc["created_at"].isoformat(),
            "onboarding_completed": False
        }
        
        return {
            "success": True,
            "user": user_response,
            "token": token,
            "message": "Account created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", tags=["Authentication"])
async def login_user(credentials: UserLogin):
    """
    Login with email and password
    
    Validates credentials and returns user info with JWT token.
    """
    try:
        db = mongodb_manager.get_database()
        if not db:
            # Demo mode - accept any login
            user_id = f"demo_user_{secrets.token_urlsafe(8)}"
            user = {
                "id": user_id,
                "name": "Demo User",
                "email": credentials.email,
                "onboarding_completed": False
            }
            token = create_access_token({"sub": user_id, "email": credentials.email})
            return {
                "success": True,
                "user": user,
                "token": token,
                "message": "Logged in successfully (demo mode)"
            }
        
        users_collection = db.users
        
        # Find user by email
        user = users_collection.find_one({"email": credentials.email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create JWT token
        token = create_access_token({"sub": user["id"], "email": user["email"]})
        
        # Return user info (without password hash)
        user_response = {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "created_at": user["created_at"].isoformat(),
            "onboarding_completed": user.get("onboarding_completed", False),
            "profile": user.get("profile", {})
        }
        
        return {
            "success": True,
            "user": user_response,
            "token": token,
            "message": "Logged in successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.put("/profile", tags=["Authentication"])
async def update_profile(
    profile_data: UserProfileUpdate,
    user_id: str = Depends(verify_token)
):
    """
    Update user profile with onboarding data
    
    Stores financial preferences and onboarding questionnaire responses.
    """
    try:
        db = mongodb_manager.get_database()
        if not db:
            # Demo mode - return success
            return {
                "success": True,
                "user": {
                    "id": user_id,
                    "onboarding_completed": True,
                    "profile": profile_data.dict(exclude_unset=True)
                },
                "message": "Profile updated successfully (demo mode)"
            }
        
        users_collection = db.users
        
        # Build update document
        update_data = profile_data.dict(exclude_unset=True, exclude={"userId"})
        
        # Update user profile
        result = users_collection.update_one(
            {"id": profile_data.userId},
            {"$set": {
                "profile": update_data,
                "onboarding_completed": update_data.get("onboarding_completed", False),
                "updated_at": datetime.utcnow()
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get updated user
        updated_user = users_collection.find_one({"id": profile_data.userId})
        
        user_response = {
            "id": updated_user["id"],
            "name": updated_user["name"],
            "email": updated_user["email"],
            "onboarding_completed": updated_user.get("onboarding_completed", False),
            "profile": updated_user.get("profile", {})
        }
        
        return {
            "success": True,
            "user": user_response,
            "message": "Profile updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile update failed: {str(e)}"
        )

@router.get("/me", tags=["Authentication"])
async def get_current_user(user_id: str = Depends(verify_token)):
    """
    Get current user information
    
    Returns user profile based on JWT token.
    """
    try:
        db = mongodb_manager.get_database()
        if not db:
            return {
                "success": True,
                "user": {
                    "id": user_id,
                    "name": "Demo User",
                    "email": "demo@finsage.ai",
                    "onboarding_completed": False
                }
            }
        
        users_collection = db.users
        user = users_collection.find_one({"id": user_id})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_response = {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "onboarding_completed": user.get("onboarding_completed", False),
            "profile": user.get("profile", {})
        }
        
        return {
            "success": True,
            "user": user_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )
