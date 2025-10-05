from __future__ import annotations

import os
import socket
from datetime import datetime

from typing import Dict, List
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi import Query, Path
from typing import Optional

from models.person import PersonCreate, PersonRead, PersonUpdate
from models.address import AddressCreate, AddressRead, AddressUpdate
from models.allergy import AllergyCreate, AllergyRead, AllergyUpdate
from models.medication import MedicationCreate, MedicationRead, MedicationUpdate
from models.health import Health

port = int(os.environ.get("FASTAPIPORT", 8000))

# -----------------------------------------------------------------------------
# Fake in-memory "databases"
# -----------------------------------------------------------------------------
persons: Dict[UUID, PersonRead] = {}
addresses: Dict[UUID, AddressRead] = {}
allergies: Dict[UUID, AllergyRead] = {}
medications: Dict[UUID, MedicationRead] = {}

app = FastAPI(
    title="Person/Address API",
    description="Demo FastAPI app using Pydantic v2 models for Person and Address",
    version="0.1.0",
)

# -----------------------------------------------------------------------------
# Address endpoints
# -----------------------------------------------------------------------------

def make_health(echo: Optional[str], path_echo: Optional[str]=None) -> Health:
    return Health(
        status=200,
        status_message="OK",
        timestamp=datetime.utcnow().isoformat() + "Z",
        ip_address=socket.gethostbyname(socket.gethostname()),
        echo=echo,
        path_echo=path_echo
    )

@app.get("/health", response_model=Health)
def get_health_no_path(echo: str | None = Query(None, description="Optional echo string")):
    # Works because path_echo is optional in the model
    return make_health(echo=echo, path_echo=None)

@app.get("/health/{path_echo}", response_model=Health)
def get_health_with_path(
    path_echo: str = Path(..., description="Required echo in the URL path"),
    echo: str | None = Query(None, description="Optional echo string"),
):
    return make_health(echo=echo, path_echo=path_echo)

@app.post("/addresses", response_model=AddressRead, status_code=201)
def create_address(address: AddressCreate):
    if address.id in addresses:
        raise HTTPException(status_code=400, detail="Address with this ID already exists")
    addresses[address.id] = AddressRead(**address.model_dump())
    return addresses[address.id]

@app.get("/addresses", response_model=List[AddressRead])
def list_addresses(
    street: Optional[str] = Query(None, description="Filter by street"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state/region"),
    postal_code: Optional[str] = Query(None, description="Filter by postal code"),
    country: Optional[str] = Query(None, description="Filter by country"),
):
    results = list(addresses.values())

    if street is not None:
        results = [a for a in results if a.street == street]
    if city is not None:
        results = [a for a in results if a.city == city]
    if state is not None:
        results = [a for a in results if a.state == state]
    if postal_code is not None:
        results = [a for a in results if a.postal_code == postal_code]
    if country is not None:
        results = [a for a in results if a.country == country]

    return results

@app.get("/addresses/{address_id}", response_model=AddressRead)
def get_address(address_id: UUID):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    return addresses[address_id]

@app.patch("/addresses/{address_id}", response_model=AddressRead)
def update_address(address_id: UUID, update: AddressUpdate):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    stored = addresses[address_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    addresses[address_id] = AddressRead(**stored)
    return addresses[address_id]

# -----------------------------------------------------------------------------
# Person endpoints
# -----------------------------------------------------------------------------
@app.post("/persons", response_model=PersonRead, status_code=201)
def create_person(person: PersonCreate):
    # Each person gets its own UUID; stored as PersonRead
    person_read = PersonRead(**person.model_dump())
    persons[person_read.id] = person_read
    return person_read

@app.get("/persons", response_model=List[PersonRead])
def list_persons(
    uni: Optional[str] = Query(None, description="Filter by Columbia UNI"),
    first_name: Optional[str] = Query(None, description="Filter by first name"),
    last_name: Optional[str] = Query(None, description="Filter by last name"),
    email: Optional[str] = Query(None, description="Filter by email"),
    phone: Optional[str] = Query(None, description="Filter by phone number"),
    birth_date: Optional[str] = Query(None, description="Filter by date of birth (YYYY-MM-DD)"),
    city: Optional[str] = Query(None, description="Filter by city of at least one address"),
    country: Optional[str] = Query(None, description="Filter by country of at least one address"),
):
    results = list(persons.values())

    if uni is not None:
        results = [p for p in results if p.uni == uni]
    if first_name is not None:
        results = [p for p in results if p.first_name == first_name]
    if last_name is not None:
        results = [p for p in results if p.last_name == last_name]
    if email is not None:
        results = [p for p in results if p.email == email]
    if phone is not None:
        results = [p for p in results if p.phone == phone]
    if birth_date is not None:
        results = [p for p in results if str(p.birth_date) == birth_date]

    # nested address filtering
    if city is not None:
        results = [p for p in results if any(addr.city == city for addr in p.addresses)]
    if country is not None:
        results = [p for p in results if any(addr.country == country for addr in p.addresses)]

    return results

@app.get("/persons/{person_id}", response_model=PersonRead)
def get_person(person_id: UUID):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    return persons[person_id]

@app.patch("/persons/{person_id}", response_model=PersonRead)
def update_person(person_id: UUID, update: PersonUpdate):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    stored = persons[person_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    persons[person_id] = PersonRead(**stored)
    return persons[person_id]




# -----------------------------------------------------------------------------
# Allergy endpoints
# -----------------------------------------------------------------------------
@app.post("/allergies", response_model=AllergyRead, status_code=201)
def create_allergy(allergy: AllergyCreate):
    # Optional FK presence check (safe no-op if persons are empty for demos)
    if getattr(allergy, "person_id", None) and allergy.person_id not in persons:
        # Not fatal for a demo API; feel free to relax to a warning if you prefer
        raise HTTPException(status_code=400, detail="person_id does not exist")
    if allergy.id in allergies:
        raise HTTPException(status_code=400, detail="Allergy with this ID already exists")
    allergies[allergy.id] = AllergyRead(**allergy.model_dump())
    return allergies[allergy.id]

@app.get("/allergies", response_model=List[AllergyRead])
def list_allergies(
    person_id: Optional[UUID] = Query(None, description="Filter by person_id"),
    allergen: Optional[str] = Query(None, description="Filter by allergen"),
    allergy_type: Optional[str] = Query(None, description="Filter by allergy_type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    noted_date: Optional[str] = Query(None, description="Filter by noted_date (YYYY-MM-DD)"),
):
    results = list(allergies.values())

    if person_id is not None:
        results = [a for a in results if a.person_id == person_id]
    if allergen is not None:
        results = [a for a in results if a.allergen == allergen]
    if allergy_type is not None:
        results = [a for a in results if a.allergy_type == allergy_type]
    if severity is not None:
        results = [a for a in results if a.severity == severity]
    if noted_date is not None:
        results = [a for a in results if (a.noted_date and str(a.noted_date) == noted_date)]

    return results

@app.get("/allergies/{allergy_id}", response_model=AllergyRead)
def get_allergy(allergy_id: UUID):
    if allergy_id not in allergies:
        raise HTTPException(status_code=404, detail="Allergy not found")
    return allergies[allergy_id]

@app.patch("/allergies/{allergy_id}", response_model=AllergyRead)
def update_allergy(allergy_id: UUID, update: AllergyUpdate):
    if allergy_id not in allergies:
        raise HTTPException(status_code=404, detail="Allergy not found")
    stored = allergies[allergy_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    allergies[allergy_id] = AllergyRead(**stored)
    return allergies[allergy_id]

# -----------------------------------------------------------------------------
# Medication endpoints
# -----------------------------------------------------------------------------
@app.post("/medications", response_model=MedicationRead, status_code=201)
def create_medication(med: MedicationCreate):
    if getattr(med, "person_id", None) and med.person_id not in persons:
        raise HTTPException(status_code=400, detail="person_id does not exist")
    if med.id in medications:
        raise HTTPException(status_code=400, detail="Medication with this ID already exists")
    medications[med.id] = MedicationRead(**med.model_dump())
    return medications[med.id]

@app.get("/medications", response_model=List[MedicationRead])
def list_medications(
    person_id: Optional[UUID] = Query(None, description="Filter by person_id"),
    name: Optional[str] = Query(None, description="Filter by medication name"),
    frequency: Optional[str] = Query(None, description="Filter by frequency"),
    is_current: Optional[bool] = Query(None, description="Filter by current flag"),
    start_date: Optional[str] = Query(None, description="Filter by exact start_date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by exact end_date (YYYY-MM-DD)"),
):
    results = list(medications.values())

    if person_id is not None:
        results = [m for m in results if m.person_id == person_id]
    if name is not None:
        results = [m for m in results if m.name == name]
    if frequency is not None:
        results = [m for m in results if m.frequency == frequency]
    if is_current is not None:
        results = [m for m in results if m.is_current == is_current]
    if start_date is not None:
        results = [m for m in results if (m.start_date and str(m.start_date) == start_date)]
    if end_date is not None:
        results = [m for m in results if (m.end_date and str(m.end_date) == end_date)]

    return results

@app.get("/medications/{medication_id}", response_model=MedicationRead)
def get_medication(medication_id: UUID):
    if medication_id not in medications:
        raise HTTPException(status_code=404, detail="Medication not found")
    return medications[medication_id]

@app.patch("/medications/{medication_id}", response_model=MedicationRead)
def update_medication(medication_id: UUID, update: MedicationUpdate):
    if medication_id not in medications:
        raise HTTPException(status_code=404, detail="Medication not found")
    stored = medications[medication_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    medications[medication_id] = MedicationRead(**stored)
    return medications[medication_id]

# -----------------------------------------------------------------------------
# Root
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Person/Address API. See /docs for OpenAPI UI."}

# -----------------------------------------------------------------------------
# Entrypoint for `python main.py`
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
