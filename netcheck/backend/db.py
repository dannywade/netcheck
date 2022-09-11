from sqlmodel import SQLModel, create_engine, Session
from datetime import datetime
from .models import TestResults, DeviceInventory

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Adds data in as rows
def create_dummy_data():
    current_date = datetime.now()
    # current_date = get_time.strftime("%m/%d/%Y %H:%M:%S")
    result1 = TestResults(
        name="circuit_upgrade",
        executed_at=current_date,
        success_rate=100.0,
        total_tests=3,
        tests_passed=3,
        tests_failed=0,
    )
    result2 = TestResults(
        name="wan_check",
        executed_at=current_date,
        success_rate=50.0,
        total_tests=4,
        tests_passed=2,
        tests_failed=2,
    )
    result3 = TestResults(
        name="l2_stp_check",
        executed_at=current_date,
        success_rate=0,
        total_tests=3,
        tests_passed=0,
        tests_failed=3,
    )
    result4 = DeviceInventory(
        hostname="RT-1",
        mgmt_ip="10.1.1.1",
        vendor="cisco",
        model="9500",
        os_version="17.6.6",
        serial_number="ABC1234",
    )
    result5 = DeviceInventory(
        hostname="RT-2",
        mgmt_ip="10.1.1.2",
        vendor="cisco",
        model="9300",
        os_version="17.3.4a",
        serial_number="ABCD12346",
    )
    result6 = DeviceInventory(
        hostname="RT-3",
        mgmt_ip="10.1.1.3",
        vendor="cisco",
        model="9400",
        os_version="17.8.8",
        serial_number="QWERTY4321",
    )
    result7 = DeviceInventory(
        hostname="SW-1",
        mgmt_ip="10.1.1.2",
        vendor="cisco",
        model="9600",
        os_version="16.8.5",
        serial_number="ZYX6789",
    )

    with Session(engine) as session:
        session.add(result1)
        session.add(result2)
        session.add(result3)
        session.add(result4)
        session.add(result5)
        session.add(result6)
        session.add(result7)

        session.commit()

        session.refresh(result1)
