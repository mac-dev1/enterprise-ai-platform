from fastapi import Depends, Header, HTTPException
from jose import jwt
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User
from app.services.auth_service import SECRET_KEY, ALGORITHM


def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user