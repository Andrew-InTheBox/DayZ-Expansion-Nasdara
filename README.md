# DayZ Nasdara with Expansion

This sibling server was copied from `DayZServerChernaTrader`. Run
`start_autoMods.bat` from this folder to use `serverDZ.cfg` and mission
`mpmissions/expansion.nasdara`. The starter launcher uses port 2402 so it does
not collide with the Chernarus server's port 2302.

The starter launcher loads CF, DabsFramework, and the core DayZ Expansion
modules. The other installed mods were copied but are not loaded until their
missions and map-specific settings are reviewed for Nasdara. The launcher
does not load the Chernarus Heatmap server mod.

The active `config/` profile starts empty and will be populated by the server
and mods on first run. The old profile is retained in
`chernarus_config_reference/` for adapting settings later. Do not move its
traders, patrols, quests, markers, or other coordinates into `config/` without
replacing them with Nasdara locations.

The mission's `SETUP_NOTES.md` explains its vanilla Nasdara files and Expansion
economy additions. Expansion vehicle events and map-placed content still need
Nasdara coordinates. The first server launch has not been tested.

Workshop and server updates are disabled in `.env` for the first launch. Enable
them there after verifying the copied files and update paths.
