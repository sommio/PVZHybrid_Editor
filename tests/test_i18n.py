import json
from pathlib import Path

import pytest

import i18n

REPO_ROOT = Path(__file__).resolve().parents[1]
LOCALES_DIR = REPO_ROOT / "locales"


def test_supported_languages_include_required_eight_languages():
    codes = [language.code for language in i18n.supported_languages()]

    assert codes == ["zh_CN", "en", "es", "fr", "de", "ja", "ko", "ru"]
    assert len(codes) == 8


def test_locale_files_exist_and_share_identical_translation_keys():
    expected_codes = {language.code for language in i18n.supported_languages()}
    locale_paths = {path.stem: path for path in LOCALES_DIR.glob("*.json")}

    assert set(locale_paths) == expected_codes

    key_sets = {}
    for code, path in locale_paths.items():
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["code"] == code
        assert payload["language_name"]
        assert payload["native_name"]
        assert payload["translations"]
        key_sets[code] = set(payload["translations"])

    assert len({frozenset(keys) for keys in key_sets.values()}) == 1


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("zh_CN", "选择游戏"),
        ("en", "Choose game"),
        ("es", "Elegir juego"),
    ],
)
def test_translate_known_ui_text(language, expected):
    assert i18n.translate("选择游戏", language=language) == expected


def test_translate_interpolates_named_values_and_falls_back_to_source_text():
    assert (
        i18n.translate(
            "app.title",
            language="en",
            version="2.73",
            game_version="3.17",
        )
        == "PVZ Hybrid Multi-tool Editor  2.73      Game version: 3.17"
    )
    assert i18n.translate("未收录文案", language="en") == "未收录文案"


def test_unsupported_language_is_rejected():
    with pytest.raises(ValueError):
        i18n.set_language("pt_BR")


class FakeWidget:
    def __init__(self):
        self.options = {}

    def configure(self, **kwargs):
        self.options.update(kwargs)


def test_registered_widgets_refresh_when_language_changes():
    widget = FakeWidget()
    i18n.set_language("zh_CN")
    i18n.register_widget(widget, text="选择游戏")

    i18n.set_language("es")
    i18n.refresh_widgets()
    assert widget.options["text"] == "Elegir juego"

    i18n.set_language("en")
    i18n.refresh_widgets()
    assert widget.options["text"] == "Choose game"


def test_translate_values_preserves_unknown_items():
    assert i18n.translate_values(["选择游戏", "Ctrl+F2"], language="en") == [
        "Choose game",
        "Ctrl+F2",
    ]


def test_install_tk_i18n_translates_widgets_and_notebook_tabs():
    class FakeLabel:
        def __init__(self, *args, **kwargs):
            del args
            self.options = dict(kwargs)

        def configure(self, **kwargs):
            self.options.update(kwargs)

    class FakeNotebook:
        def __init__(self, *args, **kwargs):
            del args, kwargs
            self.tabs = {}

        def add(self, child, **kwargs):
            self.tabs[child] = kwargs

        def tab(self, child, **kwargs):
            self.tabs[child].update(kwargs)

    class FakeTtk:
        Label = FakeLabel
        Notebook = FakeNotebook

    i18n.set_language("en")
    i18n.install_tk_i18n(FakeTtk)

    label = FakeTtk.Label(text="选择游戏")
    notebook = FakeTtk.Notebook()
    notebook.add("common", text="常用功能")

    assert label.options["text"] == "Choose game"
    assert notebook.tabs["common"]["text"] == "Common tools"

    i18n.set_language("es")
    i18n.refresh_widgets()

    assert label.options["text"] == "Elegir juego"
    assert notebook.tabs["common"]["text"] == "Herramientas comunes"


def test_translated_combobox_values_keep_source_values_for_business_logic():
    class FakeCombobox:
        def __init__(self, *args, **kwargs):
            del args
            self.options = dict(kwargs)
            self.selected = ""

        def configure(self, **kwargs):
            self.options.update(kwargs)

        def get(self):
            return self.selected

        def set(self, value):
            self.selected = value

    class FakeTtk:
        Combobox = FakeCombobox

    i18n.set_language("en")
    i18n.install_tk_i18n(FakeTtk)

    combobox = FakeTtk.Combobox(values=["选择游戏", "植物"])
    combobox.set("植物")

    assert combobox.options["values"] == ["Choose game", "Plants"]
    assert combobox.selected == "Plants"
    assert combobox.get() == "植物"

    i18n.set_language("es")
    i18n.refresh_widgets()

    assert combobox.options["values"] == ["Elegir juego", "Plantas"]
    assert combobox.selected == "Plantas"
    assert combobox.get() == "植物"
