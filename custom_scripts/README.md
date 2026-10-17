# Custom Scripts

Helper scripts are grouped by the kind of DayZ server configuration work they support. Each script category has an `output/` directory for generated reports, CSVs, plots, or transformed files.

## Folders

- `ai_patrols/`: AI patrol/location settings builders, reports, and map plots.
- `animals/`: Animal territory spawn-zone map plots.
- `roamers/`: Roamer heatmap, log, and animation plotting tools.
- `loadouts/`: Expansion loadout analysis and loadout mutation helpers.
- `market/`: Expansion market JSON pricing, threshold, and item helpers.
- `loot_types/`: `types.xml`, tier, nominal/minimum, and vehicle-spawn analysis helpers.
- `vehicles/`: Vehicle event spawn parsing and map plotting tools.
- `player_spawns/`: Player spawn bubble plotting tools.
- `quests/`: Quest/NPC/objective analysis reports.
- `docs/`: Documentation scraping helpers.
- `maintenance/`: Broad server config maintenance and validation scripts.
- `assets/`: Shared static assets used by scripts, such as map background images.

Run Python scripts with `C:\Users\andre\venv-dirs\venv-utils\Scripts\python.exe` from the repo root unless a script says otherwise.

## Nasdara setup

These 56 Python helpers were copied from the Chernarus server's `custom_scripts/`
folder. Mission defaults now use this server's `mpmissions/expansion.nasdara`;
profile defaults use this server's `config/`. Paths derive from script locations,
including helpers that previously depended on the working directory. Explicit
command-line input paths still select the files supplied by the operator.

The plotters use `assets/nasdara-map-background.png`, copied from
`C:\Users\andre\Downloads\Nasdara Mountain Valley Topographic Map.png`.
Shared image bounds are in `assets/nasdara-map-settings.json`: X and Z both run
from 0 to 16384 metres, using the world size supplied by the server owner. The
rectangular image is mapped to that full square; exact landmark alignment has
not been independently verified. Adjust the shared bounds if the image is a crop.
Chernarus-specific 32 metre plot offsets have been removed.

The vehicle helpers use Nasdara's `db/events.xml`; this mission does not currently
include Expansion vehicle events. The vehicle plotter tolerates the absent
Expansion event file. The player spawn plotter supports Nasdara's grouped `<pos>`
entries as well as ungrouped entries.

Some helpers are historical, mod-specific editing recipes. Copying them does not
enable mods or migrate their settings. Inputs absent from this setup still need
to be provided before those helpers can run, including RF heli definitions,
SNAFU keep lists/bare-types variants, MMG ATACS definitions, and the AI location
builder's `docs/ai-locations-input.txt` / `docs/ai-locations-no-go-inputs.txt`.
`ai_patrols/add_roamers.txt` contains Livonia locations, not Nasdara locations;
`add_roaming_patrols.py` therefore requires an explicit `--roamers` input file
whose locations have been checked for Nasdara.

Validation during copying: all Python files compiled; the vehicle analysis
helper completed against the local mission; vehicle and player spawn plots were
checked using temporary outputs. Configuration-editing helpers were not run.
The vehicle nominal/minimum report retains its original policy checks; its
flags for zero vehicle values in `types.xml` do not establish a server fault
(vehicles are also controlled by event definitions).

## Nasdara AI patrol plots and HTML reports

From the server root, using the Python venv above:

```powershell
python custom_scripts/ai_patrols/plot_ai_patrols.py --html
python custom_scripts/ai_patrols/plot_ai_patrols.py --no-patrol-labels --output custom_scripts/ai_patrols/output/nasdara_ai_patrols.png
python custom_scripts/ai_patrols/generate_ai_patrol_report.py
```

`--html` writes `custom_scripts/ai_patrols/output/ai_patrol_explorer.html`.
Open that generated file, or use `custom_scripts/ai_patrols/ai_patrol_explorer.html`,
which redirects to it. The generator uses `ai_patrol_explorer.template.html`;
that template is not a standalone viewer. The generated viewer embeds both the
patrol data and `assets/nasdara-map-background.png`, so it needs no separate data
files or web server. Regenerate it after changing the patrol settings.
The HTML embeds its data and background image and opens offline in a browser.
Regenerate it after changing server settings; it is a configuration snapshot.
Search and filter by behavior, spawn source, faction, or effective category.
Select any definition, including unmapped ones, to inspect persistence, loadout,
chance, AI count settings, raw JSON and effective inherited settings. The player
count control previews category and global caps for 0–10 players; it does not
change the server. Both PNG and HTML support `--exclude-behaviour`, and focus
arguments (`--focus-region`, or `--focus-center` with optional `--focus-size`).
Other inputs can be supplied with `--input`, `--ai-settings`, `--locations`,
`--map-settings`, and `--background`. `--locations-only` shows roaming locations
and no-go areas without patrols. The separate location plotter remains available.

Interpret map markers as configuration data, not live bots:

- Circles are world-coordinate waypoints or possible roaming starts. `ROAMING`
  is not drawn as a fixed route through every listed waypoint.
- Squares are potential building/area centers or event candidate sites from
  the mission's `mapgrouppos.xml`, `cfgEffectArea.json`, and active event
  definitions paired with `cfgeventspawns.xml`. Local object offsets are kept
  in the details and are never plotted at the world origin. Building orientation
  and relative offsets are not transformed into exact AI spawn positions.
- The roster counts patrol definitions separately from mapped starts/anchors.
  Map groups are an incomplete object inventory; dynamic events are not live
  events. An unmapped definition is not proof that the class is absent in game.
- Map bounds retain the supplied 16384 m world square. The rectangular raster's
  exact landmark alignment remains unverified; shared bounds can be adjusted.

The matrix report now groups by spawn source and behavior instead of name
prefixes, includes persistence/chance, effective noise and respawn values with
inheritance sources, mapped anchor counts, and load-balancing caps at 10 players.
`RespawnTime: -1` means disabled; `-2` inherits the patrol global setting. Normal
inherited settings such as noise use `-1`, including fallback to `AISettings`.
No plotting/report command edits server configuration.

Regression checks:

```powershell
python -m unittest discover -s custom_scripts/ai_patrols -p 'test_*.py'
```
