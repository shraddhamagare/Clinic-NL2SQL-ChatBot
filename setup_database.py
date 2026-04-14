import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "clinic.db"

# --- Sample Data Pools ---
first_names = ["Aarav","Priya","Rohit","Sneha","Vikram","Ananya","Karan","Meera",
               "Arjun","Pooja","Rahul","Divya","Suresh","Kavya","Nikhil","Lakshmi",
               "Amit","Riya","Deepak","Nisha","Sanjay","Anjali","Rajesh","Sunita",
               "Aditya","Swati","Manish","Geeta","Vinod","Rekha"]
last_names  = ["Sharma","Verma","Patel","Singh","Kumar","Gupta","Mehta","Joshi",
               "Reddy","Nair","Iyer","Pillai","Shah","Rao","Malhotra","Chopra",
               "Bose","Das","Mishra","Tiwari"]
cities      = ["Mumbai","Delhi","Bengaluru","Chennai","Hyderabad","Pune","Kolkata","Jaipur","Ahmedabad","Lucknow"]
genders     = ["M","F"]
specializations = ["Dermatology","Cardiology","Orthopedics","General","Pediatrics"]
departments     = ["Skin Care","Heart Care","Bone & Joint","General Medicine","Child Care"]
statuses_appt   = ["Scheduled","Completed","Cancelled","No-Show"]
statuses_inv    = ["Paid","Pending","Overdue"]
treatment_names = ["Consultation","X-Ray","Blood Test","ECG","MRI Scan","Physiotherapy",
                   "Vaccination","Skin Biopsy","Echo","Ultrasound","Surgery","Dressing"]

def random_date(start_days_ago=365, end_days_ago=0):
    days = random.randint(end_days_ago, start_days_ago)
    return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

def random_datetime(start_days_ago=365, end_days_ago=0):
    days  = random.randint(end_days_ago, start_days_ago)
    hour  = random.randint(8, 17)
    minute = random.choice([0, 15, 30, 45])
    return (datetime.now() - timedelta(days=days)).replace(hour=hour, minute=minute, second=0).strftime("%Y-%m-%d %H:%M:%S")

def maybe_null(value, probability=0.15):
    """Return None with given probability to simulate realistic NULLs."""
    return None if random.random() < probability else value

def create_schema(conn):
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS patients (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name      TEXT NOT NULL,
            last_name       TEXT NOT NULL,
            email           TEXT,
            phone           TEXT,
            date_of_birth   DATE,
            gender          TEXT,
            city            TEXT,
            registered_date DATE
        );

        CREATE TABLE IF NOT EXISTS doctors (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            specialization  TEXT,
            department      TEXT,
            phone           TEXT
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id       INTEGER,
            doctor_id        INTEGER,
            appointment_date DATETIME,
            status           TEXT,
            notes            TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (doctor_id)  REFERENCES doctors(id)
        );

        CREATE TABLE IF NOT EXISTS treatments (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id     INTEGER,
            treatment_name     TEXT,
            cost               REAL,
            duration_minutes   INTEGER,
            FOREIGN KEY (appointment_id) REFERENCES appointments(id)
        );

        CREATE TABLE IF NOT EXISTS invoices (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id    INTEGER,
            invoice_date  DATE,
            total_amount  REAL,
            paid_amount   REAL,
            status        TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        );
    """)
    conn.commit()

def insert_doctors(conn):
    cur = conn.cursor()
    doctor_names = [
        "Dr. Anil Kapoor","Dr. Sunita Sharma","Dr. Ramesh Patel","Dr. Priya Nair","Dr. Vikram Singh",
        "Dr. Meena Iyer","Dr. Suresh Reddy","Dr. Kavitha Rao","Dr. Arjun Mehta","Dr. Divya Pillai",
        "Dr. Kiran Gupta","Dr. Anjali Joshi","Dr. Deepak Verma","Dr. Rekha Malhotra","Dr. Nikhil Bose"
    ]
    doctors = []
    for i, name in enumerate(doctor_names):
        spec  = specializations[i % 5]
        dept  = departments[i % 5]
        phone = maybe_null(f"9{random.randint(100000000,999999999)}")
        doctors.append((name, spec, dept, phone))
    cur.executemany("INSERT INTO doctors (name,specialization,department,phone) VALUES (?,?,?,?)", doctors)
    conn.commit()

def insert_patients(conn):
    cur = conn.cursor()
    patients = []
    for _ in range(200):
        fn    = random.choice(first_names)
        ln    = random.choice(last_names)
        email = maybe_null(f"{fn.lower()}.{ln.lower()}{random.randint(1,99)}@email.com")
        phone = maybe_null(f"9{random.randint(100000000,999999999)}")
        dob   = random_date(start_days_ago=25*365, end_days_ago=5*365)
        gender= random.choice(genders)
        city  = random.choice(cities)
        reg   = random_date(start_days_ago=730, end_days_ago=0)
        patients.append((fn, ln, email, phone, dob, gender, city, reg))
    cur.executemany("""
        INSERT INTO patients (first_name,last_name,email,phone,date_of_birth,gender,city,registered_date)
        VALUES (?,?,?,?,?,?,?,?)""", patients)
    conn.commit()

def insert_appointments(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM patients")
    patient_ids = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT id FROM doctors")
    doctor_ids  = [r[0] for r in cur.fetchall()]

    # Make some patients repeat visitors (realistic skew)
    weighted_patients = patient_ids + random.choices(patient_ids[:40], k=200)
    # Make some doctors busier
    weighted_doctors  = doctor_ids  + random.choices(doctor_ids[:5],  k=50)

    appointments = []
    for _ in range(500):
        pid    = random.choice(weighted_patients)
        did    = random.choice(weighted_doctors)
        dt     = random_datetime()
        status = random.choices(statuses_appt, weights=[15,50,20,15])[0]
        notes  = maybe_null(f"Patient visited for routine checkup.", probability=0.4)
        appointments.append((pid, did, dt, status, notes))

    cur.executemany("""
        INSERT INTO appointments (patient_id,doctor_id,appointment_date,status,notes)
        VALUES (?,?,?,?,?)""", appointments)
    conn.commit()

def insert_treatments(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM appointments WHERE status='Completed'")
    completed_ids = [r[0] for r in cur.fetchall()]

    # Pick ~350 of completed appointments for treatments
    sample_ids = random.sample(completed_ids, min(350, len(completed_ids)))
    treatments = []
    for appt_id in sample_ids:
        tname    = random.choice(treatment_names)
        cost     = round(random.uniform(50, 5000), 2)
        duration = random.randint(10, 120)
        treatments.append((appt_id, tname, cost, duration))

    cur.executemany("""
        INSERT INTO treatments (appointment_id,treatment_name,cost,duration_minutes)
        VALUES (?,?,?,?)""", treatments)
    conn.commit()

def insert_invoices(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM patients")
    patient_ids = [r[0] for r in cur.fetchall()]

    sample_patients = random.sample(patient_ids, min(300, len(patient_ids)))
    invoices = []
    for pid in sample_patients:
        inv_date     = random_date()
        total        = round(random.uniform(100, 10000), 2)
        status       = random.choices(statuses_inv, weights=[50,30,20])[0]
        paid         = total if status == "Paid" else round(random.uniform(0, total * 0.5), 2)
        invoices.append((pid, inv_date, total, paid, status))

    cur.executemany("""
        INSERT INTO invoices (patient_id,invoice_date,total_amount,paid_amount,status)
        VALUES (?,?,?,?,?)""", invoices)
    conn.commit()

def main():
    conn = sqlite3.connect(DB_NAME)
    print("🔧 Creating schema...")
    create_schema(conn)

    print("👨‍⚕️ Inserting doctors...")
    insert_doctors(conn)

    print("🧑‍🤝‍🧑 Inserting patients...")
    insert_patients(conn)

    print("📅 Inserting appointments...")
    insert_appointments(conn)

    print("💊 Inserting treatments...")
    insert_treatments(conn)

    print("🧾 Inserting invoices...")
    insert_invoices(conn)

    # Summary
    cur = conn.cursor()
    counts = {}
    for table in ["patients","doctors","appointments","treatments","invoices"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = cur.fetchone()[0]

    conn.close()
    print("\n✅ Database created successfully!")
    print(f"   Created {counts['patients']} patients, {counts['doctors']} doctors, "
          f"{counts['appointments']} appointments, {counts['treatments']} treatments, "
          f"{counts['invoices']} invoices")
    print(f"   Database saved to: {DB_NAME}")

if __name__ == "__main__":
    main()