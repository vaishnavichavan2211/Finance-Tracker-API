

import sys
import os
from datetime import date

# Allow importing from the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.record import FinancialRecord, TransactionType, RecordCategory

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)


def run_seed():
    db = SessionLocal()

    # ── Check if already seeded 
    if db.query(User).count() > 0:
        print("⚠️  Database already has data. Skipping seed to avoid duplicates.")
        db.close()
        return

    print("🌱 Seeding database with sample data...")

    # ── Create sample users 
    users = [
        User(
            full_name = "Alice Admin",
            email     = "alice@example.com",
            hashed_pw = hash_password("admin123"),
            role      = UserRole.ADMIN,
        ),
        User(
            full_name = "Bob Analyst",
            email     = "bob@example.com",
            hashed_pw = hash_password("analyst123"),
            role      = UserRole.ANALYST,
        ),
        User(
            full_name = "Carol Viewer",
            email     = "carol@example.com",
            hashed_pw = hash_password("viewer123"),
            role      = UserRole.VIEWER,
        ),
    ]

    db.add_all(users)
    db.commit()
    for u in users:
        db.refresh(u)

    print(f"  ✅ Created {len(users)} users")

    # ── Create sample financial records for Alice 
    alice_id = users[0].user_id
    bob_id   = users[1].user_id

    records = [
        # Alice's income
        FinancialRecord(amount=5000.00, txn_type=TransactionType.INCOME,  category=RecordCategory.SALARY,        txn_date=date(2024, 3, 1),  notes="March salary",           owner_id=alice_id),
        FinancialRecord(amount=800.00,  txn_type=TransactionType.INCOME,  category=RecordCategory.FREELANCE,     txn_date=date(2024, 3, 10), notes="Logo design project",    owner_id=alice_id),
        FinancialRecord(amount=200.00,  txn_type=TransactionType.INCOME,  category=RecordCategory.INVESTMENT,    txn_date=date(2024, 3, 15), notes="Dividend payout",        owner_id=alice_id),
        # Alice's expenses
        FinancialRecord(amount=1200.00, txn_type=TransactionType.EXPENSE, category=RecordCategory.HOUSING,       txn_date=date(2024, 3, 2),  notes="March rent",             owner_id=alice_id),
        FinancialRecord(amount=320.00,  txn_type=TransactionType.EXPENSE, category=RecordCategory.FOOD,          txn_date=date(2024, 3, 5),  notes="Weekly groceries x4",   owner_id=alice_id),
        FinancialRecord(amount=85.00,   txn_type=TransactionType.EXPENSE, category=RecordCategory.TRANSPORT,     txn_date=date(2024, 3, 7),  notes="Monthly bus pass",       owner_id=alice_id),
        FinancialRecord(amount=150.00,  txn_type=TransactionType.EXPENSE, category=RecordCategory.ENTERTAINMENT, txn_date=date(2024, 3, 20), notes="Concert tickets",        owner_id=alice_id),
        FinancialRecord(amount=60.00,   txn_type=TransactionType.EXPENSE, category=RecordCategory.UTILITIES,     txn_date=date(2024, 3, 22), notes="Electricity bill",       owner_id=alice_id),
        FinancialRecord(amount=45.00,   txn_type=TransactionType.EXPENSE, category=RecordCategory.HEALTHCARE,    txn_date=date(2024, 3, 25), notes="Pharmacy",               owner_id=alice_id),

        # April records for Alice
        FinancialRecord(amount=5000.00, txn_type=TransactionType.INCOME,  category=RecordCategory.SALARY,        txn_date=date(2024, 4, 1),  notes="April salary",           owner_id=alice_id),
        FinancialRecord(amount=1200.00, txn_type=TransactionType.EXPENSE, category=RecordCategory.HOUSING,       txn_date=date(2024, 4, 2),  notes="April rent",             owner_id=alice_id),
        FinancialRecord(amount=500.00,  txn_type=TransactionType.EXPENSE, category=RecordCategory.TRAVEL,        txn_date=date(2024, 4, 15), notes="Weekend trip flights",   owner_id=alice_id),
        FinancialRecord(amount=280.00,  txn_type=TransactionType.EXPENSE, category=RecordCategory.SHOPPING,      txn_date=date(2024, 4, 18), notes="Spring wardrobe",        owner_id=alice_id),

        # Bob's records
        FinancialRecord(amount=3500.00, txn_type=TransactionType.INCOME,  category=RecordCategory.SALARY,        txn_date=date(2024, 3, 1),  notes="March salary",           owner_id=bob_id),
        FinancialRecord(amount=600.00,  txn_type=TransactionType.INCOME,  category=RecordCategory.FREELANCE,     txn_date=date(2024, 3, 12), notes="Data analysis contract", owner_id=bob_id),
        FinancialRecord(amount=900.00,  txn_type=TransactionType.EXPENSE, category=RecordCategory.HOUSING,       txn_date=date(2024, 3, 2),  notes="March rent",             owner_id=bob_id),
        FinancialRecord(amount=200.00,  txn_type=TransactionType.EXPENSE, category=RecordCategory.FOOD,          txn_date=date(2024, 3, 8),  notes="Groceries",              owner_id=bob_id),
        FinancialRecord(amount=120.00,  txn_type=TransactionType.EXPENSE, category=RecordCategory.EDUCATION,     txn_date=date(2024, 3, 16), notes="Online course subscription", owner_id=bob_id),
    ]

    db.add_all(records)
    db.commit()

    print(f" Created {len(records)} financial records")
    print()
    print(" Seeding complete! You can now log in with:")
    print("   Admin   → alice@example.com  / admin123")
    print("   Analyst → bob@example.com    / analyst123")
    print("   Viewer  → carol@example.com  / viewer123")
    print()
    print("   Swagger docs: http://localhost:8000/docs")

    db.close()


if __name__ == "__main__":
    run_seed()
