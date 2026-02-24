#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

WEBSITE_LOCALES: List[str] = [
    "en", "en-US", "en-GB", "en-CA", "en-AU",
    "ja", "de", "fr", "es-ES", "es-419", "pt-BR", "ko",
    "zh-Hans", "zh-Hant", "it", "nl", "id", "vi", "th", "tr",
    "ar", "he", "hi", "pl", "ro", "cs", "hu", "el", "uk", "ru", "ms",
]

APP_TO_STORE_LOCALE = {
    "en": "en-US",
    "en-US": "en-US",
    "en-GB": "en-GB",
    "en-CA": "en-CA",
    "en-AU": "en-AU",
    "ja": "ja",
    "de": "de-DE",
    "fr": "fr-FR",
    "es-ES": "es-ES",
    "es-419": "es-MX",
    "pt-BR": "pt-BR",
    "ko": "ko",
    "zh-Hans": "zh-Hans",
    "zh-Hant": "zh-Hant",
    "it": "it",
    "nl": "nl-NL",
    "id": "id",
    "vi": "vi",
    "th": "th",
    "tr": "tr",
    "ar": "ar-SA",
    "he": "he",
    "hi": "hi",
    "pl": "pl",
    "ro": "ro",
    "cs": "cs",
    "hu": "hu",
    "el": "el",
    "uk": "uk",
    "ru": "ru",
    "ms": "ms",
}

SUPPORT_LABELS = {
    "en": "Support",
    "en-US": "Support",
    "en-GB": "Support",
    "en-CA": "Support",
    "en-AU": "Support",
    "ja": "サポート",
    "de": "Support",
    "fr": "Assistance",
    "es-ES": "Soporte",
    "es-419": "Soporte",
    "pt-BR": "Suporte",
    "ko": "지원",
    "zh-Hans": "支持",
    "zh-Hant": "支援",
    "it": "Supporto",
    "nl": "Ondersteuning",
    "id": "Dukungan",
    "vi": "Hỗ trợ",
    "th": "การช่วยเหลือ",
    "tr": "Destek",
    "ar": "الدعم",
    "he": "תמיכה",
    "hi": "सहायता",
    "pl": "Wsparcie",
    "ro": "Suport",
    "cs": "Podpora",
    "hu": "Támogatás",
    "el": "Υποστήριξη",
    "uk": "Підтримка",
    "ru": "Поддержка",
    "ms": "Sokongan",
}

RTL_LOCALES = {"ar", "he"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def parse_metadata_description(desc: str) -> Dict[str, object]:
    lines = [line.strip() for line in desc.splitlines() if line.strip()]
    bullets = [line[1:].strip() for line in lines if line.startswith("-")]

    trust_line = ""
    if lines:
        for line in reversed(lines):
            if line.startswith("-"):
                continue
            if line != lines[0]:
                trust_line = line
                break

    mission_line = lines[-1] if lines else ""
    return {
        "headline": lines[0] if lines else "",
        "bullets": bullets,
        "trust_line": trust_line,
        "mission_line": mission_line,
    }


def get_xc_value(strings: Dict[str, object], key: str, locale: str) -> str:
    entry = strings.get(key)
    if not isinstance(entry, dict):
        return ""
    localizations = entry.get("localizations")
    if not isinstance(localizations, dict):
        return ""

    candidates: List[str] = [locale]
    if "-" in locale:
        candidates.append(locale.split("-", 1)[0])
    if locale == "en":
        candidates.extend(["en-US", "en-GB", "en-CA", "en-AU"])
    candidates.extend(["en-US", "en"])

    seen = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        payload = localizations.get(candidate)
        if not isinstance(payload, dict):
            continue
        string_unit = payload.get("stringUnit")
        if not isinstance(string_unit, dict):
            continue
        value = string_unit.get("value")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    mandara_root = Path(os.getenv("MANDARISE_ROOT", str(root.parent))).resolve()

    xc_path = mandara_root / "MandariseApp" / "Mandarise" / "Localizable.xcstrings"
    metadata_root = mandara_root / "fastlane" / "metadata"

    xc = json.loads(xc_path.read_text(encoding="utf-8"))
    strings = xc.get("strings", {})
    if not isinstance(strings, dict):
        raise RuntimeError("invalid xcstrings format")

    labels: Dict[str, Dict[str, str]] = {}
    for locale in WEBSITE_LOCALES:
        store_locale = APP_TO_STORE_LOCALE[locale]
        locale_dir = metadata_root / store_locale
        name = read_text(locale_dir / "name.txt") if (locale_dir / "name.txt").exists() else "MANDARA STEPS"
        subtitle = read_text(locale_dir / "subtitle.txt") if (locale_dir / "subtitle.txt").exists() else "Goal planner & focus timer"
        desc = read_text(locale_dir / "description.txt") if (locale_dir / "description.txt").exists() else ""
        parsed = parse_metadata_description(desc)
        bullets: List[str] = parsed["bullets"]  # type: ignore[assignment]

        hero_title = get_xc_value(strings, "Welcome to Mandarise", locale) or f"Welcome to {name}"
        hero_subtitle = (
            get_xc_value(strings, "Set a goal and break it down with a mandala plan.", locale)
            or str(parsed["headline"])
            or "Set a goal and break it down with a mandala plan."
        )
        nav_privacy = get_xc_value(strings, "Privacy Policy", locale) or "Privacy Policy"
        nav_home = get_xc_value(strings, "Home", locale) or "Home"

        trust_body = (
            get_xc_value(strings, "Local-first. No accounts. No ads in v1.0.", locale)
            or str(parsed["trust_line"])
            or "Local-first. No accounts. No ads in v1.0."
        )
        trust_detail = (
            get_xc_value(
                strings,
                "Mandarise is local-first. Your goals, sessions, logs, and selected photos stay on device. We do not collect accounts, location, or ad identifiers in v1.0.",
                locale,
            )
            or trust_body
        )

        meta_description = f"{hero_subtitle} {trust_body}".strip()
        feature_goal_title = bullets[0] if len(bullets) > 0 else (get_xc_value(strings, "Create Goal", locale) or "Create Goal")
        feature_focus_title = bullets[1] if len(bullets) > 1 else "Focus / Timer"
        feature_logs_title = bullets[2] if len(bullets) > 2 else (get_xc_value(strings, "Logs", locale) or "Logs")

        labels[locale] = {
            "appName": name,
            "appTagline": subtitle,
            "pageTitle": f"{name} | {subtitle}",
            "pageDescription": meta_description,
            "supportPageTitle": f"{SUPPORT_LABELS.get(locale, 'Support')} | {name}",
            "supportPageDescription": f"{SUPPORT_LABELS.get(locale, 'Support')} · {name}",
            "privacyPageTitle": f"{nav_privacy} | {name}",
            "privacyPageDescription": trust_body,
            "heroTitle": hero_title,
            "heroSubtitle": hero_subtitle,
            "ctaAppStore": "App Store",
            "navSupport": SUPPORT_LABELS.get(locale, "Support"),
            "navPrivacy": nav_privacy,
            "navHome": nav_home,
            "featuresHeading": get_xc_value(strings, "What matters most today?", locale) or "What You Can Do",
            "featureGoalTitle": feature_goal_title,
            "featureGoalBody": get_xc_value(strings, "Tap a card to set a goal", locale) or "Tap a card to set a goal",
            "featureFocusTitle": feature_focus_title,
            "featureFocusBody": (
                bullets[4]
                if len(bullets) > 4
                else (get_xc_value(strings, "Set a focus for today.", locale) or "Set a focus for today.")
            ),
            "featureLogsTitle": feature_logs_title,
            "featureLogsBody": (
                get_xc_value(strings, "No logs yet. Complete a focus session to get started.", locale)
                or "No logs yet. Complete a focus session to get started."
            ),
            "trustTitle": get_xc_value(strings, "Privacy", locale) or "Privacy",
            "trustBody": trust_body,
            "trustDetail": trust_detail,
            "publisherHeading": "Mandala Interactive Works (MIW)",
            "publisherMission": str(parsed["mission_line"]) or hero_subtitle,
            "supportTitle": SUPPORT_LABELS.get(locale, "Support"),
            "supportHint": str(parsed["mission_line"]) or hero_subtitle,
            "privacyTitle": nav_privacy,
            "languageName": locale,
        }

    payload = {
        "defaultLocale": "en-US",
        "availableLocales": WEBSITE_LOCALES,
        "rtlLocales": sorted(RTL_LOCALES),
        "appStoreUrl": "https://apps.apple.com/app/id6758521973",
        "updatedAt": "2026-02-25",
        "labels": labels,
    }

    out = root / "assets" / "i18n" / "translations.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"generated: {out} locales={len(WEBSITE_LOCALES)}")


if __name__ == "__main__":
    main()
