from app.database.database import Base, engine

from app.models.user import User
from app.models.vessel import Vessel
from app.models.incident import Incident


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database connected successfully.")
    print("Tables created successfully.")


if __name__ == "__main__":
    init_db()