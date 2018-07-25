from opti.monsterbox import Monster, get_monsters
from opti.defs import set_map as SETMAP
import opti.runeimporter
import random

MAX_SETS = 5

class ScoreCard:
    score = 0

    def __init__(self, score, monster, eval_func_name):
        self.score = score
        self.eval_func_name = eval_func_name
        self.rune_ids = monster.rune_ids

    def __cmp__(self, other):
        if type(other) == type(self):
            if self.score < other.score:
                return -1
            elif self.score == other.score:
                return 0
            return 1
        else:
            raise TypeError("Scorecards can only compare to scorecards")

    def __gt__(self, other):
        if type(other) == type(self):
            if self.score > other.score:
                return True
            return False
        else:
            raise TypeError("Scorecards can only compare to scorecards")

    def __lt__(self, other):
        return not self.__gt__(other)


class MonsterEvaluator:

    def __init__(self, monster):
        if monster is not None:
            self.monster = monster
            self.recent_scorecards = {}

    def eval_pure_nuker(self):
        evaluation = self.monster.stats['ATK flat'] * self.monster.stats['CRate'] / 100 * self.monster.stats['CDmg'] / 100
        return evaluation

    #def eval_fast_nuker(self):
    #    evaluation = self.eval_pure_nuker()
    #    if self.monster.stats['SPD'] < targetspeed:
    #        evaluation = evaluation / (targetspeed - self.monster.stats['SPD'])
    #    return evaluation

    def eval_speed_nuker(self):
        evaluation = self.monster.stats['ATK flat'] * self.monster.stats['CRate'] / 100 * self.monster.stats['CDmg'] / 100 * self.monster.stats['SPD'] / 100
        return evaluation

    def eval_bruiser(self):
        evaluation = (self.monster.stats['HP flat'] + self.monster.stats['DEF flat'] * 5) * self.monster.stats['CRate'] / 100 * self.monster.stats['CDmg'] / 400 * self.monster.stats['SPD']
        return evaluation

    def eval_booster(self, targetspeed=0):
        if self.monster.stats['SPD'] < targetspeed:
            return 0
        return self.monster.stats['SPD']

    def eval_raid_frontline(self):
        evaluation = (self.monster.stats['HP flat'] + self.monster.stats['DEF flat'] * 20) * self.monster.stats['SPD'] * self.monster.stats['RES']
        return evaluation

    #def eval_raid_cleanser(self):
    #    return evaluation

    #def eval_raid_healer(self):
    #    return evaluation

    #def eval_raid_DPS(self):
    #    return evaluation

    def evaluation_types(self):
        eval_funcs = []
        for func in dir(self):
            if func.startswith('eval_'):
                eval_funcs.append(func)

        return eval_funcs

    def score_runes(self, evaltype):

        e = getattr(self, evaltype)
        return ScoreCard(e(), self.monster, evaltype)

    def rank_all_archetypes(self):
        self.evaluations = {}

        # evaluate all archetypes
        for evaltype in self.evaluation_types():
            e = self.score_runes(evaltype)
            assert e is not None
            self.evaluations[evaltype] = e

        return self.evaluations

    def single_trial(self, runebox, evaltype, allowedsets=None):
        if evaltype not in self.evaluation_types():
            raise ValueError("MonsterEvaluator.single_trial: 'evaltype' not a valid evaluator function.")

        if allowedsets is None:
            allowedsets = list(SETMAP.values())

        scorecards = {}

        assert self.monster is not None

        # initialize a dict of lists to track evaluations
        scorecards = [[], [], [], [], [], []]

        # initialize with current runes if all runes are present
        valid_runes = [rune_id for rune_id in runebox.upgraded_rune_ids if runebox.get_rune(rune_id).setname in allowedsets]

        for rune_id in valid_runes:
            # Get top n runes for each slot
            self.monster.set_rune_ids([rune_id])
            slot = runebox.get_rune(rune_id).slot - 1

            single_score = self.score_runes(evaltype)

            scorecards[slot].append(single_score)
            try:
                index = -1

                # Organize scorcards by score
                while index > (len(scorecards[slot])*-1 + 1) and scorecards[slot][index] > scorecards[slot][index-1]:
                    scorecards[slot][index], scorecards[slot][index-1] = scorecards[slot][index-1], scorecards[slot][index]
                    index = index - 1

            except IndexError: # not enough items
                print('IndexError happened while attempting to sort')

            if len(scorecards[slot]) > MAX_SETS:
                scorecards[slot].pop()

        self.recent_scorecards['evaltype'] = scorecards
        return scorecards
