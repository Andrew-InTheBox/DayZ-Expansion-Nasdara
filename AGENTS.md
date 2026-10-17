# Nasdara server setup

The active mission is `mpmissions/expansion.nasdara`. It derives from Bohemia's
`dayzOffline.nasdara` mission. Its `SETUP_NOTES.md` records the Expansion changes.

The active profile is `config/`. `chernarus_config_reference/` is an inactive
copy of the previous server profile. Check all coordinates, patrols, traders,
events, and quest locations against Nasdara before migrating its settings.

The launcher is `start_autoMods.bat`, and `serverDZ.cfg` loads
`expansion.nasdara`. The launcher currently loads the core Expansion stack.
Other copied mods are available but are not enabled in its mod list.

The official vanilla source is:
`C:\Users\andre\OneDrive\Documents\DayZ Official Mission Files\bohemia_repo_official\DayZ-Central-Economy\dayzOffline.nasdara`

For large XML and JSON files, search relevant sections or use a Python script.
Use `C:\Users\andre\venv-dirs\venv-utils` for Python scripts.
