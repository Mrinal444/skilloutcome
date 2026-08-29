from app.database import SessionLocal, engine
from app.models.user import User

print("DATABASE URL:", engine.url)
print("DATABASE PATH:", engine.url.database)

db = SessionLocal()

users = db.query(User).all()

print("NUMBER OF USERS:", len(users))

for user in users:
    print(
        "ID:", user.id,
        "| Name:", user.name,
        "| Email:", user.email,
        "| Role:", user.role
    )

db.close()