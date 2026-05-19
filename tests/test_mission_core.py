import pytest
import yaml

import mission_core


@pytest.fixture()
def config(tmp_path):
    path = tmp_path / "missions"
    return mission_core.MissionConfig(path)


def test_slugify_removes_shell_sensitive_characters():
    assert mission_core.slugify(" L'escursione radio ") == "lescursione-radio"
    assert mission_core.slugify("Volo Air 75!") == "volo-air-75"
    assert mission_core.slugify("Meteo: città & quota") == "meteo-citta-quota"


def test_slugify_uses_safe_fallback_for_empty_output():
    assert mission_core.slugify("   ") == "mission"
    assert mission_core.slugify("🚁") == "mission"


def test_config_can_be_loaded_from_environment(tmp_path, monkeypatch):
    missions_dir = tmp_path / "custom-missions"
    monkeypatch.setenv(mission_core.MISSIONS_DIR_ENV, str(missions_dir))

    config = mission_core.MissionConfig.from_env()

    assert config.missions_dir == missions_dir
    assert config.mission_file("mission-1") == missions_dir / "mission-1" / "mission.yaml"


def test_generate_unique_mission_id_adds_numeric_suffix(config):
    base_id = "2026-05-19-test"
    missions_dir = config.missions_dir
    (missions_dir / base_id).mkdir(parents=True)
    (missions_dir / f"{base_id}-2").mkdir()

    assert mission_core.generate_unique_mission_id(base_id, config) == f"{base_id}-3"


def test_save_find_and_update_mission_roundtrip(config):
    mission = {
        "id": "2026-05-19-test",
        "uuid": "uuid-1",
        "title": "Test",
        "type": "generic",
        "status": "planned",
        "created_at": "2026-05-19T10:00:00+00:00",
        "date": "2026-05-19",
        "location": "Base",
        "tags": ["radio"],
        "gear": [],
        "notes": "",
    }

    mission_core.save_mission(mission, config)

    mission_path = config.mission_file(mission["id"])
    assert mission_path.exists()
    assert mission_core.find_mission(mission["id"], config) == mission

    updated = mission_core.update_mission(
        mission["id"],
        {"status": "done", "location": None, "notes": "Completed"},
        config,
    )

    assert updated["status"] == "done"
    assert updated["location"] == "Base"
    assert updated["notes"] == "Completed"
    assert mission_core.find_mission(mission["id"], config)["status"] == "done"


def test_load_mission_applies_defaults_and_normalizes_lists(tmp_path):
    mission_file = tmp_path / "mission.yaml"
    mission_file.write_text(
        yaml.safe_dump(
            {
                "id": "mission-1",
                "title": "Partial",
                "tags": "not-a-list",
                "gear": None,
            }
        ),
        encoding="utf-8",
    )

    mission = mission_core.load_mission(mission_file)

    assert mission["id"] == "mission-1"
    assert mission["title"] == "Partial"
    assert mission["type"] == "generic"
    assert mission["status"] == "unknown"
    assert mission["tags"] == []
    assert mission["gear"] == []


def test_create_mission_data_generates_safe_unique_id(config):
    existing_id = "2026-05-19-lescursione-radio"
    missions_dir = config.missions_dir
    (missions_dir / existing_id).mkdir(parents=True)

    mission = mission_core.create_mission_data(
        title="L'escursione radio",
        mission_type="field",
        status="planned",
        location="Monte",
        tags=["radio", "test"],
        config=config,
    )

    assert mission["id"].endswith("lescursione-radio") or mission["id"].endswith(
        "lescursione-radio-2"
    )
    assert "'" not in mission["id"]
    assert mission["uuid"]
    assert mission["title"] == "L'escursione radio"
    assert mission["type"] == "field"
    assert mission["status"] == "planned"
    assert mission["location"] == "Monte"
    assert mission["tags"] == ["radio", "test"]
