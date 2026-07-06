"""Static i18n coverage helpers used by tests and maintenance scripts."""

from __future__ import annotations

import ast
import json
from pathlib import Path

UI_TEXT_KEYWORDS = {"text", "title"}


def extract_static_ui_texts(path: Path) -> set[str]:
    source = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(source)
    visitor = _StaticUiTextVisitor()
    visitor.visit(tree)
    return visitor.texts


def missing_locale_keys(
    *,
    locale_dir: Path,
    source_texts: set[str],
    language_codes: list[str],
) -> dict[str, list[str]]:
    missing: dict[str, list[str]] = {}
    for code in language_codes:
        payload = json.loads((locale_dir / f"{code}.json").read_text(encoding="utf-8"))
        translations = payload.get("translations", {})
        missing_keys = sorted(source_texts - set(translations))
        if missing_keys:
            missing[code] = missing_keys
    return missing


def _has_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)


class _StaticUiTextVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.texts: set[str] = set()

    def visit_Call(self, node: ast.Call) -> None:
        for keyword in node.keywords:
            self._collect_keyword(keyword)
        self._collect_title_call(node)
        self.generic_visit(node)

    def _collect_keyword(self, keyword: ast.keyword) -> None:
        if keyword.arg in UI_TEXT_KEYWORDS:
            self._collect_constant(keyword.value)
        elif keyword.arg == "values":
            self._collect_values(keyword.value)

    def _collect_title_call(self, node: ast.Call) -> None:
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "title":
            return
        if not node.args:
            return
        self._collect_constant(node.args[0])

    def _collect_values(self, value: ast.AST) -> None:
        if not isinstance(value, ast.List | ast.Tuple):
            return
        for item in value.elts:
            self._collect_constant(item)

    def _collect_constant(self, value: ast.AST) -> None:
        if (
            isinstance(value, ast.Constant)
            and isinstance(value.value, str)
            and _has_cjk(value.value)
        ):
            self.texts.add(value.value)
