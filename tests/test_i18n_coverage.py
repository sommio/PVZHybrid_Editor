from pathlib import Path

import i18n
import i18n_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
EDITOR = REPO_ROOT / "editor.py"
LOCALES_DIR = REPO_ROOT / "locales"


def test_all_static_editor_ui_texts_are_in_every_locale_catalog():
    source_texts = i18n_audit.extract_static_ui_texts(EDITOR)

    assert len(source_texts) >= 300

    missing_by_locale = i18n_audit.missing_locale_keys(
        locale_dir=LOCALES_DIR,
        source_texts=source_texts,
        language_codes=[language.code for language in i18n.supported_languages()],
    )

    assert missing_by_locale == {}
