# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

from app import database, models, auth
from app.database import engine, get_db

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ChatGLM3-6B Cloud Bot")

# ------------------ 模型加载 ------------------
MODEL_NAME = os.getenv("MODEL_NAME")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)

# 尝试使用 GPU，否则 fallback 到 CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
try:
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        load_in_4bit=True,  # 4-bit 量化（显存不足时启用）
        device_map="auto"
    )
except Exception as e:
    print(f"[警告] 无法使用 4-bit 加载，尝试 CPU 推理: {e}")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True
    ).cpu()

# ------------------ Pydantic 模型 ------------------
class ChatRequest(BaseModel):
    prompt: str
    max_length: int = 128
    temperature: float = 0.7

class ConversationOut(BaseModel):
    prompt: str
    response: str
    timestamp: datetime

    class Config:
        from_attributes = True

# ------------------ API 路由 ------------------

@app.post("/register")
def register(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == form_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    hashed = auth.get_password_hash(form_data.password)
    user = models.User(username=form_data.username, hashed_password=hashed)
    db.add(user)
    db.commit()
    return {"msg": "注册成功"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/chat")
def chat(
    request: ChatRequest,
    token: str = Depends(auth.oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username = payload.get("sub")
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user:
            raise HTTPException(status_code=403)
    except JWTError:
        raise HTTPException(status_code=403)

    inputs = tokenizer(request.prompt, return_tensors="pt").to(model.device if hasattr(model, 'device') else 'cpu')
    outputs = model.generate(
        **inputs,
        max_length=request.max_length,
        temperature=request.temperature,
        do_sample=True
    )
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # 保存历史
    conv = models.Conversation(
        user_id=user.id,
        prompt=request.prompt,
        response=response_text
    )
    db.add(conv)
    db.commit()

    return {"response": response_text}

@app.get("/history", response_model=List[ConversationOut])
def get_history(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username = payload.get("sub")
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user:
            raise HTTPException(status_code=403)
    except JWTError:
        raise HTTPException(status_code=403)

    history = db.query(models.Conversation).filter(models.Conversation.user_id == user.id).order_by(models.Conversation.timestamp.desc()).limit(10).all()
    return history
