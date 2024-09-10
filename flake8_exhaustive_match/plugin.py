import ast
from typing import Dict, List


class MatchNotExhaustiveException(BaseException): ...


class MatchExhaustivenessChecker:
    name = "flake8-match-exhaustiveness"
    version = "0.1.0"

    def __init__(self, tree):
        self.tree = tree
        self.enums: Dict[str, List[str]] = self._find_enums(tree)

    def run(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Match):
                try:
                    self.check_exhaustiveness(node)
                except MatchNotExhaustiveException as e:
                    yield (
                        node.lineno,
                        node.col_offset,
                        f"MEX001 match statement is not exhaustive: {e}",
                        type(self),
                    )

    def check_exhaustiveness(self, match_node: ast.Match) -> None:
        match_var = match_node.subject

        if isinstance(match_var, ast.Name):
            for enum_name, enum_values in self.enums.items():
                matched_values = [
                    case.pattern.value.attr
                    for case in match_node.cases
                    if isinstance(case.pattern, ast.MatchValue)
                ]
                missing_values = set(enum_values) - set(matched_values)

                if missing_values:
                    raise MatchNotExhaustiveException(
                        f"Missing enum values for {sorted(missing_values)}"
                    )

        has_wildcard = any(
            isinstance(case.pattern, ast.MatchAs) and case.pattern.name is None
            for case in match_node.cases
        )

        if not has_wildcard:
            return None

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
