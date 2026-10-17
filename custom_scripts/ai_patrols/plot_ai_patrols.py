"""Plot Nasdara patrol starts, potential object anchors, and AI location areas."""
import argparse
import base64
import html
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from ai_patrol_data import DEFAULT_AI, DEFAULT_MISSION, SCRIPT_DIR, build_dataset, read_json

ASSETS = SCRIPT_DIR.parent / 'assets'
COLORS = {'ROAMING': '#007d92', 'ROAMING_LOCAL': '#bf5b00', 'HALT': '#7041a6',
          'LOOP_OR_ALTERNATE': '#ba293e'}


def write_interactive_html(path, dataset, source_path, map_settings, background, initial_bounds=None,
                           player_count=10, labels=True, location_labels=False):
    """Embed all data and the background so the result works offline."""
    content = (SCRIPT_DIR / 'ai_patrol_explorer.template.html').read_text(encoding='utf-8')
    payload = dict(dataset, bounds=map_settings['background_bounds'],
                   mapNote=map_settings.get('notes', ''), initialBounds=initial_bounds,
                   playerCount=player_count, labels=labels, locationLabels=location_labels)
    encoded = json.dumps(payload, ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    image = 'data:image/png;base64,' + base64.b64encode(background.read_bytes()).decode('ascii') if background.exists() else ''
    content = content.replace('__SOURCE__', html.escape(str(source_path)))
    content = content.replace('__GENERATED__', datetime.now().astimezone().isoformat(timespec='seconds'))
    content = content.replace('__DATA__', encoded).replace('__BACKGROUND__', image)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def write_png(path, dataset, map_settings, background, args, initial_bounds):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Circle
    fig, ax = plt.subplots(figsize=(14, 11))
    bounds = map_settings['background_bounds']
    if background.exists():
        ax.imshow(plt.imread(background), extent=bounds, origin='upper')
    for area in dataset['areas']:
        color = '#b31f34' if area['kind'] == 'No-go area' else '#237941'
        ax.add_patch(Circle((area['x'], area['z']), area['radius'], fill=False, color=color, alpha=.7))
        if args.locations_only or args.label_locations:
            ax.annotate(area['name'], (area['x'], area['z']), fontsize=6)
    definitions, anchors, unmapped = 0, 0, []
    behaviours = set()
    for patrol in dataset['patrols']:
        if not patrol['points']:
            unmapped.append(patrol['name'])
            continue
        definitions += 1
        anchors += len(patrol['points'])
        behaviours.add(patrol['behaviour'])
        color = COLORS.get(patrol['behaviour'], '#333333')
        coords = [(p['x'], p['z']) for p in patrol['points']]
        xs, zs = zip(*coords)
        ax.scatter(xs, zs, c=color, marker='s' if patrol['objectClassName'] else 'o', s=18, alpha=.8)
        if not patrol['objectClassName'] and patrol['behaviour'] not in ('ROAMING', 'ROAMING_LOCAL') and len(coords) > 1:
            if patrol['behaviour'] == 'LOOP':
                xs, zs = list(xs)+[xs[0]], list(zs)+[zs[0]]
            ax.plot(xs, zs, color=color, alpha=.65)
        if not args.no_patrol_labels:
            # Label one anchor per definition rather than hundreds of repeated names.
            ax.annotate(patrol['name'], coords[0], xytext=(3, 5), textcoords='offset points', fontsize=6,
                        bbox=dict(facecolor='white', alpha=.7, edgecolor='none', pad=1))
    handles = [Line2D([], [], marker='o', linestyle='', color=COLORS.get(b, '#333'), label=b) for b in sorted(behaviours)]
    handles += [Line2D([], [], marker='s', linestyle='', color='#555', label='Potential building/event anchor'),
                Line2D([], [], color='#b31f34', label='No-go area'), Line2D([], [], color='#237941', label='Roaming location')]
    ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(1, 1), fontsize=8)
    view = initial_bounds or bounds
    ax.set_xlim(view[:2]); ax.set_ylim(view[2:]); ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('World X (m)'); ax.set_ylabel('World Z (m)')
    ax.set_title('Nasdara AI patrol starts and potential spawn anchors')
    ax.grid(alpha=.2)
    summary = f"{len(dataset['patrols'])} definitions · {definitions} mapped · {anchors} starts/anchors · {len(unmapped)} without mapped anchors"
    fig.text(.02, .035, summary, fontsize=9)
    fig.text(.02, .015, 'Configuration preview, not live AI. Roaming dots show starts; squares show object centers/candidate sites, not routes.', fontsize=8)
    fig.tight_layout(rect=(0, .055, 1, 1))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches='tight'); plt.close(fig)
    print(summary)
    if unmapped:
        print('No anchors in the supplied mission sources: ' + ', '.join(unmapped))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=DEFAULT_MISSION / 'expansion/settings/AIPatrolSettings.json')
    parser.add_argument('--ai-settings', type=Path, default=DEFAULT_AI)
    parser.add_argument('--locations', type=Path, help='Default: AILocationSettings.json next to the patrol input')
    parser.add_argument('--map-settings', type=Path, default=ASSETS / 'nasdara-map-settings.json')
    parser.add_argument('--background', type=Path, default=ASSETS / 'nasdara-map-background.png')
    parser.add_argument('--output', type=Path, help='PNG output path')
    parser.add_argument('--html', nargs='?', const=str(SCRIPT_DIR / 'output/ai_patrol_explorer.html'), type=Path)
    parser.add_argument('--players', type=int, choices=range(0, 11), default=10, help='Initial load-balancing preview player count (0-10)')
    parser.add_argument('--locations-only', action='store_true')
    parser.add_argument('--label-locations', action='store_true')
    parser.add_argument('--no-patrol-labels', action='store_true')
    parser.add_argument('--exclude-behaviour', action='append', default=[], help='Exclude from PNG and HTML (repeatable)')
    parser.add_argument('--focus-region', nargs=4, type=float, metavar=('MIN_X', 'MAX_X', 'MIN_Z', 'MAX_Z'))
    parser.add_argument('--focus-center', nargs=2, type=float, metavar=('X', 'Z'))
    parser.add_argument('--focus-size', nargs=2, type=float, metavar=('WIDTH', 'HEIGHT'))
    args = parser.parse_args()
    if args.focus_region and args.focus_center:
        parser.error('Use --focus-region or --focus-center, not both.')
    if args.focus_size and not args.focus_center:
        parser.error('--focus-size requires --focus-center.')
    if args.focus_size and any(v <= 0 for v in args.focus_size):
        parser.error('--focus-size values must be positive.')
    mission = args.input.resolve().parents[2]
    config = read_json(args.input) if not args.locations_only else {'Patrols': [], 'Enabled': 0}
    ai = read_json(args.ai_settings)
    location_path = args.locations or args.input.with_name('AILocationSettings.json')
    locations = read_json(location_path) if location_path.exists() else {}
    dataset = build_dataset(config, ai, mission, locations)
    excluded = {s.upper() for s in args.exclude_behaviour}
    dataset['patrols'] = [p for p in dataset['patrols'] if p['behaviour'].upper() not in excluded]
    settings = read_json(args.map_settings)
    bounds = settings['background_bounds']
    focus = args.focus_region
    if args.focus_center:
        x, z = args.focus_center; width, height = args.focus_size or (800, 800)
        focus = [x-width/2, x+width/2, z-height/2, z+height/2]
    for value in (bounds, focus):
        if value and (len(value) != 4 or value[0] >= value[1] or value[2] >= value[3]):
            parser.error('Map/focus bounds must have min < max on both axes.')
    if args.html:
        write_interactive_html(args.html, dataset, args.input, settings, args.background, focus, args.players,
                               not args.no_patrol_labels, args.label_locations or args.locations_only)
        print(f'Interactive map saved as: {args.html}')
    else:
        output = args.output or SCRIPT_DIR / 'output' / f"{datetime.now():%Y%m%d%H%M%S}_patrols.png"
        write_png(output, dataset, settings, args.background, args, focus)
        print(f'Plot saved as: {output}')
    print('Behaviour definitions:', dict(Counter(p['behaviour'] for p in dataset['patrols'])))


if __name__ == '__main__':
    main()
