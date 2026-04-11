from pydantic import BaseModel

class StudentData(BaseModel):
    G1: int
    G2: int
    absences: int
    failures: int
    studytime: int
    Medu: int
    Fedu: int
    goout: int
    health: int
    higher: str  # "yes" or "no"
    sex: str     # "F" or "M"
    school: str  # "GP" or "MS"