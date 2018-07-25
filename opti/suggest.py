import json

from opti.monsterbox import get_monsters
from opti.evaluations import MonsterEvaluator, ScoreCard
from opti.runeimporter import RuneBox

''' This rune suggestion tool uses an algorithm to determine a rune combination
that is extremely likely to be one of the best combinations. However, it can
of course fail to recommend a good set. The optimizer generates random results,
then reviews the random results and picks the likely best runes to work with
for your selected archetype. Then, it sorts through those runes instead of
trying all combinations. If you get some runes that look like they suck,
run the optimizer again. '''


def suggest_from_scorecards(evaluator, eval_func_name, box,
                            priset, secset, allow_broken=False):

    scorecards = evaluator.single_trial(box, eval_func_name, allowedsets=[priset, secset])
    eval_func = getattr(evaluator, eval_func_name)
    mon = evaluator.monster
    best = scorecards[0][0]
    scored_rune_ids = [set(), set(), set(), set(), set(), set()]

    for slot in scorecards:
        for score in slot:
            for rune_id in score.rune_ids:
                scored_rune_ids[box.get_rune(rune_id).slot - 1].add(rune_id)

    for runeid1 in scored_rune_ids[0]:
        for runeid2 in scored_rune_ids[1]:
            for runeid3 in scored_rune_ids[2]:
                for runeid4 in scored_rune_ids[3]:
                    for runeid5 in scored_rune_ids[4]:
                        for runeid6 in scored_rune_ids[5]:
                            testrunes = [runeid1, runeid2, runeid3,
                                         runeid4, runeid5, runeid6]

                            # Check for a valid set. Auto validate if all
                            # are the same rune or broken sets are allowed

                            valid_set = allow_broken or (priset == secset)
                            priset_count = 0
                            secset_count = 0

                            for id in testrunes:
                                sn = box.get_rune(id).setname
                                if sn == priset:
                                    priset_count += 1
                                if sn == secset:
                                    secset_count += 1

                            if priset_count == 4 and secset_count == 2:
                                valid_set = True

                            if valid_set:
                                mon.set_rune_ids(testrunes)
                                eval = ScoreCard(eval_func(), mon, eval_func_name)
                                if eval > best:
                                    best = eval

    return best


def suggestion_to_json(box, monstername, options):
    evalfunc, evalname, priset, secset = options
    try:
        mon = get_monsters(box.filename, box)[monstername]
    except KeyError:
        name = ''.join("Monster does not exist. ", monstername)
        return json.dumps(name)

    mev = MonsterEvaluator(mon)
    suggestions = suggest_from_scorecards(mev, evalfunc, box, priset, secset)
    mon.set_rune_ids(suggestions.rune_ids)

    output = {}

    output['score'] = suggestions.score
    output['rune_ids'] = suggestions.rune_ids
    output['runes'] = [box.get_rune(rune).__str__() for rune in suggestions.rune_ids]
    output['stats'] = mon.__str__()

    return json.dumps(output)


if __name__ == '__main__':
    print(suggestion_to_json('runes.json', 'Colleen', 'eval_pure_nuker'))
