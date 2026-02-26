from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr, validator
import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import uuid
import mariadb
from passlib.context import CryptContext
import re
import logging

# Set up logger
logger = logging.getLogger(__name__)

# Create a router instance
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={401: {"description": "Unauthorized"}},
)

# Password context for hashing and verifying
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours (increased from 30 minutes)
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Database connection from environment variables
MARIADB_HOST = os.getenv("MARIADB_HOST", "mariadb")
MARIADB_DATABASE = os.getenv("MARIADB_DATABASE", "regulaite")
MARIADB_USER = os.getenv("MARIADB_USER", "regulaite_user")
MARIADB_PASSWORD = os.getenv("MARIADB_PASSWORD", "SecureP@ssw0rd!")


# Password validation function
def validate_password(password: str) -> bool:
    """
    Validate password complexity requirements:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 special character
    """
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]', password):
        return False
    return True


# Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    company: Optional[str] = None
    username: Optional[str] = None
    
    @validator('password')
    def password_must_meet_complexity(cls, v):
        if not validate_password(v):
            raise ValueError('Password must be at least 8 characters long, contain at least one uppercase letter and one special character')
        return v
        
    @validator('username')
    def username_must_be_valid(cls, v):
        if v is None:
            return v
        if not re.match(r'^[a-zA-Z0-9_]{3,30}$', v):
            raise ValueError('Username must be 3-30 characters and contain only letters, numbers, and underscores')
        return v


class UserResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    company: Optional[str] = None
    username: Optional[str] = None
    created_at: datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None


# Helper functions
def get_db_connection():
    """Get a connection to MariaDB"""
    try:
        conn = mariadb.connect(
            host=MARIADB_HOST,
            user=MARIADB_USER,
            password=MARIADB_PASSWORD,
            database=MARIADB_DATABASE,
            port=3306,
        )
        return conn
    except mariadb.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection error: {e}"
        )


def create_auth_tables(conn):
    """Create authentication tables if they don't exist"""
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id VARCHAR(255) PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(255) NOT NULL,
        company VARCHAR(255),
        username VARCHAR(255) UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        last_login TIMESTAMP NULL,
        settings JSON
    )
    """)
    
    # Create refresh tokens table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS refresh_tokens (
        token_id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        refresh_token VARCHAR(255) NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    cursor.close()


def verify_password(plain_password, hashed_password):
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: str):
    """Create a refresh token and store it in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Generate a refresh token
    token_id = str(uuid.uuid4())
    refresh_token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Store in database
    cursor.execute(
        "INSERT INTO refresh_tokens (token_id, user_id, refresh_token, expires_at) VALUES (?, ?, ?, ?)",
        (token_id, user_id, refresh_token, expires_at)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    return refresh_token


def get_user_by_email(email: str):
    """Get user by email"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return user


def get_user_by_id(user_id: str):
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = get_user_by_id(token_data.user_id)
    if user is None:
        raise credentials_exception
    
    return user


# Routes
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    """Register a new user"""
    logger.info(f"Registration attempt for email: {user.email}")
    
    conn = None
    try:
        # Get database connection
        logger.info("Attempting to get database connection...")
        conn = get_db_connection()
        logger.info("Database connection established successfully")
        
        # Ensure tables exist
        logger.info("Creating auth tables if they don't exist...")
        create_auth_tables(conn)
        logger.info("Auth tables verified/created successfully")
        
        cursor = conn.cursor()
        
        # Check if email already exists
        logger.info(f"Checking if email {user.email} already exists...")
        existing_user = get_user_by_email(user.email)
        if existing_user:
            logger.warning(f"Registration failed: Email {user.email} already registered")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        logger.info("Email check passed - email is available")
        
        # Create new user
        user_id = str(uuid.uuid4())
        logger.info(f"Generated user ID: {user_id}")
        
        password_hash = get_password_hash(user.password)
        logger.info("Password hashed successfully")
        
        # Insert user into database
        logger.info("Inserting user into database...")
        cursor.execute(
            "INSERT INTO users (user_id, email, password_hash, full_name, company, username) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, user.email, password_hash, user.full_name, user.company, user.username)
        )
        conn.commit()
        logger.info(f"User {user.email} registered successfully with ID: {user_id}")
        
        # Return user data without password
        user_response = UserResponse(
            user_id=user_id,
            email=user.email,
            full_name=user.full_name,
            company=user.company,
            username=user.username,
            created_at=datetime.now()
        )
        logger.info(f"Returning successful registration response for user: {user.email}")
        return user_response
        
    except HTTPException as he:
        # Re-raise HTTP exceptions (like email already exists)
        logger.error(f"HTTP Exception during registration: {he.detail}")
        if conn:
            conn.rollback()
        raise he
    except mariadb.Error as me:
        logger.error(f"MariaDB error during registration: {str(me)}")
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(me)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}", exc_info=True)
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token"""
    # Get user by email
    user = get_user_by_email(form_data.username)  # username field contains email
    
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["user_id"]},
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(user["user_id"])
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get token from database
    cursor.execute(
        "SELECT * FROM refresh_tokens WHERE refresh_token = ? AND expires_at > NOW()",
        (refresh_token,)
    )
    token_data = cursor.fetchone()
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": token_data["user_id"]},
        expires_delta=access_token_expires
    )
    
    # Create new refresh token
    new_refresh_token = create_refresh_token(token_data["user_id"])
    
    # Delete old refresh token
    cursor.execute(
        "DELETE FROM refresh_tokens WHERE refresh_token = ?",
        (refresh_token,)
    )
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.post("/logout")
async def logout(refresh_token: str):
    """Logout user by invalidating refresh token"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Delete refresh token
    cursor.execute(
        "DELETE FROM refresh_tokens WHERE refresh_token = ?",
        (refresh_token,)
    )
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        user_id=current_user["user_id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        company=current_user["company"],
        username=current_user.get("username"),
        created_at=current_user["created_at"]
    ) 