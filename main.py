from fastapi import FastAPI

from database import Base, engine

from routers import employees
from routers import competencies
from routers import assessments
from routers import roles
from routers import recommendations
from routers import materials
from routers import quizzes

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="KarmaSkill AI",
    description=(
        "AI-powered Competency Gap and "
        "Personalized Learning Engine"
    ),
    version="0.1.0"
)


app.include_router(employees.router)
app.include_router(competencies.router)
app.include_router(assessments.router)
app.include_router(roles.router)
app.include_router(recommendations.router)
app.include_router(materials.router)
app.include_router(quizzes.router)

@app.get("/")
def root():

    return {
        "project": "KarmaSkill AI",
        "message": "Competency Gap Engine API",
        "status": "running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }