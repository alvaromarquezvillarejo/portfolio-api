from fastapi import FastAPI
from app.routes import users
from app.database import Base, engine

# Crear tablas
Base.metadata.create_all(bind=engine)

# Inicializar app
app = FastAPI()

# Incluir rutas
app.include_router(users.router)

# Endpoint raíz
@app.get("/")
def root():
    return {"message": "API funcionando 🚀"}