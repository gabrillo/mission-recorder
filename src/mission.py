from pathlib import Path
from datetime import datetime, timezone
import typer
import yaml
import uuid
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

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
    now = datetime.now(timezone.utc)

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


@app.command(name="list")
def list_missions():
    """
    Elenca le missioni
    """

    if not MISSIONS_DIR.exists():
        console.print("[red]Nessuna missione trovata[/red]")
        return

    table = Table(title="Missioni")

    table.add_column("Mission ID", style="cyan")

    for mission in sorted(MISSIONS_DIR.iterdir()):
        if mission.is_dir():
            table.add_row(mission.name)

    console.print(table)


# New show command
@app.command()
def show(mission_id: str):
    """
    Mostra i dettagli di una missione
    """

    mission_path = MISSIONS_DIR / mission_id

    if not mission_path.exists():
        console.print(f"[red]Missione non trovata:[/red] {mission_id}")
        raise typer.Exit(code=1)

    yaml_path = mission_path / "mission.yaml"

    if not yaml_path.exists():
        console.print("[red]mission.yaml mancante[/red]")
        raise typer.Exit(code=1)

    with open(yaml_path, "r") as f:
        mission_data = yaml.safe_load(f)

    table = Table(title=f"Missione: {mission_id}")

    table.add_column("Campo", style="green")
    table.add_column("Valore", style="white")

    for key, value in mission_data.items():
        if isinstance(value, list):
            value = ", ".join(value)

        table.add_row(str(key), str(value))

    console.print(table)

    console.print(f"\n[cyan]Path:[/cyan] {mission_path}")

    files = [p.name for p in mission_path.iterdir()]

    console.print("\n[yellow]File presenti:[/yellow]")

    for file_name in sorted(files):
        console.print(f" - {file_name}")


if __name__ == "__main__":
    app()