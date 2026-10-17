# Expansion Nasdara mission starter

This mission starts from Bohemia's `dayzOffline.nasdara` files. All vanilla Nasdara
economy, spawn, event, environment, underground, and map data remains in place.
The original Nasdara `init.c` also remains in place, including its starter clothing
and April 30 date reset.

Expansion additions:

- `cfgeconomycore.xml` loads `expansion_ce/expansion_types.xml` and
  `expansion_ce/expansion_spawnabletypes.xml` from the Chernarus Expansion setup.
- `expansion/settings/MapSettings.json` keeps the existing map settings, with all
  Chernarus server markers removed.
- `expansion/settings/SpawnSettings.json` disables Expansion spawn selection and
  its starter gear, leaving Nasdara's vanilla spawn points and `init.c` loadout
  in control. Its Chernarus spawn locations have been removed.

No Expansion vehicle events are registered yet. The Chernarus events use fixed
spawn positions, and copying them would place vehicles at unrelated Nasdara
coordinates. To add them, define Nasdara positions in `cfgeventspawns.xml`,
then add the matching `expansion_events.xml` to this mission's `expansion_ce/`
and register it in `cfgeconomycore.xml`.

Expansion AI patrols, airdrops, traders, quests, custom objects, and trader zones
also need Nasdara locations before they can be enabled. Expansion can generate
its other settings on first server start. Configure the server to load mission
template `expansion.nasdara` with the required Expansion mods.

The sibling server folder currently contains only this mission. Server binaries,
mod files, keys, and a `serverDZ.cfg` are still needed before it can launch.
