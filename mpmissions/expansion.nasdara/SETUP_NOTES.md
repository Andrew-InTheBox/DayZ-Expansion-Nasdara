# Expansion Nasdara mission starter

This mission starts from Bohemia's `dayzOffline.nasdara` files. All vanilla Nasdara
economy, spawn, event, environment, underground, and map data remains in place.
The original Nasdara `init.c` also remains in place, including its starter clothing
and April 30 date reset.

Expansion additions:

- `cfgeconomycore.xml` loads `expansion_ce/expansion_types.xml` and
  `expansion_ce/expansion_spawnabletypes.xml` from the Chernarus Expansion setup.
- `cfgeconomycore.xml` also loads the Chernarus server's SNAFU Weapons, MMG,
  and Airborne AI item XML files from `snafu/`, `db/mmg/`, and `db/airborne_ai/`.
  These files contain item economy definitions and attachment rules, with no
  Chernarus-specific positions. `start_autoMods.bat` discovers all `@` mod
  folders and all `_@` server-side mod folders at startup.
- The imported SNAFU, MMG, and Airborne AI `types` entries use Nasdara's
  `Tier1`-`Tier3` loot progression. Items that used only Chernarus `Tier4`
  now use `Tier3`; entries already using `Tier2` or `Tier3` keep those tiers.
  Weapon and gear entries with a clear faction match use `MilitaryEast` or
  `MilitaryWest`. Shared supplies retain `Military`, which Nasdara also uses.
  Admin gear and other zero-nominal items remain zero-nominal.
- The imported SNAFU file used a nonexistent generic `SNAFUGevar_Suppressor`
  class. It now uses the installed mod's `SNAFUGevar_Suppressor_Green`
  class in both the loot definition and rifle attachment rule.
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
its other settings on first server start. `serverDZ.cfg` loads mission template
`expansion.nasdara`.
