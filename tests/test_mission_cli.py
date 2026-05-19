import yaml
from typer.testing import CliRunner

import mission
import mission_core


runner = CliRunner()


def test_help_shows_create_as_canonical_command():
    result = runner.invoke(mission.app, ["--help"])

    assert result.exit_code == 0
    assert "create" in result.output
    assert "list" in result.output
    assert "search" in result.output
    assert "show" in result.output
    assert "edit" in result.output
    assert "new" not in result.output


def test_list_help_shows_filter_options():
    result = runner.invoke(mission.app, ["list", "--help"])

    assert result.exit_code == 0
    assert "--query" in result.output
    assert "--status" in result.output
    assert "--type" in result.output
    assert "--tag" in result.output
    assert "--location" in result.output
    assert "--date" in result.output


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


def test_list_command_filters_missions(tmp_path):
    missions_dir = tmp_path / "missions"
    config = mission_core.MissionConfig(missions_dir)

    mission_core.save_mission(
        {
            "id": "2026-05-19-alpha",
            "uuid": "uuid-1",
            "title": "Alpha",
            "type": "field",
            "status": "planned",
            "created_at": "2026-05-19T10:00:00+00:00",
            "date": "2026-05-19",
            "location": "Base Nord",
            "tags": ["radio"],
            "gear": [],
            "notes": "",
        },
        config,
    )
    mission_core.save_mission(
        {
            "id": "2026-05-20-beta",
            "uuid": "uuid-2",
            "title": "Beta",
            "type": "survey",
            "status": "done",
            "created_at": "2026-05-20T10:00:00+00:00",
            "date": "2026-05-20",
            "location": "Valle",
            "tags": ["photo"],
            "gear": [],
            "notes": "",
        },
        config,
    )

    result = runner.invoke(
        mission.app,
        ["list", "--missions-dir", str(missions_dir), "--status", "done"],
    )

    assert result.exit_code == 0
    assert "2026-05-20-beta" in result.output
    assert "2026-05-19-alpha" not in result.output


def test_search_command_searches_text_and_filters(tmp_path):
    missions_dir = tmp_path / "missions"
    config = mission_core.MissionConfig(missions_dir)

    mission_core.save_mission(
        {
            "id": "2026-05-19-radio",
            "uuid": "uuid-1",
            "title": "Radio Check",
            "type": "field",
            "status": "planned",
            "created_at": "2026-05-19T10:00:00+00:00",
            "date": "2026-05-19",
            "location": "Base",
            "tags": ["radio"],
            "gear": ["antenna"],
            "notes": "Repeater signal",
        },
        config,
    )
    mission_core.save_mission(
        {
            "id": "2026-05-20-photo",
            "uuid": "uuid-2",
            "title": "Photo Survey",
            "type": "survey",
            "status": "done",
            "created_at": "2026-05-20T10:00:00+00:00",
            "date": "2026-05-20",
            "location": "Valle",
            "tags": ["photo"],
            "gear": ["camera"],
            "notes": "",
        },
        config,
    )

    result = runner.invoke(
        mission.app,
        ["search", "repeater", "--missions-dir", str(missions_dir), "--tag", "radio"],
    )

    assert result.exit_code == 0
    assert "2026-05-19-radio" in result.output
    assert "2026-05-20-photo" not in result.output
