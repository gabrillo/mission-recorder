import uuid
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import yaml

MISSIONS_DIR = Path("missions")

DEFAULT_MISSION = {
    "id": "",
    "uuid": "",
    "title": "Untitled",
    "type": "generic",
    "status": "unknown",
    "created_at": "",
    "date": "",
    "location": "",
    "tags": [],
    "gear": [],
    "notes": "",
}



def slugify(text: str) -> str:
    text = text.strip().lower()

    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")

    text = re.sub(r"[^a-z0-9]+", "-", text)

    text = re.sub(r"-+", "-", text)

    return text.strip("-")


def load_mission(mission_file: Path) -> dict:
    with open(mission_file, "r", encoding="utf-8") as f:
        raw_data = yaml.safe_load(f) or {}

    mission = DEFAULT_MISSION.copy()
    mission.update(raw_data)

    if not isinstance(mission.get("tags"), list):
        mission["tags"] = []

    if not isinstance(mission.get("gear"), list):
        mission["gear"] = []

    return mission


# Persistence and lookup helpers
def get_mission_path(mission_id: str) -> Path:
    return MISSIONS_DIR / mission_id / "mission.yaml"

def generate_unique_mission_id(base_id: str) -> str:
    mission_id = base_id
    counter = 2

    while (MISSIONS_DIR / mission_id).exists():
        mission_id = f"{base_id}-{counter}"
        counter += 1

    return mission_id


def save_mission(mission_data: dict):
    mission_id = mission_data.get("id")

    if not mission_id:
        raise ValueError("Mission is missing id")

    mission_dir = MISSIONS_DIR / mission_id
    mission_dir.mkdir(parents=True, exist_ok=True)

    mission_path = get_mission_path(mission_id)

    with open(mission_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            mission_data,
            f,
            sort_keys=False,
            allow_unicode=True,
        )


def find_mission(mission_id: str) -> dict:
    mission_path = get_mission_path(mission_id)

    if not mission_path.exists():
        raise FileNotFoundError(f"Mission not found: {mission_id}")

    return load_mission(mission_path)


def update_mission(mission_id: str, updates: dict) -> dict:
    mission = find_mission(mission_id)

    for key, value in updates.items():
        if value is not None:
            mission[key] = value

    save_mission(mission)

    return mission


def create_mission_data(
    title: str,
    mission_type: str,
    status: str,
    location: str,
    tags: list[str],
):
    now = datetime.now(timezone.utc)

    slug = slugify(title)

    base_id = f"{now.strftime('%Y-%m-%d')}-{slug}"
    mission_id = generate_unique_mission_id(base_id)

    return {
        "id": mission_id,
        "uuid": str(uuid.uuid4()),
        "title": title,
        "type": mission_type,
        "status": status,
        "created_at": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "location": location,
        "tags": tags,
        "gear": [],
        "notes": "",
    }
