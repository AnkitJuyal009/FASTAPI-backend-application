
import json
from os import replace
import stat
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, EmailStr, Field, computed_field, field_validator
from typing import List, Literal


# created an object of fast api
app = FastAPI()

"""
GET METHOD
"""

# decorator
@app.get('/')
def greet():
    return {"Hello"}

#helper function
def load_data():
    with open("student.json", "r") as file:
        return json.load(file)

def save_data(data):
    with open("student.json", "w") as file:
        json.dump(data, file, indent=4)  # indent - keeps the file readable


@app.get('/student')
def student():
    return load_data()


# Path - ... is manadate, the Path tells us about additiona;l validation and metadata
# in this example "..." is not required as by default Path parameters are madatory
@app.get('/student/{student_id}')
def get_id(student_id:str = Path(...,description="The ID of the student", examples=["1","2"])):
    data = load_data()
    students = data["students"]

    if student_id not in students:
        raise HTTPException (
            status_code=404,
            detail=f"Student with ID {student_id} not found"
        )
    return students[student_id]

# Query parameters - used to filter out, starts with ?
# data = load_data() --> populates data in json where

@app.get('/filter')
def filter_student(subject:str = Query(default=None, description="Show only students according to subject", examples=["Python"])):
    data = load_data()
    students = data["students"]

    if subject is None:
        return students

    filtered = {}
    for student_id, info in students.items():
        # print(info)
        if subject in info["subjects"]:
            filtered[student_id] = info

    return filtered


# sort through Query parameter

SORT_FIELDS = ["gpa", "age", "name"]
SORT_ORDER = ["asc", "desc"]

@app.get('/sort')
def sort_student(sort_by:str, order:str):
    data = load_data()
    students = data["students"]

    if sort_by not in SORT_FIELDS:
        raise HTTPException(
            status_code=404,
            detail=f"Invalid {sort_by} field, please choose form {SORT_FIELDS}"
        )

    if order not in SORT_ORDER:
        raise HTTPException(
            status_code=404,
            detail=f"Invalid {order} field, please choose form {SORT_ORDER}"
        )

    # Main logic - first turn dict to list , and put ID inside each element
    student = []
    # created a list and added id into the list
    for student_id, info in students.items():
        info["id"] = student_id
        student.append(info)

    
    sorted_students = sorted(
        student,
        key= lambda s: s[sort_by],
        reverse=(order == "desc")
    )
    return sorted_students


#Pagination - required Page and limit
# start = (page-1) *limit
# end = start + limit

@app.get('/paginate')
def paginate_students(
    page:int = Query(default=1, ge=1, description="page that you want"), 
    limit:int = Query(default=2, ge=1, le=100, description="how many students in a page")):
    data = load_data()
    students = data["students"]

    
    # Main logic - first turn dict to list , and put ID inside each element
    student = []
    # created a list and added id into the list
    for student_id, info in students.items():
        info["id"] = student_id
        student.append(info)

    total_student = len(student)


    # edge case
    student_in_provided_limit = page * limit

    if student_in_provided_limit > total_student:
        raise HTTPException(
            status_code=404,
            detail=f"there is no data left to show"
        )
    
    start = (page - 1) * limit
    end = start + limit
    page_student = student[start:end]
    
    return {
        "page": page,
        "limit": limit,
        "total_student" : total_student,
        "page_student": page_student
    }


"""
REQUEST Body

"""

GENDER_OPTIONS = ["male", "female", "others"]

class Address(BaseModel):
    city:str 
    state:str 
    country:str 
    pincode:str 


class Student(BaseModel):
    id : str = Field(..., examples=["1"])
    name : str = Field(..., min_length=2, max_length=50)
    age : int = Field(..., gt=0, lt=100)
    email : EmailStr
    gender: Literal["male", "female", "others"]
    course : str | None = None
    year : int | None = Field(default=None, gt=0, lt=5)
    gpa : float | None = Field(default=None, gt=0.0, le=10.0)
    subjects : List[str] | None = Field(default=None)
    address : Address | None = None

    @field_validator("name")
    @classmethod
    def check_name(clas, value):
        if not value.replace(" ", "").isalpha():
            raise ValueError("name must contain only letters and namespaces") 
        return value.title()

    @computed_field
    @property
    def grade(self) -> str | None:
        if self.gpa is None:
            return None
        if self.gpa >= 9.0:
            return "A+"
        elif self.gpa >= 8.0:
            return "A"
        elif self.gpa >= 7.0:
            return "B+"
        elif self.gpa >= 6.0:
            return "B"
        elif self.gpa >= 5.0:
            return "C"
        else:
            return "F"
        


@app.post('/create', status_code=201)
def create_student(student:Student):
    data = load_data()
    students = data["students"]

    print(student.id)

    if student.id in students:
        raise HTTPException(status_code=409,detail="Already an ID is present in the database")

    students[student.id] = student.model_dump(exclude={"id","grade"})

    save_data(data)

    return {"message":"Student has been successfully created", "student":student}


class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=50)
    age: int | None = Field(default=None, gt=0, lt=100)
    email: EmailStr | None = None
    gender: Literal["male", "female", "others"] | None = None

    course: str | None = None
    year: int | None = Field(default=None, gt=0, lt=5)
    gpa: float | None = Field(default=None, gt=0.0, le=10.0)
    subjects: list[str] | None = None
    address: Address | None = None


@app.put('/update/{student_id}')
def update_student(
    studentUpdate : StudentUpdate,
    student_id : str = Path(..., description="The ID of the student")
    ):

    data = load_data()
    students = data["students"]

    if student_id not in students:
        raise HTTPException(status_code=404, detail=f"{student_id} not found")

    # Get the existing student data as it is
    existing_student = students[student_id]

    # GET dict as we have the object from the input
    updated_student = studentUpdate.model_dump(exclude_unset=True)

    # copy nw value to existing one
    for key, value in updated_student.items():
        existing_student[key] = value
        # OR existing_student.update(updated_student)

    # IMP :- Check the sanity of the class
    student = Student(id=student_id, **existing_student)

    # convert to dict without id and grade
    students[student_id] = student.model_dump(exclude=["id","grade"])

    # save data in json file
    save_data(data)

    return {"message":"Student updated successfully","student":student}


@app.delete('/delete/{student_id}')
def delete_student(student_id: str = Path(...)):
    data = load_data()
    students = data["students"]

    if student_id not in students:
        raise HTTPException (status_code=404, detail=f"{student_id} is not present in the database")

    del students[student_id]
    save_data(data)

    return {"message":"Student deleted successfully", "student_id":student_id}











