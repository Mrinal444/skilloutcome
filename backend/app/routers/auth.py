from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.trainee import Trainee
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.schemas.common import APIResponse
from app.auth.jwt import hash_password, verify_password, create_access_token
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=APIResponse)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """
    POST /api/v1/auth/register
    Creates a new user account. Public access.
    """
    # Check if email already exists
    email = str(payload.email).strip().lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Validate role
    try:
        role = UserRole(payload.role.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {[r.value for r in UserRole]}",
        )

    user = User(
        name=payload.name,
        email=email,
        password_hash=hash_password(payload.password),
        role=role,
    )
    db.add(user)
    if role == UserRole.TRAINEE:
        db.flush()
        db.add(Trainee(user_id=user.id, education="", location="", experience=0))
    db.commit()
    db.refresh(user)

    return APIResponse(success=True, message="User registered successfully")


@router.post("/login", response_model=APIResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    email = str(payload.email).strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )

    return APIResponse(
        success=True,
        message="Login successful",
        data=TokenResponse(
            access_token=access_token,
            role=user.role.value,
        ).model_dump(),
    )


@router.get("/me", response_model=APIResponse)
def current_user(current_user: User = Depends(get_current_user)):
    """Return the authenticated user for frontend session restoration."""
    return APIResponse(
        success=True,
        message="Current user loaded",
        data=UserResponse.model_validate(current_user).model_dump(),
    )
