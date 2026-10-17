"""Shared, read-only interpretation of Expansion patrol definitions for reports."""
from collections import defaultdict
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
DEFAULT_MISSION = ROOT / 'mpmissions' / 'expansion.nasdara'
DEFAULT_AI = ROOT / 'config' / 'ExpansionMod' / 'Settings' / 'AISettings.json'
EVENT_CLASSES = {'Wreck_UH1Y', 'Wreck_Mi8_Crashed', 'ContaminatedArea_Static', 'ContaminatedArea_Dynamic'}
INHERITED = ('AccuracyMin', 'AccuracyMax', 'ThreatDistanceLimit', 'NoiseInvestigationDistanceLimit',
             'MaxFlankingDistance', 'EnableFlankingOutsideCombat', 'DamageMultiplier',
             'DamageReceivedMultiplier', 'FormationScale', 'DespawnTime', 'MinDistRadius',
             'MaxDistRadius', 'DespawnRadius')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def category_for(patrol):
    return patrol.get('LoadBalancingCategory') or ('ObjectPatrol' if patrol.get('ObjectClassName') else 'Patrol')


def spawn_source(patrol):
    obj = patrol.get('ObjectClassName', '')
    if not obj:
        return 'World waypoints'
    if obj in EVENT_CLASSES or obj.startswith('ContaminatedArea'):
        return 'Event / area'
    return 'Building / object'


def group_for(patrol):
    return f"{spawn_source(patrol)} · {patrol.get('Behaviour', 'Unknown')}"


def effective_setting(patrol, globals_, ai, key):
    """Keep per-field sentinel semantics, especially RespawnTime -1 vs -2."""
    value = patrol.get(key)
    origin = 'Patrol override'
    sentinel = -2 if key == 'RespawnTime' else -1
    if value is None or value == sentinel:
        value, origin = globals_.get(key), 'Patrol globals'
        if key in INHERITED and (value is None or value == -1):
            value, origin = ai.get(key), 'AISettings'
    if key == 'RespawnTime' and value == -1:
        return {'value': 'Disabled', 'source': origin, 'raw': patrol.get(key)}
    if value is None or isinstance(value, (int, float)) and value < 0:
        return {'value': f'Engine/default ({value})', 'source': origin, 'raw': patrol.get(key)}
    return {'value': value, 'source': origin, 'raw': patrol.get(key)}


def limits_at(categories, player_count):
    return {name: [entry['MaxPatrols'] for entry in entries
                   if entry['MinPlayers'] <= player_count <= entry['MaxPlayers']]
            for name, entries in categories.items()}


def valid_position(value):
    return (isinstance(value, (list, tuple)) and len(value) >= 3
            and all(isinstance(x, (float, int)) and math.isfinite(x) for x in value[:3]))


def load_anchors(mission, classes):
    """Return potential object centers, never treat relative offsets as world coords.

    Map group entries are an incomplete building inventory. Event entries are
    candidate sites, not evidence of a currently active event or AI instance.
    """
    anchors = defaultdict(list)
    groups = mission / 'mapgrouppos.xml'
    if groups.exists():
        for _, elem in ET.iterparse(groups, events=('end',)):
            name = elem.get('name')
            if elem.tag == 'group' and name in classes:
                pos = [float(v) for v in elem.get('pos', '').split()]
                if valid_position(pos):
                    anchors[name].append({'x': pos[0], 'z': pos[2], 'kind': 'Building anchor', 'source': groups.name})
            elem.clear()
    effect_path = mission / 'cfgEffectArea.json'
    if effect_path.exists():
        for area in read_json(effect_path).get('Areas', []):
            pos, name = area.get('Data', {}).get('Pos'), area.get('Type')
            if name in classes and valid_position(pos):
                anchors[name].append({'x': pos[0], 'z': pos[2], 'kind': 'Area anchor',
                                      'source': f"{effect_path.name}: {area.get('AreaName', '')}"})
    events_path, positions_path = mission / 'db/events.xml', mission / 'cfgeventspawns.xml'
    if events_path.exists() and positions_path.exists():
        event_classes = {}
        for event in ET.parse(events_path).getroot().findall('event'):
            if event.findtext('active', '0').strip() == '1':
                event_classes[event.get('name')] = {c.get('type') for c in event.findall('./children/child')} & classes
        for event in ET.parse(positions_path).getroot().findall('event'):
            for name in event_classes.get(event.get('name'), []):
                for pos in event.findall('pos'):
                    if 'x' in pos.attrib and 'z' in pos.attrib:
                        anchors[name].append({'x': float(pos.get('x')), 'z': float(pos.get('z')),
                                              'kind': 'Event candidate', 'source': f"{positions_path.name}: {event.get('name')}"})
    return anchors


def build_dataset(config, ai, mission, locations=None):
    patrols = config.get('Patrols', [])
    anchors = load_anchors(mission, {p.get('ObjectClassName') for p in patrols if p.get('ObjectClassName')})
    result = []
    for i, patrol in enumerate(patrols):
        obj = patrol.get('ObjectClassName', '')
        waypoints = [wp for wp in patrol.get('Waypoints', []) if valid_position(wp)]
        source = spawn_source(patrol)
        if obj:
            points = anchors.get(obj, [])
        else:
            roaming = patrol.get('Behaviour') in ('ROAMING', 'ROAMING_LOCAL')
            mapped = waypoints[:1] if roaming and not patrol.get('UseRandomWaypointAsStartPoint') else waypoints
            points = [{'x': wp[0], 'z': wp[2], 'kind': 'Possible start' if roaming else 'Waypoint',
                       'source': 'Configured world coordinates'} for wp in mapped]
        result.append({'id': i, 'name': patrol.get('Name') or obj or f'Patrol {i+1}',
                       'behaviour': patrol.get('Behaviour', 'Unknown'), 'category': category_for(patrol),
                       'spawnSource': source, 'faction': patrol.get('Faction', ''),
                       'objectClassName': obj, 'points': points, 'waypoints': waypoints,
                       'persist': bool(patrol.get('Persist')), 'loadout': patrol.get('Loadout') or '(faction default)',
                       'chance': patrol.get('Chance'), 'aiMin': patrol.get('NumberOfAI'),
                       'aiMax': patrol.get('NumberOfAIMax'), 'settings': patrol,
                       'effective': {k: effective_setting(patrol, config, ai, k) for k in INHERITED + ('RespawnTime',)},
                       'positionNote': ('Potential object/event anchors; relative waypoints are not plotted.' if obj else
                                        'Roaming start only; subsequent movement is chosen by the AI.' if patrol.get('Behaviour') == 'ROAMING' else
                                        'Configured route; not live AI positions.')})
    areas = []
    for key, kind in [('RoamingLocations', 'Roaming location'), ('NoGoAreas', 'No-go area')]:
        for area in (locations or {}).get(key, []):
            pos, radius = area.get('Position'), area.get('Radius', 0)
            if valid_position(pos) and radius > 0:
                areas.append({'name': area.get('Name', kind), 'kind': kind, 'x': pos[0], 'z': pos[2], 'radius': radius})
    return {'patrols': result, 'areas': areas, 'categories': config.get('LoadBalancingCategories', {}),
            'enabled': config.get('Enabled'), 'playerFactions': ai.get('PlayerFactions', []),
            'globals': {k: v for k, v in config.items() if k not in ('Patrols', 'LoadBalancingCategories')}}
