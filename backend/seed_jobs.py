import pandas as pd
from database import SessionLocal
import models

CSV_PATH = "data/job_postings.csv"
MAX_ROWS = 500

def safe_float(value):
    try:
        return float(value) if pd.notna(value) else None
    except (ValueError, TypeError):
        return None


def seed_jobs():
    df = pd.read_csv(CSV_PATH)
    df = df.dropna(subset=["title", "description"])
    df = df.head(MAX_ROWS)

    db = SessionLocal()

    # Delete matches first, since they reference jobs via foreign key
    db.query(models.Match).delete()
    db.query(models.Job).delete()
    db.commit()

    count = 0
    for _, row in df.iterrows():
        job = models.Job(
            title=str(row["title"])[:255],
            company=f"Company #{int(row['company_id'])}" if pd.notna(row.get("company_id")) else "Unknown Company",
            description=str(row["description"])[:5000],
            url=str(row["job_posting_url"]) if pd.notna(row.get("job_posting_url")) else None,
            location=str(row["location"]) if pd.notna(row.get("location")) else None,
            experience_level=str(row["formatted_experience_level"]) if pd.notna(row.get("formatted_experience_level")) else None,
            work_type=str(row["formatted_work_type"]) if pd.notna(row.get("formatted_work_type")) else None,
            salary_min=safe_float(row.get("min_salary")),
            salary_max=safe_float(row.get("max_salary")),
        )
        db.add(job)
        count += 1

    db.commit()
    db.close()
    print(f"Seeded {count} jobs into the database.")


if __name__ == "__main__":
    seed_jobs()