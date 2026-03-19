# create_admin.py
from app.database import SessionLocal, Base, engine
from app.models import User
from passlib.context import CryptContext

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# Configuración de hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Datos del admin inicial
admin_email = "admin@portfolio.com"
admin_password = "Admin1234"  # Cambia a una contraseña segura
admin_role = "admin"

# Conexión a la DB
db = SessionLocal()
try:
    # Verificar si ya existe
    existing_admin = db.query(User).filter(User.email == admin_email).first()
    if existing_admin:
        print("Admin ya existe:", admin_email)
    else:
        hashed_password = pwd_context.hash(admin_password)
        admin_user = User(email=admin_email, password=hashed_password, role=admin_role)
        db.add(admin_user)
        db.commit()
        print("Admin creado con éxito:", admin_email)
finally:
    db.close()
