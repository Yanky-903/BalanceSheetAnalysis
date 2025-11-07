from .db import SessionLocal, engine
from .models import User, Company, UserCompany, Base
from .auth import get_password_hash
from sqlalchemy import text

def seed():
    # create tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # create users if not exists
        if db.query(User).filter(User.email == "analyst@example.com").first() is None:
            u1 = User(email="analyst@example.com", name="Analyst One", hashed_password=get_password_hash("analystpass"), role="analyst")
            db.add(u1)
        if db.query(User).filter(User.email == "ceo_jio@example.com").first() is None:
            u2 = User(email="ceo_jio@example.com", name="CEO Jio", hashed_password=get_password_hash("ceopass"), role="ceo")
            db.add(u2)
        if db.query(User).filter(User.email == "ambani@example.com").first() is None:
            u3 = User(email="ambani@example.com", name="Ambani Family", hashed_password=get_password_hash("adminpass"), role="group_admin", group_name="Reliance Group")
            db.add(u3)
        db.commit()

        # create companies if not exists
        if db.query(Company).filter(Company.name == "Reliance Retail Ventures").first() is None:
            c1 = Company(name="Reliance Retail Ventures", ticker="RILR", group_name="Reliance Group")
            db.add(c1)
        if db.query(Company).filter(Company.name == "Jio Platforms").first() is None:
            c2 = Company(name="Jio Platforms", ticker="JIO", group_name="Reliance Group")
            db.add(c2)
        db.commit()

        # link analyst to Reliance Retail and CEO to Jio via safe inserts
        # we use text() to support SQLAlchemy text mode when needed
        # find ids
        analyst = db.query(User).filter(User.email == "analyst@example.com").first()
        ceo_jio = db.query(User).filter(User.email == "ceo_jio@example.com").first()
        c_retail = db.query(Company).filter(Company.name == "Reliance Retail Ventures").first()
        c_jio = db.query(Company).filter(Company.name == "Jio Platforms").first()

        # insert only if not present
        if analyst and c_retail:
            exists = db.execute(text("SELECT 1 FROM user_companies WHERE user_id = :u AND company_id = :c"),
                                {"u": analyst.id, "c": c_retail.id}).fetchone()
            if not exists:
                db.execute(text("INSERT INTO user_companies(user_id, company_id) VALUES (:u, :c)"),
                           {"u": analyst.id, "c": c_retail.id})
        if ceo_jio and c_jio:
            exists = db.execute(text("SELECT 1 FROM user_companies WHERE user_id = :u AND company_id = :c"),
                                {"u": ceo_jio.id, "c": c_jio.id}).fetchone()
            if not exists:
                db.execute(text("INSERT INTO user_companies(user_id, company_id) VALUES (:u, :c)"),
                           {"u": ceo_jio.id, "c": c_jio.id})

        db.commit()
        print("Seed completed.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
