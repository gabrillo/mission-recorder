import yaml
from typer.testing import CliRunner

import mission


runner = CliRunner()


def test_help_shows_create_as_canonical_command():
    result = runner.invoke(mission.app, ["--help"])

    assert result.exit_code == 0
    assert "create" in result.output
    assert "list" in result.output
    assert "show" in result.output
    assert "edit" in result.output
    assert "new" not in result.output


def test_create_command_writes_mission_files(tmp_path):
    missions_dir = tmp_path / "missions"

    result = runner.invoke(
        mission.app,
        ["create", "--missions-dir", str(missions_dir)],
        input="Test CLI\nfield\nplanned\nBase\nradio, test\n",
    )

    assert result.exit_code == 0
    assert "Missione creata:" in result.output

    mission_dirs = list(missions_dir.iterdir())
    assert len(mission_dirs) == 1

    mission_dir = mission_dirs[0]
    mission_file = mission_dir / "mission.yaml"

    assert mission_file.exists()
    assert (mission_dir / "notes.md").exists()
    assert (mission_dir / "media").is_dir()

    mission_data = yaml.safe_load(mission_file.read_text(encoding="utf-8"))

    assert mission_data["title"] == "Test CLI"
    assert mission_data["type"] == "field"
    assert mission_data["status"] == "planned"
    assert mission_data["location"] == "Base"
    assert mission_data["tags"] == ["radio", "test"]


def test_new_alias_still_creates_mission(tmp_path):
    missions_dir = tmp_path / "missions"

    result = runner.invoke(
        mission.app,
        ["new", "--missions-dir", str(missions_dir)],
        input="Legacy CLI\nfield\nplanned\nBase\nradio\n",
    )

    assert result.exit_code == 0
    assert "Missione creata:" in result.output
    assert len(list(missions_dir.iterdir())) == 1
