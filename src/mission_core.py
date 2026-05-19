import os
import uuid
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml

MISSIONS_DIR = Path("missions")
MISSIONS_DIR_ENV = "MISSION_RECORDER_DIR"


@dataclass(frozen=True)
class MissionConfig:
    missions_dir: Path = MISSIONS_DIR

    @classmethod
    def from_env(cls) -> "MissionConfig":
        missions_dir = os.environ.get(MISSIONS_DIR_ENV)

        if missions_dir:
            return cls(Path(missions_dir))

        return cls()

    def mission_dir(self, mission_id: str) -> Path:
        return self.missions_dir / mission_id

    def mission_file(self, mission_id: str) -> Path:
        return self.mission_dir(mission_id) / "mission.yaml"


def get_config(config: Optional[MissionConfig] = None) -> MissionConfig:
    return config or MissionConfig.from_env()

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

    text = re.sub(r"['`]", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)

    text = re.sub(r"-+", "-", text)

    return text.strip("-") or "mission"


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
def get_mission_path(
    mission_id: str,
    config: Optional[MissionConfig] = None,
) -> Path:
    return get_config(config).mission_file(mission_id)


def generate_unique_mission_id(
    base_id: str,
    config: Optional[MissionConfig] = None,
) -> str:
    config = get_config(config)
    mission_id = base_id
    counter = 2

    while config.mission_dir(mission_id).exists():
        mission_id = f"{base_id}-{counter}"
        counter += 1

    return mission_id


def save_mission(
    mission_data: dict,
    config: Optional[MissionConfig] = None,
):
    config = get_config(config)
    mission_id = mission_data.get("id")

    if not mission_id:
        raise ValueError("Mission is missing id")

    mission_dir = config.mission_dir(mission_id)
    mission_dir.mkdir(parents=True, exist_ok=True)

    mission_path = get_mission_path(mission_id, config)

    with open(mission_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            mission_data,
            f,
            sort_keys=False,
            allow_unicode=True,
        )


def find_mission(
    mission_id: str,
    config: Optional[MissionConfig] = None,
) -> dict:
    mission_path = get_mission_path(mission_id, config)

    if not mission_path.exists():
        raise FileNotFoundError(f"Mission not found: {mission_id}")

    return load_mission(mission_path)


def update_mission(
    mission_id: str,
    updates: dict,
    config: Optional[MissionConfig] = None,
) -> dict:
    config = get_config(config)
    mission = find_mission(mission_id, config)

    for key, value in updates.items():
        if value is not None:
            mission[key] = value

    save_mission(mission, config)

    return mission


def create_mission_data(
    title: str,
    mission_type: str,
    status: str,
    location: str,
    tags: list[str],
    config: Optional[MissionConfig] = None,
):
    config = get_config(config)
    now = datetime.now(timezone.utc)

    slug = slugify(title)

    base_id = f"{now.strftime('%Y-%m-%d')}-{slug}"
    mission_id = generate_unique_mission_id(base_id, config)

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
