import ast

from flake8_match_exhaustiveness.plugin import MatchExhaustivenessChecker


def test_match_is_exhaustive_with_wildcard():
    code = """
match x:
    case 1:
        pass
    case _:
        pass
    """
    tree = ast.parse(code)
    checker = MatchExhaustivenessChecker(tree)
    errors = list(checker.run())
    assert len(errors) == 0


def test_match_is_not_exhaustive():
    code = """
match x:
    case 1:
        pass
    """
    tree = ast.parse(code)
    checker = MatchExhaustivenessChecker(tree)
    errors = list(checker.run())
    assert len(errors) == 1
    assert errors[0][2] == "MEX001 match statement is not exhaustive"


def test_match_exhaustive_with_enum():
    code = """
from enum import Enum

class Colors(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

def f(x: Colors):
    match x:
        case Colors.RED:
            pass
        case Colors.GREEN:
            pass
        case Colors.BLUE:
            pass
    """
    tree = ast.parse(code)
    checker = MatchExhaustivenessChecker(tree)
    errors = list(checker.run())
    assert len(errors) == 0


def test_match_not_exhaustive_with_enum():
    code = """
from enum import Enum

class Colors(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

def f(x: Colors):
    match x:
        case Colors.RED:
            pass
        case Colors.GREEN:
            pass
    """
    tree = ast.parse(code)
    checker = MatchExhaustivenessChecker(tree)
    errors = list(checker.run())
    assert len(errors) == 1
    assert (
        errors[0][2]
        == "MEX001 match statement is not exhaustive: Missing enum values for ['BLUE']"
    )


def test_match_not_exhaustive_with_multiple_missing_enum():
    code = """
from enum import Enum

class Colors(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

def f(x: Colors):
    match x:
        case Colors.RED:
            pass
    """
    tree = ast.parse(code)
    checker = MatchExhaustivenessChecker(tree)
    errors = list(checker.run())
    assert len(errors) == 1
    assert (
        errors[0][2]
        == "MEX001 match statement is not exhaustive: Missing enum values for ['BLUE', 'GREEN']"
    )
