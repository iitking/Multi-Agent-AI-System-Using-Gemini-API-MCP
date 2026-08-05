import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy import select
from backend.database.session import engine, async_session, init_db as init_db_tables
from backend.database.models import User, SystemMetric
from backend.api.auth import get_password_hash


async def seed_data():
    await init_db_tables()
    async with async_session() as session:
        # Seed users if not exist
        res = await session.execute(select(User).where(User.username == "admin"))
        admin_user = res.scalar_one_or_none()

        if not admin_user:
            users = [
                User(
                    username="admin",
                    email="admin@apexcloud.io",
                    hashed_password=get_password_hash("admin123"),
                    role="admin",
                    tenant_id="enterprise_demo"
                ),
                User(
                    username="analyst_jane",
                    email="jane.doe@apexcloud.io",
                    hashed_password=get_password_hash("analyst123"),
                    role="analyst",
                    tenant_id="enterprise_demo"
                ),
                User(
                    username="viewer_bob",
                    email="bob.smith@apexcloud.io",
                    hashed_password=get_password_hash("viewer123"),
                    role="viewer",
                    tenant_id="enterprise_demo"
                )
            ]
            session.add_all(users)

            # Seed initial system benchmark metrics
            metrics = [
                SystemMetric(metric_name="task_completion_rate", metric_value=96.4, tags={"target": "sla"}),
                SystemMetric(metric_name="calculation_accuracy", metric_value=99.8, tags={"dataset": "sales_q3"}),
                SystemMetric(metric_name="median_latency_seconds", metric_value=12.4, tags={"p": "50"}),
                SystemMetric(metric_name="p95_latency_seconds", metric_value=24.1, tags={"p": "95"}),
                SystemMetric(metric_name="cost_per_run_usd", metric_value=0.042, tags={"model": "gemini-2.5-flash"}),
                SystemMetric(metric_name="approval_gate_acceptance_rate", metric_value=91.2, tags={"policy": "strict"})
            ]
            session.add_all(metrics)

            await session.commit()
            print("Database initialized and seed data successfully created.")
        else:
            print("Database already contains seed data.")


if __name__ == "__main__":
    asyncio.run(seed_data())
