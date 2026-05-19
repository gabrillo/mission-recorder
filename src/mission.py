import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

from mission_core import (
    create_mission_data,
    find_mission,
    load_mission,
    save_mission,
    update_mission,
)

app = typer.Typer()
console = Console()


@app.command()
def new():
    """
    Crea una nuova missione
    """

    title = typer.prompt("Titolo")

    if not title.strip():
        console.print("[red]Il titolo non può essere vuoto[/red]")
        raise typer.Exit(code=1)

    mission_type = typer.prompt(
        "Tipo",
        default="generic"
    )

    status = typer.prompt(
        "Status",
        default="planned"
    )

    location = typer.prompt(
        "Location",
        default=""
    )

    tags_raw = typer.prompt(
        "Tags (separate da virgola)",
        default=""
    )

    tags = [
        tag.strip()
        for tag in tags_raw.split(",")
        if tag.strip()
    ]

    mission_data = create_mission_data(
        title=title,
        mission_type=mission_type,
        status=status,
        location=location,
        tags=tags,
    )

    mission_path = Path("missions") / mission_data["id"]

    mission_path.mkdir(parents=True, exist_ok=True)
    (mission_path / "media").mkdir(exist_ok=True)

    save_mission(mission_data)

    with open(mission_path / "notes.md", "w", encoding="utf-8") as f:
        f.write(f"# {title}\n")

    console.print(
        f"[green]Missione creata:[/green] {mission_data['id']}"
    )


@app.command(name="list")
def list_missions():
    """
    Elenca le missioni
    """

    missions_dir = Path("missions")

    if not missions_dir.exists():
        console.print("[red]Nessuna missione trovata[/red]")
        return

    table = Table(title="Missioni")

    table.add_column("ID", style="cyan")
    table.add_column("Data")
    table.add_column("Titolo")
    table.add_column("Tipo")
    table.add_column("Status")

    for mission_dir in sorted(missions_dir.iterdir()):

        mission_file = mission_dir / "mission.yaml"

        if not mission_file.exists():
            continue

        try:
            mission = load_mission(mission_file)
        except Exception as e:
            console.print(
                f"[red]Errore caricando {mission_file.name}:[/red] {e}"
            )
            continue

        table.add_row(
            str(mission.get("id") or "-"),
            str(mission.get("date") or "-"),
            str(mission.get("title") or "Untitled"),
            str(mission.get("type") or "generic"),
            str(mission.get("status") or "unknown"),
        )

    console.print(table)


# New show command
@app.command()
def show(mission_id: str):
    """
    Mostra i dettagli di una missione
    """

    mission_path = Path("missions") / mission_id

    try:
        mission_data = find_mission(mission_id)
    except FileNotFoundError:
        console.print(f"[red]Missione non trovata:[/red] {mission_id}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Errore caricando missione:[/red] {e}")
        raise typer.Exit(code=1)

    table = Table(title=f"Missione: {mission_id}")

    table.add_column("Campo", style="cyan")
    table.add_column("Valore", style="white")

    for key, value in mission_data.items():
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value)

        if value in [None, ""]:
            value = "-"

        table.add_row(str(key), str(value))

    console.print(table)

    console.print(f"\n[bold]Path:[/bold] {mission_path}")

    files = sorted([p.name for p in mission_path.iterdir()])

    console.print("\n[bold]File presenti:[/bold]")

    for file_name in files:
        console.print(f" - {file_name}")


@app.command()
def edit(
    mission_id: str,
    title: str = typer.Option(None),
    status: str = typer.Option(None),
    mission_type: str = typer.Option(None, "--type"),
    location: str = typer.Option(None),
    notes: str = typer.Option(None),
):
    """
    Modifica una missione esistente
    """

    updates = {
        "title": title,
        "status": status,
        "type": mission_type,
        "location": location,
        "notes": notes,
    }

    updates = {
        key: value
        for key, value in updates.items()
        if value is not None
    }

    if not updates:
        console.print("[yellow]Nessun campo da aggiornare[/yellow]")
        raise typer.Exit(code=1)

    try:
        mission = update_mission(mission_id, updates)
    except FileNotFoundError:
        console.print(f"[red]Missione non trovata:[/red] {mission_id}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Errore aggiornando missione:[/red] {e}")
        raise typer.Exit(code=1)

    console.print(
        f"[green]Missione aggiornata:[/green] {mission['id']}"
    )


def main():
    app()


if __name__ == "__main__":
    main()
