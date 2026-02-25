from fastapi import FastAPI, HTTPException, Depends, Form, status
from typing import List 
from pydantic import BaseModel
from typing import Optional
import httpx

from jwt_utils import create_access_token
from auth import jwt_auth

app = FastAPI(title="API Gateway", version="1.0.0")

# Microservices
SERVICES = {
    "student": "http://localhost:8001",
    "course": "http://localhost:8002"
}

# ---------------------------
# Authentication
# ---------------------------
USERS_DB = {
    "admin123": "12345"
}

@app.post("/auth/login")
def login(username: str = Form(...), password: str = Form(...)):
    # Check credentials
    if username not in USERS_DB or USERS_DB[username] != password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Create JWT token
    token = create_access_token({"sub": username})
    return {
        "access_token": token,
        "token_type": "Bearer"
    }

# ---------------------------
# Request forwarding utility
# ---------------------------
async def forward_request(service: str, path: str, method: str, json_data=None):
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")

    url = f"{SERVICES[service]}{path}"

    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, json=json_data)
        if response.status_code >= 400:
            # Forward error from microservice
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json() if response.text else None

# ---------------------------
# Pydantic models
# ---------------------------
class StudentCreate(BaseModel):
    name: str
    age: int
    email: str
    course: str

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None
    course: Optional[str] = None

class CourseCreate(BaseModel):
    name: str
    description: str
    credits: int

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    credits: Optional[int] = None

# ---------------------------
# Root
# ---------------------------
@app.get("/")
def read_root():
    return {"message": "API Gateway is running"}

# ---------------------------
# Student routes
# ---------------------------
@app.get("/gateway/students", dependencies=[Depends(jwt_auth)])
async def get_all_students():
    return await forward_request("student", "/api/students", "GET")

@app.get("/gateway/students/{student_id}", dependencies=[Depends(jwt_auth)])
async def get_student(student_id: int):
    return await forward_request("student", f"/api/students/{student_id}", "GET")

@app.post("/gateway/students", dependencies=[Depends(jwt_auth)])
async def create_student(student: StudentCreate):
    return await forward_request("student", "/api/students", "POST", json_data=student.dict())

@app.put("/gateway/students/{student_id}", dependencies=[Depends(jwt_auth)])
async def update_student(student_id: int, student: StudentUpdate):
    return await forward_request(
        "student",
        f"/api/students/{student_id}",
        "PUT",
        json_data=student.dict(exclude_unset=True)
    )

@app.delete("/gateway/students/{student_id}", dependencies=[Depends(jwt_auth)])
async def delete_student(student_id: int):
    return await forward_request("student", f"/api/students/{student_id}", "DELETE")

# ---------------------------
# Course routes
# ---------------------------
@app.get("/gateway/courses", dependencies=[Depends(jwt_auth)])
async def get_all_courses():
    return await forward_request("course", "/api/courses", "GET")

@app.get("/gateway/courses/{course_id}", dependencies=[Depends(jwt_auth)])
async def get_course(course_id: int):
    return await forward_request("course", f"/api/courses/{course_id}", "GET")

@app.post("/gateway/courses", dependencies=[Depends(jwt_auth)])
async def create_course(course: CourseCreate):
    return await forward_request("course", "/api/courses", "POST", json_data=course.dict())

@app.put("/gateway/courses/{course_id}", dependencies=[Depends(jwt_auth)])
async def update_course(course_id: int, course: CourseUpdate):
    return await forward_request(
        "course",
        f"/api/courses/{course_id}",
        "PUT",
        json_data=course.dict(exclude_unset=True)
    )

@app.delete("/gateway/courses/{course_id}", dependencies=[Depends(jwt_auth)])
async def delete_course(course_id: int):
    return await forward_request("course", f"/api/courses/{course_id}", "DELETE")
