import ast
from typing import Dict, List


class MatchExhaustivenessChecker:
    name = "flake8-match-exhaustiveness"
    version = "0.1.0"

    def __init__(self, tree):
        self.tree = tree
        self.enums: Dict[str, List[str]] = self._find_enums(tree)

    def run(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Match):
                if not self.is_exhaustive(node):
                    yield (
                        node.lineno,
                        node.col_offset,
                        "MEX001 match statement is not exhaustive",
                        type(self),
                    )

    def is_exhaustive(self, match_node: ast.Match) -> bool:
        match_var = match_node.subject

        if isinstance(match_var, ast.Name):
            for enum_name, enum_values in self.enums.items():
                matched_values = [
                    case.pattern.value.attr
                    for case in match_node.cases
                    if isinstance(case.pattern, ast.MatchValue)
                ]
                return set(matched_values) == set(enum_values)

        has_wildcard = any(
            isinstance(case.pattern, ast.MatchAs) and case.pattern.name is None
            for case in match_node.cases
        )

        return has_wildcard

    def _find_enums(self, tree: ast.AST) -> Dict[str, List[str]]:
        enums = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "Enum":
                        enum_name = node.name
                        enum_values = [
                            item.targets[0].id
                            for item in node.body
                            if isinstance(item, ast.Assign)
                        ]
                        enums[enum_name] = enum_values
        return enums


def register(linter):
    linter.register_checker(MatchExhaustivenessChecker)
