from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import logging
from datetime import datetime, timedelta

from start_files.config import SECRET_KEY, ALGORITHM
from start_files.auth.ldap_auth import authenticate_ldap
from start_files.models.users import User, get_db
from start_files.models.inventory import sessionLocal, Inventory, InventoryHistory

# -------------------------
# Router setup
# -------------------------
router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# -------------------------
# Auth helpers
# -------------------------
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_token_from_request(request: Request) -> str | None:
    """Get JWT from cookie OR Authorization header"""
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        return auth.split(" ", 1)[1]

    return request.cookies.get("access_token")

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    token = get_token_from_request(request)

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_roles(*allowed_roles: str):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied")
        return user
    return role_checker

# -------------------------
# Auth routes
# -------------------------
class LoginRequest(BaseModel):
    username: str
    password: str
    remember_me: bool = False

@router.post("/auth/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    if not authenticate_ldap(data.username, data.password):
        return JSONResponse({"error": "Invalid credentials"}, status_code=401)

    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        role = "admin" if db.query(User).count() == 0 else "user"
        user = User(username=data.username, role=role)
        user.set_password(data.password)
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": user.username, "role": user.role})

    response = JSONResponse({
        "access_token": token,
        "token_type": "bearer",
        "role": user.role
    })

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,   # TRUE only with HTTPS
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return response

# -------------------------
# UI routes
# -------------------------
@router.get("/", response_class=HTMLResponse)
async def root_redirect():
    return RedirectResponse(url="/login")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/inventory", response_class=HTMLResponse)
async def inventory_page(
    request: Request,
    user: User = Depends(get_current_user)
):
    templates = request.app.state.templates
    return templates.TemplateResponse(
        "inventory.html",
        {"request": request, "user": user}
    )

# -------------------------
# Inventory API
# -------------------------
class InventoryUpdate(BaseModel):
    used: int

@router.get("/api/inventory")
def get_inventory(user: User = Depends(require_roles("admin", "user"))):
    db = sessionLocal()
    try:
        items = db.query(Inventory).all()
        return [{"id": i.id, "name": i.name, "used": i.used} for i in items]
    finally:
        db.close()

@router.post("/api/inventory/{item_id}")
def update_inventory(
    item_id: int,
    data: InventoryUpdate,
    user: User = Depends(require_roles("admin", "user"))
):
    db = sessionLocal()
    try:
        item = db.query(Inventory).filter(Inventory.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        item.used = data.used
        db.commit()
        db.refresh(item)
        return {"success": True}
    finally:
        db.close()

# -------------------------
# History API
# -------------------------
class HistoryCreate(BaseModel):
    item: str
    change: int
    timestamp: str

@router.get("/api/history")
def get_history(user: User = Depends(require_roles("admin", "user"))):
    db = sessionLocal()
    try:
        history = db.query(InventoryHistory).order_by(
            InventoryHistory.id.desc()
        ).all()
        return [
            {"id": h.id, "item": h.item, "change": h.change, "timestamp": h.timestamp}
            for h in history
        ]
    finally:
        db.close()

@router.post("/api/history")
def add_history(
    data: HistoryCreate,
    user: User = Depends(require_roles("admin", "user"))
):
    db = sessionLocal()
    try:
        entry = InventoryHistory(
            item=data.item,
            change=data.change,
            timestamp=data.timestamp
        )
        db.add(entry)
        db.commit()
        return {"success": True}
    finally:
        db.close()

@router.delete("/api/history/{history_id}")
def delete_history(
    history_id: int,
    user: User = Depends(require_roles("admin"))
):
    db = sessionLocal()
    try:
        entry = db.query(InventoryHistory).filter(
            InventoryHistory.id == history_id
        ).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        db.delete(entry)
        db.commit()
        return {"success": True}
    finally:
        db.close()
