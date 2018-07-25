import os
import sys
import pytest


@pytest.fixture
def testbox():
    from opti.runeimporter import RuneBox
    testfile = os.path.join(os.getcwd(), 'test', 'runes.json')
    return RuneBox(testfile)

@pytest.fixture
def monster(testbox):
    import opti.monsterbox
    details = {
              'name': 'Shannon'
              }
    stats = {
            "HP Flat": 582,
            "ATK Flat": 505,
            "DEF Flat": 560,
            "SPD": 111,
            "RES": 15,
            "ACC": 0,
            "CRate": 15,
            "CDmg": 50,
            }

    mon = opti.monsterbox.Monster([], stats, details, testbox)
    return mon

@pytest.fixture
def evaluator(monster):
    import opti.evaluations
    ev = opti.evaluations.MonsterEvaluator(monster)
    return ev

def test_rune_box(testbox):
    box = testbox
    rune_id = 16036756868
    assert box.get_rune(rune_id).setname == "Violent"

def test_monster(monster):
    import opti.monsterbox
    print(monster.stats)
    assert monster.stats

def test_suggest(testbox, monster, evaluator):
    from opti.suggest import suggest_from_scorecards, suggestion_to_json
