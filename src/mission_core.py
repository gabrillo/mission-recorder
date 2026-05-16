import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml

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
    return (
        text.strip()
        .lower()
        .replace(" ", "-")
        .replace("/", "-")
    )


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


def create_mission_data(
    title: str,
    mission_type: str,
    status: str,
    location: str,
    tags: list[str],
):
    now = datetime.now(timezone.utc)

    slug = slugify(title)

    mission_id = f"{now.strftime('%Y-%m-%d')}-{slug}"

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
