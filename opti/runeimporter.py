import json
import random

from opti.defs import effect_type_map, set_map


class RuneBox():
    def __init__(self, filename):
        self.filename=filename
        self.organize_runes(filename)
        self.locked_runes=[]

    def import_runes(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
        summonerjson = json.loads(''.join(lines))
        allRunes = summonerjson['runes']
        for mon in summonerjson['unit_list']:
            for rune in mon['runes']:
                allRunes.append(rune)

        return allRunes

    def get_rune(self, id):
        return self.unsorted_runes[id]

    def get_random_rune(self):
        return random.choice(self.unsorted_runes[values])

    def organize_runes(self, filename):
        self.unsorted_runes = {}
        self.sorted_rune_ids = [[] for _ in range(len(set_map))]
        self.upgraded_rune_ids = []

        #create rune objects. Add +12 runes to the primary dict.
        for rune in self.import_runes(filename):
            self.unsorted_runes[rune['rune_id']] = Rune(rune['class'], rune['pri_eff'], rune['sec_eff'], rune['slot_no'], rune['upgrade_curr'], rune['set_id'])

            if self.unsorted_runes[rune['rune_id']].upg >= 12:
                self.upgraded_rune_ids.append(rune['rune_id'])
                self.sorted_rune_ids[self.unsorted_runes[rune['rune_id']].set].append(rune['rune_id'])

    def lock_rune(self, rune_id):
        if rune_id in self.upgraded_rune_ids:
            self.upgraded_rune_ids.remove(rune_id)
            set = self.unsorted_runes[rune_id].set
            self.sorted_rune_ids[set].remove(rune_id)
            self.locked_runes.append(rune_id)

    def unlock_rune(self, rune_id):
        if rune_id in self.unsorted_runes.keys():
            if rune_id not in self.upgraded_rune_ids:
                set = self.unsorted_runes[rune_id].set
                self.upgraded_rune_ids.append(rune_id)
                self.sorted_rune_ids[set].append(rune_id)
                self.locked_runes.remove(rune_id)

    def unlock_all_runes(self):
        for rune_id in self.unsorted_runes.keys():
            self.unlock_rune(rune_id)

    def get_six_ids(self):
        result = []

        for slot in self.sorted_rune_ids:
            choice = random.choice(slot)
            result.append(choice)

        return result

    def display_all_runes(self):
        for rune in self.unsorted_runes.values():
            print(rune)

    def display_sorted_runes(self, runes):
        for rune in self.sorted_rune_ids.values():
            print(rune)

    def count(self):
        return len(self.unsorted_runes)

    def to_json(self):
        return json.dumps({'runes': self.unsorted_runes})

class Rune():
    def __init__(self, grade, primary, stats, slot, upg, set):

        self.primary = effect_type_map[primary[0]]
        self.grade = grade
        self.slot = slot
        self.upg = upg
        self.set = int(set)
        self.setname = set_map[self.set]

        self.stats = {'HP%': 0,
                      'ATK%': 0,
                      'DEF%': 0,
                      'CRate': 0,
                      'CDmg': 0,
                      'ACC': 0,
                      'RES': 0,
                      'HP flat': 0,
                      'DEF flat': 0,
                      'ATK flat': 0,
                      'SPD': 0,
                      }

        stats = [(effect_type_map[x[0]], x[1]) for x in stats]
        stats.append((self.primary, primary[1]))

        for s in stats:
            self.stats[s[0]] = s[1]

    def __str__(self):
        formattedstring = "Main: " + str(self.primary) + '\t' + self.setname + '\n'
        formattedstring = formattedstring + "Slot: " + str(self.slot) + '\n'
        formattedstring = formattedstring + "Upg: " + str(self.upg) + '\t\t'
        formattedstring = formattedstring + "Grade: " + str(self.grade) + '\n'
        fstats = ''.join([stat[0] + '\t' + str(stat[1]) + '\n' for stat in self.stats.items() if stat[1] != 0])
        formattedstring = formattedstring + "Stats: " + '\n' + fstats

        return formattedstring
