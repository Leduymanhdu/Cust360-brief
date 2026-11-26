"""Initial database seeder matching documented demo users and account fixtures."""

from uuid import UUID
from sqlalchemy.orm import Session
from app.models import User, Account, Site, UserAccountAccess
from app.services.password_service import hash_password

SALES_USER_ID = "10000000-0000-4000-8000-000000000001"
ADMIN_USER_ID = "10000000-0000-4000-8000-000000000002"
SERVICE_USER_ID = "10000000-0000-4000-8000-000000000003"
INACTIVE_USER_ID = "10000000-0000-4000-8000-000000000004"

ACCOUNT_ABC_VIETNAM_ID = "20000000-0000-4000-8000-000000000001"
ACCOUNT_ABC_COMPANY_ID = "20000000-0000-4000-8000-000000000002"
ACCOUNT_RESTRICTED_ID = "20000000-0000-4000-8000-000000000003"

SITE_HANOI_ID = "30000000-0000-4000-8000-000000000001"
SITE_DANANG_ID = "30000000-0000-4000-8000-000000000002"


def seed_initial_data(db: Session) -> None:
    """Idempotently seed standard accounts and users into the database."""
    # 1. Accounts
    existing_acc = db.query(Account).filter_by(id=ACCOUNT_ABC_VIETNAM_ID).first()
    if not existing_acc:
        acc1 = Account(
            id=ACCOUNT_ABC_VIETNAM_ID,
            legal_name="ABC Vietnam Ltd",
            tax_code="0123456789",
            industry="Manufacturing",
            status="ACTIVE",
        )
        acc2 = Account(
            id=ACCOUNT_ABC_COMPANY_ID,
            legal_name="ABC Vietnam Company",
            tax_code="0987654321",
            industry="Industrial equipment",
            status="ACTIVE",
        )
        acc3 = Account(
            id=ACCOUNT_RESTRICTED_ID,
            legal_name="Hai Ha Industrial JSC",
            tax_code="0102030405",
            industry="Food manufacturing",
            status="ACTIVE",
        )
        db.add_all([acc1, acc2, acc3])
        db.commit()

        # Sites
        site1 = Site(
            id=SITE_HANOI_ID,
            account_id=ACCOUNT_ABC_VIETNAM_ID,
            site_name="Hanoi Factory",
            address="KCN Thang Long, Dong Anh, Hanoi",
        )
        site2 = Site(
            id=SITE_DANANG_ID,
            account_id=ACCOUNT_ABC_COMPANY_ID,
            site_name="Da Nang Branch",
            address="KCN Hoa Khanh, Da Nang",
        )
        db.add_all([site1, site2])
        db.commit()

    # 2. Users with hashed passwords
    existing_sales = db.query(User).filter_by(email="sales@songnhat.com.vn").first()
    if not existing_sales:
        sales_user = User(
            id=SALES_USER_ID,
            email="sales@songnhat.com.vn",
            password_hash=hash_password("SecurePass123!"),
            full_name="Nguyen Van A",
            role="SALES",
            is_active=True,
            failed_login_attempts=0,
        )
        admin_user = User(
            id=ADMIN_USER_ID,
            email="admin@songnhat.com.vn",
            password_hash=hash_password("AdminPass123!"),
            full_name="SongNhat Admin",
            role="ADMIN",
            is_active=True,
            failed_login_attempts=0,
        )
        service_user = User(
            id=SERVICE_USER_ID,
            email="service@songnhat.com.vn",
            password_hash=hash_password("ServicePass123!"),
            full_name="Tran Thi Service",
            role="SERVICE",
            is_active=True,
            failed_login_attempts=0,
        )
        inactive_user = User(
            id=INACTIVE_USER_ID,
            email="inactive@songnhat.com.vn",
            password_hash=hash_password("InactivePass123!"),
            full_name="Inactive Employee",
            role="SALES",
            is_active=False,
            failed_login_attempts=0,
        )
        db.add_all([sales_user, admin_user, service_user, inactive_user])
        db.commit()

        # 3. User Account Access permissions (Account Scope)
        # Sales user has access to ACC 1 and ACC 2, but NOT ACC 3 (restricted)
        access1 = UserAccountAccess(user_id=SALES_USER_ID, account_id=ACCOUNT_ABC_VIETNAM_ID)
        access2 = UserAccountAccess(user_id=SALES_USER_ID, account_id=ACCOUNT_ABC_COMPANY_ID)
        # Admin has access to all
        access3 = UserAccountAccess(user_id=ADMIN_USER_ID, account_id=ACCOUNT_ABC_VIETNAM_ID)
        access4 = UserAccountAccess(user_id=ADMIN_USER_ID, account_id=ACCOUNT_ABC_COMPANY_ID)
        access5 = UserAccountAccess(user_id=ADMIN_USER_ID, account_id=ACCOUNT_RESTRICTED_ID)

        db.add_all([access1, access2, access3, access4, access5])
        db.commit()
