from pathlib import Path
from datetime import datetime, UTC
import typer
import yaml
import uuid

app = typer.Typer()

MISSIONS_DIR = Path("missions")


@app.command()
def new():
    """
    Crea una nuova missione
    """

    title = input("Titolo missione: ")
    mission_type = input("Tipo missione: ")
    tags = input("Tag separati da virgola: ")

    # Timestamp UTC
    now = datetime.now(UTC)

    # Nome cartella
    date_str = now.strftime("%Y-%m-%d")
    slug = title.lower().replace(" ", "-")

    mission_id = f"{date_str}-{mission_type}-{slug}"

    mission_path = MISSIONS_DIR / mission_id

    # Crea cartelle
    mission_path.mkdir(parents=True, exist_ok=True)
    (mission_path / "media").mkdir(exist_ok=True)

    # Dati YAML
    mission_uuid = str(uuid.uuid4())
    mission_data = {
        "id": mission_id,
        "uuid": mission_uuid,
        "title": title,
        "type": mission_type,
        "created_at": now.isoformat(),
        "tags": [tag.strip() for tag in tags.split(",") if tag.strip()]
    }

    # Scrive mission.yaml
    with open(mission_path / "mission.yaml", "w") as f:
        yaml.dump(mission_data, f, sort_keys=False)

    # Crea notes.md
    with open(mission_path / "notes.md", "w") as f:
        f.write(f"# {title}\n\n")

    print(f"\nMissione creata: {mission_id}")


@app.command()
def list():
    """
    Elenca le missioni
    """

    if not MISSIONS_DIR.exists():
        print("Nessuna missione trovata")
        return

    for mission in sorted(MISSIONS_DIR.iterdir()):
        if mission.is_dir():
            print(mission.name)


if __name__ == "__main__":
    app()