from sqlalchemy import Column, Integer, String
from app.database import Base  # import absoluto, evita warnings en VS Code

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user")  # user o admin

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    