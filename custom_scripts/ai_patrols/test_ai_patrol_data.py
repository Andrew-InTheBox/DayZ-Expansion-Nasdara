"""Regression checks for local offsets, inheritance and Nasdara classifications."""
import copy
from pathlib import Path
import tempfile
import unittest

from ai_patrol_data import (DEFAULT_AI, DEFAULT_MISSION, build_dataset, category_for,
                            effective_setting, limits_at, read_json)


class PatrolDataTests(unittest.TestCase):
    def test_respawn_sentinels_differ_from_normal_inheritance(self):
        self.assertEqual(effective_setting({'RespawnTime': -1}, {'RespawnTime': 1800}, {}, 'RespawnTime')['value'], 'Disabled')
        inherited = effective_setting({'RespawnTime': -2}, {'RespawnTime': 1800}, {}, 'RespawnTime')
        self.assertEqual((inherited['value'], inherited['source']), (1800, 'Patrol globals'))
        self.assertEqual(effective_setting({'RespawnTime': 120}, {'RespawnTime': 1800}, {}, 'RespawnTime')['value'], 120)
        noise = effective_setting({'NoiseInvestigationDistanceLimit': -1}, {'NoiseInvestigationDistanceLimit': -1},
                                  {'NoiseInvestigationDistanceLimit': 500}, 'NoiseInvestigationDistanceLimit')
        self.assertEqual((noise['value'], noise['source']), (500, 'AISettings'))

    def test_object_offsets_stay_local_and_missing_objects_remain(self):
        with tempfile.TemporaryDirectory() as folder:
            mission = Path(folder)
            (mission / 'mapgrouppos.xml').write_text('<map><group name="Building" pos="1000 20 2000"/></map>')
            config = {'Patrols': [
                {'Name': 'Building guard', 'ObjectClassName': 'Building', 'Behaviour': 'HALT', 'Waypoints': [[1, 2, 3]]},
                {'Name': 'Unknown event', 'ObjectClassName': 'Wreck_UH1Y', 'Waypoints': []},
                {'Name': 'Roamer', 'Behaviour': 'ROAMING', 'Waypoints': [[3000, 0, 4000], [5000, 0, 6000]]}]}
            before = copy.deepcopy(config)
            data = build_dataset(config, {}, mission)
            self.assertEqual(config, before)
            self.assertEqual(data['patrols'][0]['points'][0]['x'], 1000)
            self.assertEqual(data['patrols'][0]['waypoints'], [[1, 2, 3]])
            self.assertEqual(data['patrols'][1]['points'], [])
            self.assertEqual(len(data['patrols'][2]['points']), 1)
            config['Patrols'][2]['UseRandomWaypointAsStartPoint'] = 1
            self.assertEqual(len(build_dataset(config, {}, mission)['patrols'][2]['points']), 2)

    def test_active_events_are_candidate_sites_and_inactive_events_are_ignored(self):
        with tempfile.TemporaryDirectory() as folder:
            mission = Path(folder); (mission/'db').mkdir()
            (mission/'db/events.xml').write_text('<events><event name="Crash"><active>1</active><children><child type="Wreck_UH1Y"/></children></event><event name="Disabled"><active>0</active><children><child type="Wreck_UH1Y"/></children></event></events>')
            (mission/'cfgeventspawns.xml').write_text('<eventposdef><event name="Crash"><pos x="5000" z="6000"/></event><event name="Disabled"><pos x="1" z="2"/></event></eventposdef>')
            data = build_dataset({'Patrols': [{'ObjectClassName': 'Wreck_UH1Y'}]}, {}, mission)
            self.assertEqual(len(data['patrols'][0]['points']), 1)
            self.assertEqual(data['patrols'][0]['points'][0]['kind'], 'Event candidate')

    def test_default_categories_are_singular(self):
        self.assertEqual(category_for({'ObjectClassName': 'Building'}), 'ObjectPatrol')
        self.assertEqual(category_for({}), 'Patrol')
        self.assertEqual(category_for({'LoadBalancingCategory': 'Survivor'}), 'Survivor')

    def test_current_nasdara_configuration(self):
        config = read_json(DEFAULT_MISSION / 'expansion/settings/AIPatrolSettings.json')
        ai = read_json(DEFAULT_AI)
        data = build_dataset(config, ai, DEFAULT_MISSION)
        self.assertEqual(len(data['patrols']), len(config['Patrols']))
        for item, raw in zip(data['patrols'], config['Patrols']):
            self.assertEqual(item['settings'], raw)
            if raw.get('Behaviour') == 'ROAMING':
                self.assertEqual(item['effective']['RespawnTime']['value'], raw['RespawnTime'])
                self.assertEqual(item['effective']['NoiseInvestigationDistanceLimit']['value'], raw['NoiseInvestigationDistanceLimit'])
        self.assertTrue(all(item['points'] or item['objectClassName'] or not item['waypoints'] for item in data['patrols']))

    def test_caps_at_player_range_boundaries(self):
        categories = {'Global': [{'MinPlayers': 0, 'MaxPlayers': 10, 'MaxPatrols': -1},
                                 {'MinPlayers': 11, 'MaxPlayers': 255, 'MaxPatrols': 5}]}
        self.assertEqual(limits_at(categories, 0)['Global'], [-1])
        self.assertEqual(limits_at(categories, 10)['Global'], [-1])
        self.assertEqual(limits_at(categories, 11)['Global'], [5])


if __name__ == '__main__':
    unittest.main()
