from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse

app = FastAPI()

# Authentication setup
security = HTTPBasic()

# In-memory database for patient records
patients_db = {}

# Patient model
class Patient(BaseModel):
    id: int
    name: str = Field(..., min_length=1)
    age: int = Field(..., ge=0)
    condition: Optional[str] = None

# Authentication dependency
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    valid_username = "admin"
    valid_password = "password123"
    if credentials.username != valid_username or credentials.password != valid_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials

# Add a new patient
@app.post("/patients", status_code=201, response_model=Patient)
def add_patient(patient: Patient, credentials: HTTPBasicCredentials = Depends(authenticate)):
    if patient.id in patients_db:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    patients_db[patient.id] = patient
    return patient

# Retrieve all patients
@app.get("/patients", response_model=List[Patient])
def get_patients(credentials: HTTPBasicCredentials = Depends(authenticate)):
    return list(patients_db.values())

# Retrieve a specific patient by ID
@app.get("/patients/{patient_id}", response_model=Patient)
def get_patient(patient_id: int, credentials: HTTPBasicCredentials = Depends(authenticate)):
    patient = patients_db.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

# Update a patient's record
@app.put("/patients/{patient_id}", response_model=Patient)
def update_patient(patient_id: int, updated_patient: Patient, credentials: HTTPBasicCredentials = Depends(authenticate)):
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    if patient_id != updated_patient.id:
        raise HTTPException(status_code=400, detail="Patient ID mismatch")
    patients_db[patient_id] = updated_patient
    return updated_patient

# Error handler for 401 Unauthorized
@app.exception_handler(HTTPException)
def unauthorized_exception_handler(request, exc):
    if exc.status_code == 401:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized access"})
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})