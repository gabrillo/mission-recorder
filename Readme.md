# Mission Recorder - Project State & Workflow Summary

## Project Overview

`mission-recorder` is a CLI-based mission logging system designed around structured YAML missions stored on disk.

The project currently focuses on:

- Stable mission creation
- Safe mission IDs and filesystem handling
- Consistent persistence
- Human-readable storage
- CLI usability
- Future extensibility

The architecture is intentionally simple:

- One directory per mission
- One `mission.yaml` file per mission
- Pure filesystem persistence
- No database

---

# Development Setup

Install the project and development dependencies into the local virtual environment:

```bash
.venv/bin/python -m pip install '.[dev]'
```

Run the CLI:

```bash
.venv/bin/mission-recorder --help
```

Create a mission:

```bash
.venv/bin/mission-recorder create
```

List missions:

```bash
.venv/bin/mission-recorder list
```

Filter missions:

```bash
.venv/bin/mission-recorder list --status planned --tag radio
```

Search missions:

```bash
.venv/bin/mission-recorder search repeater
```

Use a custom missions directory with either an option:

```bash
.venv/bin/mission-recorder list --missions-dir /path/to/missions
```

Or an environment variable:

```bash
MISSION_RECORDER_DIR=/path/to/missions .venv/bin/mission-recorder list
```

Run tests:

```bash
.venv/bin/python -m pytest
```

---

# Current Workflow

## Mission Creation Flow

1. User creates a mission from CLI
2. Mission title is normalized through `slugify()`
3. A date-prefixed mission ID is generated
4. Collision detection ensures uniqueness
5. A mission directory is created
6. `mission.yaml` is written inside the mission directory

Example structure:

```text
missions/
└── 2026-05-19-test-mission/
    └── mission.yaml
```

---

# ID Generation Workflow

## Current Strategy

Mission IDs are generated using:

```text
YYYY-MM-DD-slugified-title
```

Example:

```text
2026-05-19-night-flight
```

If the same title already exists on the same date:

```text
2026-05-19-night-flight-2
2026-05-19-night-flight-3
```

Collision handling is managed by:

```python
generate_unique_mission_id()
```

---

# Apostrophe / Shell Problem

A major issue discovered during development:

Mission IDs containing shell-breaking characters, especially apostrophes (`'`), caused CLI and shell issues.

Example problematic title:

```text
L'escursione radio
```

This led to invalid or annoying shell escaping behavior.

## Solution Implemented

The project now sanitizes IDs through:

```python
slugify()
```

Which:

- Lowercases text
- Strips accents
- Removes unicode
- Replaces invalid characters
- Collapses repeated separators

Result:

```text
L'escursione radio

lescursione-radio
```

This completely avoids shell escaping problems.

---

# Persistence Model

Each mission contains:

```yaml
id:
uuid:
title:
type:
status:
created_at:
date:
location:
tags:
gear:
notes:
```

Defaults are centralized in:

```python
DEFAULT_MISSION
```

---

# Current Project State

## Implemented

### Core Persistence

- Mission loading
- Mission saving
- Mission lookup
- Mission updating

### Filesystem Layout

- Directory-per-mission structure
- Automatic directory creation

### ID Safety

- Slug sanitization
- Collision handling
- Stable date-prefixed IDs

### YAML Handling

- UTF-8 safe
- Unicode-safe dumps
- Ordered keys

### Validation

- Safe fallback defaults
- List normalization for:
  - `tags`
  - `gear`

---

# CLI State

The CLI already supports:

- `create`
- `list`
- `show`
- update/edit related flows

Several rendering/formatting issues were fixed during development, including:

- Empty fields in mission tables
- Malformed rendering
- Incorrect mission listing behavior after migration

---

# Important Development Decisions

## Why Folder-Based Missions

Instead of:

```text
missions/*.yaml
```

The project uses:

```text
missions/<mission-id>/mission.yaml
```

Advantages:

- Future attachments support
- Logs
- Images
- GPS tracks
- Recordings
- Easier exports

---

# Current Core File Edited

## `/src/mission_core.py`

This is currently the main persistence/business-logic layer.

### Functions Present

#### `slugify(text)`

Normalizes titles into shell-safe IDs.

#### `load_mission(mission_file)`

Loads YAML safely and applies defaults.

#### `get_mission_path(mission_id)`

Returns `mission.yaml` path.

#### `generate_unique_mission_id(base_id)`

Handles ID collisions.

#### `save_mission(mission_data)`

Persists mission to disk.

#### `find_mission(mission_id)`

Loads a mission by ID.

#### `update_mission(mission_id, updates)`

Applies updates and saves.

#### `create_mission_data(...)`

Creates a complete mission structure.

---

# Exact Files Edited During This Workflow

## Main Files

### `src/mission.py`

CLI logic and Rich rendering.

Worked on:

- Mission listing
- Show command
- Formatting fixes
- Rendering cleanup

### `src/mission_core.py`

Core persistence and mission management.

Worked on:

- Slug sanitization
- Collision handling
- Mission loading/saving
- Update logic
- Filesystem abstraction

---

# Current Architecture

```text
CLI
 ↓
mission.py
 ↓
mission_core.py
 ↓
filesystem + YAML
```

---

# Current Stability Status

## Working Correctly

- Mission creation
- Mission persistence
- Duplicate title handling
- Apostrophe-safe mission IDs
- Mission listing
- Mission retrieval
- YAML serialization

## Remaining Future Areas

Potential future improvements:

- Schema validation
- Attachments support
- Search/filtering
- Export/import
- Markdown mission reports
- Tag querying
- Gear inventory integration
- GPS/track support
- Rich TUI
- Tests

---

# Suggested Next Development Priorities

1. Add validation layer
2. Add automated tests
3. Improve CLI UX
4. Add mission attachments
5. Add filtering/search
6. Add schema versioning
7. Add backup/export support

---

# Repository Positioning

The project is evolving into:

> A lightweight filesystem-native operational logbook / mission recorder system.

It already has a solid persistence foundation and the dangerous ID/shell edge cases have been addressed properly.
