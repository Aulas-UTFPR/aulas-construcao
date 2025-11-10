#!/usr/bin/env python3
"""
Clean Code Linter (Python)

A single-file linter that enforces a subset of "Clean Code"-inspired metrics:
- Max cyclomatic complexity per function (via radon, if installed)
- Max function length (lines)
- Max parameters per function
- Max local variables per function
- Max return statements per function
- Max branches per function (if/for/while/try/with, rough proxy for complexity)
- Forbid mutable default arguments
- Max methods per class
- Max attributes per class (class vars + attributes set on self in __init__)
- Max file length (lines)

Usage:
    python clean_code_linter.py [paths ...]

Exit codes:
    0 = no violations
    1 = violations found

Notes:
    - Cyclomatic complexity uses radon if available. Install with:
        pip install radon
      If radon is missing, complexity checks are skipped with a warning.
    - This linter intentionally keeps implementation simple and transparent.
      It complements tools like flake8/pylint; feel free to integrate it in pre-commit.
"""
from __future__ import annotations

import argparse
import ast
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple

# Optional radon import for cyclomatic complexity
try:
    from radon.complexity import cc_visit  # type: ignore
    RADON_AVAILABLE = True
except Exception:  # pragma: no cover
    RADON_AVAILABLE = False


# ----------------------------- Configuration ----------------------------- #

@dataclass
class Config:
    max_complexity: int = 10          # per function
    max_function_length: int = 50     # lines
    max_params: int = 4
    max_locals: int = 10
    max_returns: int = 3
    max_branches: int = 10
    max_methods_per_class: int = 20
    max_attrs_per_class: int = 10
    max_file_lines: int = 800
    exclude: Tuple[str, ...] = (".venv", "venv", "__pycache__", ".git")


# ------------------------------ Data Models ------------------------------ #

@dataclass
class Violation:
    path: Path
    line: int
    col: int
    code: str
    msg: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}:{self.col}: {self.code} {self.msg}"


# ------------------------------- Utilities ------------------------------- #

def is_python_file(p: Path) -> bool:
    return p.suffix == ".py" and p.is_file()


def iter_py_files(paths: Sequence[str], cfg: Config) -> Iterator[Path]:
    if not paths:
        paths = ["."]
    for base in map(Path, paths):
        if base.is_file() and is_python_file(base):
            yield base.resolve()
        elif base.is_dir():
            for root, dirs, files in os.walk(base):
                # prune excluded dirs
                dirs[:] = [d for d in dirs if d not in cfg.exclude]
                for name in files:
                    p = Path(root) / name
                    if is_python_file(p):
                        yield p.resolve()


def file_line_count(path: Path) -> int:
    try:
        with path.open("rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


# ----------------------------- AST Inspection ---------------------------- #

class CleanCodeVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str, cfg: Config):
        self.path = path
        self.source = source
        self.cfg = cfg
        self.violations: List[Violation] = []
        self._class_stack: List[ast.ClassDef] = []

    # Helpers
    def _add(self, node: ast.AST, code: str, msg: str) -> None:
        line = getattr(node, "lineno", 1)
        col = getattr(node, "col_offset", 0)
        self.violations.append(Violation(self.path, line, col, code, msg))

    @staticmethod
    def _node_length(node: ast.AST) -> int:
        start = getattr(node, "lineno", None)
        end = getattr(node, "end_lineno", None)
        if start is None or end is None:
            return 0
        return max(0, end - start + 1)

    @staticmethod
    def _extract_ids(target: ast.AST) -> List[str]:
        ids: List[str] = []
        if isinstance(target, ast.Name):
            ids.append(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                ids.extend(CleanCodeVisitor._extract_ids(elt))
        # Skip ast.Attribute (self.x) as a local var name
        return ids

    @staticmethod
    def _is_mutable_default(node: ast.expr) -> bool:
        return isinstance(node, (ast.List, ast.Set, ast.Dict))

    def _count_branches(self, fn: ast.AST) -> int:
        count = 0
        for n in ast.walk(fn):
            if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.Match)):
                count += 1
        return count

    # Visitors
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node)
        try:
            # methods per class
            methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            if len(methods) > self.cfg.max_methods_per_class:
                self._add(
                    node,
                    "CCR003",
                    f"class '{node.name}' has too many methods ({len(methods)} > {self.cfg.max_methods_per_class})",
                )

            # attributes per class (class vars + instance attrs set in __init__)
            class_attrs = 0
            for n in node.body:
                if isinstance(n, ast.Assign):
                    for t in n.targets:
                        if isinstance(t, ast.Name):
                            class_attrs += 1
            # instance attrs from __init__
            for m in methods:
                if m.name == "__init__":
                    for sub in ast.walk(m):
                        if isinstance(sub, ast.Assign):
                            for t in sub.targets:
                                if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == "self":
                                    class_attrs += 1
            if class_attrs > self.cfg.max_attrs_per_class:
                self._add(
                    node,
                    "CCR006",
                    f"class '{node.name}' has too many attributes ({class_attrs} > {self.cfg.max_attrs_per_class})",
                )
        finally:
            self.generic_visit(node)
            self._class_stack.pop()

    # Checks
    def _check_function(self, node: ast.AST) -> None:
        # name
        name = getattr(node, "name", "<lambda>")
        # params
        args_obj = node.args  # type: ignore[attr-defined]
        total_params = len(args_obj.args) + len(args_obj.kwonlyargs)
        if getattr(args_obj, "vararg", None):
            total_params += 1
        if getattr(args_obj, "kwarg", None):
            total_params += 1
        # discount 'self' or 'cls'
        if args_obj.args:
            first = args_obj.args[0].arg
            if first in {"self", "cls"}:
                total_params -= 1
        if total_params > self.cfg.max_params:
            self._add(node, "CCR001", f"function '{name}' has too many parameters ({total_params} > {self.cfg.max_params})")

        # mutable defaults
        for d in (args_obj.defaults or []):
            if self._is_mutable_default(d):
                self._add(node, "CCR005", f"function '{name}' has mutable default argument")
        for d in (args_obj.kw_defaults or []):
            if d is not None and self._is_mutable_default(d):
                self._add(node, "CCR005", f"function '{name}' has mutable default keyword argument")

        # function length
        length = self._node_length(node)
        if length and length > self.cfg.max_function_length:
            self._add(node, "CCR002", f"function '{name}' too long ({length} > {self.cfg.max_function_length} lines)")

        # locals count
        local_names = set()
        param_names = {a.arg for a in args_obj.args}
        for inner in ast.walk(node):
            if isinstance(inner, ast.Assign):
                for t in inner.targets:
                    for ident in self._extract_ids(t):
                        if ident not in param_names:
                            local_names.add(ident)
            elif isinstance(inner, ast.AnnAssign):
                for ident in self._extract_ids(inner.target):
                    if ident not in param_names:
                        local_names.add(ident)
        if len(local_names) > self.cfg.max_locals:
            self._add(node, "CCR004", f"function '{name}' has too many local variables ({len(local_names)} > {self.cfg.max_locals})")

        # returns count
        returns = sum(1 for _ in (n for n in ast.walk(node) if isinstance(n, ast.Return)))
        if returns > self.cfg.max_returns:
            self._add(node, "CCR007", f"function '{name}' has too many return statements ({returns} > {self.cfg.max_returns})")

        # branches count (rough)
        branches = self._count_branches(node)
        if branches > self.cfg.max_branches:
            self._add(node, "CCR008", f"function '{name}' has too many branches ({branches} > {self.cfg.max_branches})")


# ------------------------------ Core Runner ------------------------------ #

def analyze_file(path: Path, cfg: Config) -> List[Violation]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        return [Violation(path, e.lineno or 1, e.offset or 0, "CCR000", f"syntax error: {e.msg}")]

    visitor = CleanCodeVisitor(path, text, cfg)
    visitor.visit(tree)

    # file length
    lines = file_line_count(path)
    if lines > cfg.max_file_lines:
        visitor.violations.append(
            Violation(path, 1, 0, "CCR009", f"file too long ({lines} > {cfg.max_file_lines})")
        )

    # cyclomatic complexity via radon
    if RADON_AVAILABLE:
        try:
            for block in cc_visit(text):
                # block: has .name, .lineno, .col_offset, .complexity
                if block.complexity > cfg.max_complexity:
                    visitor.violations.append(
                        Violation(
                            path,
                            getattr(block, "lineno", 1),
                            getattr(block, "col_offset", 0),
                            "CCR010",
                            f"cyclomatic complexity too high in '{block.name}' ({block.complexity} > {cfg.max_complexity})",
                        )
                    )
        except Exception as e:  # pragma: no cover
            visitor.violations.append(
                Violation(path, 1, 0, "CCR011", f"radon failure: {e}")
            )
    else:
        # Add a soft warning (code CCR012) once per run handled in main
        pass

    return visitor.violations


def print_report(violations: List[Violation], radon_available: bool) -> None:
    if not radon_available:
        print("[warn] radon not installed; skipping cyclomatic complexity checks (pip install radon)")
    if not violations:
        print("✨ Clean! No violations found.")
        return
    # Sort
    violations.sort(key=lambda v: (str(v.path), v.line, v.col, v.code))
    # Print
    for v in violations:
        print(str(v))
    # Summary
    total = len(violations)
    by_code: dict[str, int] = {}
    for v in violations:
        by_code[v.code] = by_code.get(v.code, 0) + 1
    print("\nSummary:")
    print(f"  total violations: {total}")
    for code, count in sorted(by_code.items()):
        print(f"  {code}: {count}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Clean Code Linter (Python)")
    parser.add_argument("paths", nargs="*", help="Files or directories to scan (default: .)")
    parser.add_argument("--max-complexity", type=int, default=Config.max_complexity)
    parser.add_argument("--max-function-length", type=int, default=Config.max_function_length)
    parser.add_argument("--max-params", type=int, default=Config.max_params)
    parser.add_argument("--max-locals", type=int, default=Config.max_locals)
    parser.add_argument("--max-returns", type=int, default=Config.max_returns)
    parser.add_argument("--max-branches", type=int, default=Config.max_branches)
    parser.add_argument("--max-methods-per-class", type=int, default=Config.max_methods_per_class)
    parser.add_argument("--max-attrs-per-class", type=int, default=Config.max_attrs_per_class)
    parser.add_argument("--max-file-lines", type=int, default=Config.max_file_lines)
    parser.add_argument(
        "--exclude", nargs="*", default=list(Config.exclude),
        help="Directories to exclude (default: .venv venv __pycache__ .git)"
    )
    args = parser.parse_args(argv)

    cfg = Config(
        max_complexity=args.max_complexity,
        max_function_length=args.max_function_length,
        max_params=args.max_params,
        max_locals=args.max_locals,
        max_returns=args.max_returns,
        max_branches=args.max_branches,
        max_methods_per_class=args.max_methods_per_class,
        max_attrs_per_class=args.max_attrs_per_class,
        max_file_lines=args.max_file_lines,
        exclude=tuple(args.exclude),
    )

    violations: List[Violation] = []
    for path in iter_py_files(args.paths, cfg):
        violations.extend(analyze_file(path, cfg))

    print_report(violations, RADON_AVAILABLE)
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
