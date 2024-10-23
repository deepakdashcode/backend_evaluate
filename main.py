import datetime
from typing import List, Optional
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, OAuth2PasswordBearer, OAuth2PasswordRequestForm
import httpx
import jwt
from sqlalchemy import select
from sqlmodel import Session, create_engine, SQLModel
from models.user import  Attempted, Token, TokenData, User, Quiz, Created, Answers
from db.database import SessionDep, DATABASE_URL, engine
from passlib.context import CryptContext
from fastapi.testclient import TestClient
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWTError
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt

load_dotenv()

SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI()
client = TestClient(app)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)



security = HTTPBasic()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")



def verify(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def get_user(db, email: str):
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Not found')



def authenticate_user(db: SessionDep, email: str, password: str):
    user = get_user(db, email)
    if not user:
        return None  # Return None if user not found
    if not verify(password, user.password):
        return None  # Return None if password is incorrect
    return user


def create_access_token(data: dict, expires_delta: timedelta | None= None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    print('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
    print(encoded_jwt)
    print('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
    return encoded_jwt

async def get_current_user(db: SessionDep,token: str = Depends(oauth_2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDddd")
        print(payload)
        print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDddd")
        
        email: str = payload.get('sub')
        if email is None:
            raise credential_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credential_exception
    
    print('TOKEN DATA = ', token_data)
    user = get_user(db, email=token_data.email)
    if user is None:
        raise credential_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user

@app.post('/token', response_model=Token)
async def login_for_access_token(db: SessionDep,form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='incorrect credentials')
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub': user.email}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'token_type': "bearer"}

@app.get('/users/me/', response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get('/users/me/items')
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{'item_id': 1, "owner": current_user}]






@app.post("/login")
def login(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    # user = session.query(User).filter(User.username == form_data.username).first()
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    
    if not user or not verify_password(form_data.password, user._mapping['User'].__dict__['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print("SAFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
    print(user)
    print(verify_password(form_data.password, user._mapping['User'].__dict__['password']))
    print("SAFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
    # Create JWT token for authenticated user
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user._mapping['User'].__dict__['id'])},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}



def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return TokenData(email=user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

def get_current_user(token: str = Depends(oauth_2_scheme), db: Session = SessionDep):
    token_data = decode_jwt_token(token)
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user



def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def create_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_tables()

@app.get("/")
def read_root():
    return {"message": "Welcome to Quiz App"}


@app.post('/user/add')
async def create_user(username: str, email: str, password: str, session: SessionDep):
    
    is_present = session.exec(select(User).where(User.email == email))
    if is_present:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User already exists')
    hashed_password = pwd_context.hash(password)
    user = User(username=username, email=email, password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# Function to create a quiz and associate it with a teacher user

@app.get('/quiz/{id}')
def get_quiz(id: int, session: SessionDep):
    quiz = session.exec(select(Quiz).where(Quiz.id == id)).one_or_none()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return quiz._mapping['Quiz'].__dict__['questions']


@app.post("/quiz/add")
async def create_quiz(
    title: str,
    questions: List[str],
    session: SessionDep,
    current_user: User = Depends(get_current_active_user)
):
    user = session.exec(select(User).where(User.id == current_user.id)).one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please register first")

    # Create the quiz
    new_quiz = Quiz(title=title, questions=questions)
    session.add(new_quiz)
    session.commit()
    session.refresh(new_quiz)

    # Create a UserQuizLink entry to associate the quiz with the teacher
    user_quiz_link = Created(user_id=current_user.id, quiz_id=new_quiz.id)
    session.add(user_quiz_link)
    session.commit()
    
    print("NEW QUIZ = ", new_quiz.questions)
    return new_quiz

@app.post("/quiz/attempt")
async def attempt_quiz(quiz_id: int, answers: List[str], session: SessionDep, current_user: User = Depends(get_current_active_user)):
    answer_data = Answers(user_id=current_user.id, quiz_id=quiz_id, answers=answers)
    session.add(answer_data)
    session.commit()
    session.refresh(answer_data)
    
    user_quiz_link = Attempted(user_id=current_user.id, quiz_id=quiz_id)
    session.add(user_quiz_link)
    session.commit()
    session.refresh(user_quiz_link)
    
    print(answer_data.answers)
    return answer_data

@app.get('/quiz/{user_id}/{quiz_id}/')
async def get_quiz_answers(quiz_id: int, user_id: int, session: SessionDep):
    quiz = session.exec(select(Quiz).where(Quiz.id == quiz_id)).one_or_none()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Quiz Not found')
    
    
    ans = session.exec(select(Answers).where(Answers.user_id == user_id and Answers.quiz_id == quiz_id)).one_or_none()
    if not ans:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User Not found')
    questions = quiz._mapping['Quiz'].__dict__['questions']
    answers = ans._mapping['Answers'].__dict__['answers']
    return [questions, answers]
    

@app.get('/quiz/ids')
def get_ids(current_user: User = Depends(get_current_active_user)):
    pass
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)