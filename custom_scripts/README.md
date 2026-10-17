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
