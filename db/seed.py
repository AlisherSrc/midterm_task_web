"""Python database seeder script.

Seeds the database with at least 5 wanted criminals and 10 hunt logs
using SQLAlchemy ORM.
"""

import sys
from datetime import datetime, timedelta, timezone

from app.database import Base, SessionLocal, engine
from app.models import HuntLog, WantedCriminal


def seed_database():
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        # Check if already seeded
        existing_criminals_count = session.query(WantedCriminal).count()
        if existing_criminals_count >= 5:
            print(f"Database already contains {existing_criminals_count} criminals. Skipping seed.")
            return

        print("Seeding wanted criminals...")
        criminals = [
            WantedCriminal(
                id=1,
                name="Vicious Kane",
                nickname="Red Nova",
                reward=150000.0,
                last_known_coordinates="Sector 4, Kepler-22b (-14.234, 120.451) - Abandoned titanium refinery",
                difficulty=9,
                armed=True,
                has_crew=True,
                escape_master=True,
            ),
            WantedCriminal(
                id=2,
                name="Lyra Vance",
                nickname="Silver Ghost",
                reward=85000.0,
                last_known_coordinates="Ganymede Orbital Station (D-Ring, Bay 9)",
                difficulty=7,
                armed=True,
                has_crew=False,
                escape_master=True,
            ),
            WantedCriminal(
                id=3,
                name=None,
                nickname="Obsidian Raven",
                reward=220000.0,
                last_known_coordinates="Kuiper Belt Outpost 88 (-78.112, 12.903) - Deep freeze sector",
                difficulty=10,
                armed=True,
                has_crew=True,
                escape_master=True,
            ),
            WantedCriminal(
                id=4,
                name="Jaxson Miller",
                nickname="Plasma Jack",
                reward=45000.0,
                last_known_coordinates="Mars Cydonia Bazaar (Block 14-C)",
                difficulty=5,
                armed=True,
                has_crew=False,
                escape_master=False,
            ),
            WantedCriminal(
                id=5,
                name="Corinne Dubois",
                nickname="Viper Queen",
                reward=120000.0,
                last_known_coordinates="Europa Sub-ice Colony (-3.882, -45.109)",
                difficulty=8,
                armed=True,
                has_crew=True,
                escape_master=False,
            ),
            WantedCriminal(
                id=6,
                name="Talon Rhyse",
                nickname="Rumble",
                reward=18000.0,
                last_known_coordinates="Titan Hydrocarbon Docks (Platform 3)",
                difficulty=3,
                armed=False,
                has_crew=True,
                escape_master=False,
            ),
            WantedCriminal(
                id=7,
                name=None,
                nickname="Nebula Phantom",
                reward=320000.0,
                last_known_coordinates="Orion Nebula Smuggler Corridor (Hyperlane 4)",
                difficulty=10,
                armed=True,
                has_crew=True,
                escape_master=True,
            ),
        ]

        for c in criminals:
            existing = session.get(WantedCriminal, c.id)
            if not existing:
                session.add(c)
        session.commit()

        print("Seeding bounty hunting journal logs...")
        now = datetime.now(timezone.utc)
        hunt_logs = [
            HuntLog(
                id=1,
                criminal_id=1,
                success=False,
                notes="Ambushed his convoy near Kepler-22b. Target deployed seismic charges and jumped into hyperspace.",
                created_at=now - timedelta(days=14),
            ),
            HuntLog(
                id=2,
                criminal_id=1,
                success=False,
                notes="Cornered in asteroid belt. Escort cruisers returned heavy plasma fire forcing tactical retreat.",
                created_at=now - timedelta(days=12),
            ),
            HuntLog(
                id=3,
                criminal_id=2,
                success=False,
                notes="Detected thermal signature on Ganymede. She hacked docking locks and vented the atmospheric seal.",
                created_at=now - timedelta(days=10),
            ),
            HuntLog(
                id=4,
                criminal_id=2,
                success=True,
                notes="Tracked disguised transport to Io orbit. EMP blast disabled her engines; target placed in cryo-stasis.",
                created_at=now - timedelta(days=9),
            ),
            HuntLog(
                id=5,
                criminal_id=3,
                success=False,
                notes="Traced quantum comms to Kuiper Belt. Raven used a decoy drone with mirrored transponder signature.",
                created_at=now - timedelta(days=8),
            ),
            HuntLog(
                id=6,
                criminal_id=3,
                success=False,
                notes="Heavy laser firefight inside ice tunnels. Target escaped through emergency decompression chute.",
                created_at=now - timedelta(days=7),
            ),
            HuntLog(
                id=7,
                criminal_id=4,
                success=True,
                notes="Intercepted during illegal arms exchange at Mars Cydonia Bazaar. Captured without collateral damage.",
                created_at=now - timedelta(days=6),
            ),
            HuntLog(
                id=8,
                criminal_id=5,
                success=False,
                notes="Sub-ice submarine encounter on Europa. Target released neurotoxin cloud into ventilation.",
                created_at=now - timedelta(days=5),
            ),
            HuntLog(
                id=9,
                criminal_id=5,
                success=False,
                notes="Syndicate reinforcements arrived via stealth corvette before capture protocol could complete.",
                created_at=now - timedelta(days=4),
            ),
            HuntLog(
                id=10,
                criminal_id=6,
                success=True,
                notes="Apprehended at Titan fuel depot after sabotaging his crew's thruster manifold.",
                created_at=now - timedelta(days=3),
            ),
            HuntLog(
                id=11,
                criminal_id=7,
                success=False,
                notes="Target jammed sensor array using pulsar radiation interference and vanished from radar.",
                created_at=now - timedelta(days=2),
            ),
            HuntLog(
                id=12,
                criminal_id=7,
                success=False,
                notes="Long-range pursuit through Orion Nebula dust clouds; lost contact due to ionic storm.",
                created_at=now - timedelta(days=1),
            ),
            HuntLog(
                id=13,
                criminal_id=4,
                success=False,
                notes="Earlier attempt on Phobos: Jack detonated an ammo crate, causing brief distraction and escaped.",
                created_at=now - timedelta(hours=18),
            ),
            HuntLog(
                id=14,
                criminal_id=1,
                success=False,
                notes="Spotted at a neutral refueling station on Ceres; escaped on an unregistered smuggling skiff.",
                created_at=now - timedelta(hours=6),
            ),
        ]

        for hl in hunt_logs:
            existing_hl = session.get(HuntLog, hl.id)
            if not existing_hl:
                session.add(hl)
        session.commit()
        print("Database successfully seeded with 7 criminals and 14 hunt logs!")

    except Exception as exc:
        session.rollback()
        print(f"Error during seeding: {exc}", file=sys.stderr)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
