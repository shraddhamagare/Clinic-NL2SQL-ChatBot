from vanna.capabilities.agent_memory import ToolMemory
from vanna.core.user.models import User
from vanna_setup import get_agent, get_memory

QA_PAIRS = [
    ("How many patients do we have?", "SELECT COUNT(*) AS total_patients FROM patients;"),
    ("List all doctors and their specializations", "SELECT name, specialization, department FROM doctors ORDER BY specialization;"),
    ("Which city has the most patients?", "SELECT city, COUNT(*) AS patient_count FROM patients GROUP BY city ORDER BY patient_count DESC LIMIT 1;"),
    ("How many male and female patients do we have?", "SELECT gender, COUNT(*) AS count FROM patients GROUP BY gender;"),
    ("Which doctor has the most appointments?", "SELECT d.name, COUNT(a.id) AS total FROM doctors d JOIN appointments a ON a.doctor_id = d.id GROUP BY d.name ORDER BY total DESC LIMIT 1;"),
    ("Show appointments by status", "SELECT status, COUNT(*) AS count FROM appointments GROUP BY status ORDER BY count DESC;"),
    ("What is the total revenue?", "SELECT SUM(total_amount) AS total_revenue FROM invoices WHERE status = 'Paid';"),
    ("Show unpaid invoices", "SELECT p.first_name, p.last_name, i.total_amount, i.status FROM invoices i JOIN patients p ON p.id = i.patient_id WHERE i.status IN ('Pending','Overdue');"),
    ("Show revenue by doctor", "SELECT d.name, SUM(i.total_amount) AS revenue FROM invoices i JOIN appointments a ON a.patient_id = i.patient_id JOIN doctors d ON d.id = a.doctor_id GROUP BY d.name ORDER BY revenue DESC;"),
    ("Show monthly appointment count for past 6 months", "SELECT STRFTIME('%Y-%m', appointment_date) AS month, COUNT(*) AS count FROM appointments WHERE appointment_date >= DATE('now','-6 months') GROUP BY month ORDER BY month;"),
    ("How many cancelled appointments are there?", "SELECT COUNT(*) AS cancelled FROM appointments WHERE status='Cancelled';"),
    ("Top 5 patients by spending", "SELECT p.first_name, p.last_name, SUM(i.total_amount) AS total FROM patients p JOIN invoices i ON i.patient_id = p.id GROUP BY p.id ORDER BY total DESC LIMIT 5;"),
    ("List patients who visited more than 3 times", "SELECT p.first_name, p.last_name, COUNT(a.id) AS visits FROM patients p JOIN appointments a ON a.patient_id = p.id GROUP BY p.id HAVING visits > 3;"),
    ("Average treatment cost by specialization", "SELECT d.specialization, AVG(t.cost) AS avg_cost FROM treatments t JOIN appointments a ON a.id = t.appointment_id JOIN doctors d ON d.id = a.doctor_id GROUP BY d.specialization;"),
    ("Show patient registration trend by month", "SELECT STRFTIME('%Y-%m', registered_date) AS month, COUNT(*) AS count FROM patients GROUP BY month ORDER BY month;"),
]

def seed():
    memory = get_memory()
    user = User(id="default_user", email="user@clinic.com", group_memberships=["users"])

    print(f"🌱 Seeding {len(QA_PAIRS)} Q&A pairs...\n")

    # Try to find the correct method name
    methods = [m for m in dir(memory) if not m.startswith('_')]
    print(f"Available memory methods: {methods}\n")

    for i, (question, sql) in enumerate(QA_PAIRS, 1):
        try:
            item = ToolMemory(
                question=question,
                tool_name="run_sql",
                args={"sql": sql}
            )
            # Try different method names
            if hasattr(memory, 'add'):
                memory.save_tool_usage(item, user=user)
            elif hasattr(memory, 'store'):
                memory.store(item, user=user)
            elif hasattr(memory, 'save_memory'):
                memory.save_memory(item, user=user)
            elif hasattr(memory, 'add_memory'):
                memory.add_memory(item, user=user)
            else:
                print(f"  Could not find save method. Methods: {methods}")
                break
            print(f"  [{i:02d}] ✅ {question}")
        except Exception as e:
            print(f"  [{i:02d}] ❌ {question} → {e}")

    print(f"\n✅ Seeding complete!")

if __name__ == "__main__":
    seed()