import json
from opti.defs import monsters_name_map
from opti.defs import set_bonuses as BONUSES
from opti.runeimporter import RuneBox

class Monster:
    def __init__(self, rune_ids, basestats, datadict, box):
        self.box = box
        self.basestats = dict(basestats)
        self.set_rune_ids(rune_ids)
        self.details = datadict

    def set_rune_ids(self, rune_ids):
        self.rune_ids = rune_ids
        self.update_stats()

    def update_stats(self):
        self.stats = dict(self.basestats)

        for rune_id in self.rune_ids:
            rune = self.box.get_rune(rune_id)
            for key in rune.stats.keys():
                if key in self.stats.keys():
                    self.stats[key] = self.stats[key] + rune.stats[key]
                else:
                    self.stats[key] = rune.stats[key]
        try:
            self.stats['HP flat'] = self.basestats['HP flat'] * (1 + (self.stats['HP%'] / 100)) + self.stats['HP flat']
            self.stats['ATK flat'] = self.basestats['ATK flat'] * (1 + (self.stats['ATK%'] / 100)) + self.stats['ATK flat']
            self.stats['DEF flat'] = self.basestats['DEF flat'] * (1 + (self.stats['DEF%'] / 100)) + self.stats['DEF flat']

        except KeyError:
            # no runes on monster
            # basestats are already copied in
            pass

        self.apply_set_bonuses()

        if self.stats['CRate'] > 100:
            self.stats['CRate'] = 100

        if self.stats['RES'] > 100:
            self.stats['RES'] = 100

        if self.stats['ACC'] > 100:
            self.stats['ACC'] = 100

    def apply_set_bonuses(self):
        counts = {}

        for r in self.rune_ids:
            set = self.box.get_rune(r).setname
            if set in counts:
                counts[set] = counts[set] + 1
            else:
                counts[set] = 1

        for set in counts.keys():
            if set in BONUSES:
                while counts[set] >= BONUSES[set][0]:
                    setcount = BONUSES[set][0]
                    stat = BONUSES[set][1]
                    action = BONUSES[set][2]
                    amount = BONUSES[set][3]

                    counts[set] = counts[set] - setcount

                    if action == '+':
                        self.stats[stat] = self.stats[stat] + amount
                    if action == '*':
                        print("Before:", self.stats[stat], "Base:", self.basestats[stat], amount)
                        self.stats[stat] = self.stats[stat] + (self.basestats[stat] * amount)
                        print("After:", self.stats[stat])

                    print(f'Added bonus stats for {set}')

    def random_six(self):
        self.set_rune_ids(self.box.get_six_ids())

    def __str__(self):
        result = ''
        counter = 0
        for stat in self.stats.items():
            result = f'{result} {stat[0]}: {int(stat[1])}\t'
            if counter > 3:
                counter = 0
                result = result + '\n'

        return result

def get_monsters(filename, box):
    monsterbox = {}
    unitlist = {}
    with open(filename, 'r') as f:
        unitlist = json.loads(''.join(f.readlines()))['unit_list']
        assert len(unitlist) > 0
        assert 'unit_master_id' in unitlist[0]

    for monster in unitlist:
        try:
            name = monsters_name_map[str(monster['unit_master_id'])]
        except KeyError:
            name = "UNKNOWN"

        basestats = {'HP flat': monster['con'],
                     'ATK flat': monster['atk'],
                     'DEF flat': monster['def'],
                     'SPD': monster['spd'],
                     'RES': monster['resist'],
                     'ACC': monster['accuracy'],
                     'CRate': monster['critical_rate'],
                     'CDmg': monster['critical_damage']
                     }

        runes = {}
        for rune_id in [r['rune_id'] for r in monster['runes']]:
            runes[rune_id] = box.get_rune(rune_id)

        data = {} #TODO

        monsterbox[name] = Monster(runes, basestats, data, box)
    return monsterbox

def get_monster_names(filename):
    with open(filename, 'r') as f:
        unitlist = json.loads(''.join(f.readlines()))['unit_list']
        assert len(unitlist) > 0
        assert 'unit_master_id' in unitlist[0]

    monsternames = []
    for monster in unitlist:
        try:
            name = monsters_name_map[str(monster['unit_master_id'])]
        except KeyError:
            name = "UNKNOWN"
        monsternames.append(name)

    return monsternames
