from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel, Session
import jwt

class Created(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    quiz_id: Optional[int] = Field(default=None, foreign_key="quiz.id", primary_key=True)

class Attempted(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    quiz_id: Optional[int] = Field(default=None, foreign_key="quiz.id", primary_key=True)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    password: str
    
    created_quizzes: List["Quiz"] = Relationship(
        back_populates="created_user",
        link_model=Created
    )
    
    attempted_quizzes: List["Quiz"] = Relationship(
        back_populates="attempted_users",
        link_model=Attempted
    )


class Quiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    questions: List[str] = Field(sa_column=Column(JSON))
    
    created_user: List[User] = Relationship(
        back_populates="created_quizzes",
        link_model=Created
    )
    
    attempted_users: List[User] = Relationship(
        back_populates="attempted_quizzes",
        link_model=Attempted
    )


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    
    
class Answers(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    quiz_id: Optional[int] = Field(default=None, foreign_key="quiz.id", primary_key=True)
    answers: List[str] = Field(sa_column=Column(JSON))