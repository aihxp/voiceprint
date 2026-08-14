#!/usr/bin/env python3
"""Inspect and clean text-only Unicode artifacts without changing source files."""

# Implements: P-MUST-02, P-MUST-03, P-MUST-04, P-SHOULD-01

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
import unicodedata


_JOINERS = {"\u200c", "\u200d"}
_MONGOLIAN_VARIATION_SELECTORS = range(0x180B, 0x180E)
MAX_INPUT_BYTES = 4 * 1024 * 1024
EMOJI_ZWJ_VERSION = "17.0"
_SCRIPT_FAMILY_RANGES = (
    ("arabic", ((0x0600, 0x06FF), (0x0750, 0x077F), (0x0870, 0x08FF))),
    ("syriac", ((0x0700, 0x074F), (0x0860, 0x086F))),
    ("thaana", ((0x0780, 0x07BF),)),
    ("devanagari", ((0x0900, 0x097F), (0xA8E0, 0xA8FF))),
    ("bengali", ((0x0980, 0x09FF),)),
    ("gurmukhi", ((0x0A00, 0x0A7F),)),
    ("gujarati", ((0x0A80, 0x0AFF),)),
    ("odia", ((0x0B00, 0x0B7F),)),
    ("tamil", ((0x0B80, 0x0BFF),)),
    ("telugu", ((0x0C00, 0x0C7F),)),
    ("kannada", ((0x0C80, 0x0CFF),)),
    ("malayalam", ((0x0D00, 0x0D7F),)),
    ("sinhala", ((0x0D80, 0x0DFF),)),
    ("myanmar", ((0x1000, 0x109F), (0xAA60, 0xAA7F))),
    ("khmer", ((0x1780, 0x17FF),)),
    ("mongolian", ((0x1800, 0x18AF),)),
    ("syloti-nagri", ((0xA800, 0xA82F),)),
    ("saurashtra", ((0xA880, 0xA8DF),)),
    ("javanese", ((0xA980, 0xA9DF),)),
    ("cham", ((0xAA00, 0xAA5F),)),
    ("meetei-mayek", ((0xABC0, 0xABFF),)),
)
_EMOJI_RANGES = (
    (0x2600, 0x27BF),
    (0x1F000, 0x1FAFF),
)
_REMOVABLE_FORMAT_CODE_POINTS = {
    0x00AD,
    0x061C,
    0x180E,
    0x200B,
    0x200E,
    0x200F,
    0x202A,
    0x202B,
    0x202C,
    0x202D,
    0x202E,
    0x2060,
    0x2061,
    0x2062,
    0x2063,
    0x2064,
    0x2065,
    0x2066,
    0x2067,
    0x2068,
    0x2069,
    0x206A,
    0x206B,
    0x206C,
    0x206D,
    0x206E,
    0x206F,
    0xFEFF,
    0xFFF9,
    0xFFFA,
    0xFFFB,
}
# Derived from https://www.unicode.org/Public/17.0.0/emoji/emoji-zwj-sequences.txt
# by taking the numeric base pair on each side of U+200D.
_EMOJI_ZWJ_PAIRS = frozenset(
    {
        (0x2640, 0x27A1),
        (0x2642, 0x27A1),
        (0x26D3, 0x1F4A5),
        (0x26F9, 0x2640),
        (0x26F9, 0x2642),
        (0x2764, 0x1F468),
        (0x2764, 0x1F469),
        (0x2764, 0x1F48B),
        (0x2764, 0x1F525),
        (0x2764, 0x1F9D1),
        (0x2764, 0x1FA79),
        (0x1F344, 0x1F7EB),
        (0x1F34B, 0x1F7E9),
        (0x1F3C3, 0x2640),
        (0x1F3C3, 0x2642),
        (0x1F3C3, 0x27A1),
        (0x1F3C4, 0x2640),
        (0x1F3C4, 0x2642),
        (0x1F3CA, 0x2640),
        (0x1F3CA, 0x2642),
        (0x1F3CB, 0x2640),
        (0x1F3CB, 0x2642),
        (0x1F3CC, 0x2640),
        (0x1F3CC, 0x2642),
        (0x1F3F3, 0x26A7),
        (0x1F3F3, 0x1F308),
        (0x1F3F4, 0x2620),
        (0x1F408, 0x2B1B),
        (0x1F415, 0x1F9BA),
        (0x1F426, 0x2B1B),
        (0x1F426, 0x1F525),
        (0x1F430, 0x1F468),
        (0x1F430, 0x1F469),
        (0x1F430, 0x1F9D1),
        (0x1F43B, 0x2744),
        (0x1F441, 0x1F5E8),
        (0x1F466, 0x1F466),
        (0x1F467, 0x1F466),
        (0x1F467, 0x1F467),
        (0x1F468, 0x2695),
        (0x1F468, 0x2696),
        (0x1F468, 0x2708),
        (0x1F468, 0x2764),
        (0x1F468, 0x1F33E),
        (0x1F468, 0x1F373),
        (0x1F468, 0x1F37C),
        (0x1F468, 0x1F393),
        (0x1F468, 0x1F3A4),
        (0x1F468, 0x1F3A8),
        (0x1F468, 0x1F3EB),
        (0x1F468, 0x1F3ED),
        (0x1F468, 0x1F430),
        (0x1F468, 0x1F466),
        (0x1F468, 0x1F467),
        (0x1F468, 0x1F468),
        (0x1F468, 0x1F469),
        (0x1F468, 0x1F4BB),
        (0x1F468, 0x1F4BC),
        (0x1F468, 0x1F527),
        (0x1F468, 0x1F52C),
        (0x1F468, 0x1F680),
        (0x1F468, 0x1F692),
        (0x1F468, 0x1F91D),
        (0x1F468, 0x1F9AF),
        (0x1F468, 0x1F9B0),
        (0x1F468, 0x1F9B1),
        (0x1F468, 0x1F9B2),
        (0x1F468, 0x1F9B3),
        (0x1F468, 0x1F9BC),
        (0x1F468, 0x1F9BD),
        (0x1F468, 0x1FAEF),
        (0x1F469, 0x2695),
        (0x1F469, 0x2696),
        (0x1F469, 0x2708),
        (0x1F469, 0x2764),
        (0x1F469, 0x1F33E),
        (0x1F469, 0x1F373),
        (0x1F469, 0x1F37C),
        (0x1F469, 0x1F393),
        (0x1F469, 0x1F3A4),
        (0x1F469, 0x1F3A8),
        (0x1F469, 0x1F3EB),
        (0x1F469, 0x1F3ED),
        (0x1F469, 0x1F430),
        (0x1F469, 0x1F466),
        (0x1F469, 0x1F467),
        (0x1F469, 0x1F469),
        (0x1F469, 0x1F4BB),
        (0x1F469, 0x1F4BC),
        (0x1F469, 0x1F527),
        (0x1F469, 0x1F52C),
        (0x1F469, 0x1F680),
        (0x1F469, 0x1F692),
        (0x1F469, 0x1F91D),
        (0x1F469, 0x1F9AF),
        (0x1F469, 0x1F9B0),
        (0x1F469, 0x1F9B1),
        (0x1F469, 0x1F9B2),
        (0x1F469, 0x1F9B3),
        (0x1F469, 0x1F9BC),
        (0x1F469, 0x1F9BD),
        (0x1F469, 0x1FAEF),
        (0x1F46E, 0x2640),
        (0x1F46E, 0x2642),
        (0x1F46F, 0x2640),
        (0x1F46F, 0x2642),
        (0x1F470, 0x2640),
        (0x1F470, 0x2642),
        (0x1F471, 0x2640),
        (0x1F471, 0x2642),
        (0x1F473, 0x2640),
        (0x1F473, 0x2642),
        (0x1F477, 0x2640),
        (0x1F477, 0x2642),
        (0x1F481, 0x2640),
        (0x1F481, 0x2642),
        (0x1F482, 0x2640),
        (0x1F482, 0x2642),
        (0x1F486, 0x2640),
        (0x1F486, 0x2642),
        (0x1F487, 0x2640),
        (0x1F487, 0x2642),
        (0x1F48B, 0x1F468),
        (0x1F48B, 0x1F469),
        (0x1F48B, 0x1F9D1),
        (0x1F575, 0x2640),
        (0x1F575, 0x2642),
        (0x1F62E, 0x1F4A8),
        (0x1F635, 0x1F4AB),
        (0x1F636, 0x1F32B),
        (0x1F642, 0x2194),
        (0x1F642, 0x2195),
        (0x1F645, 0x2640),
        (0x1F645, 0x2642),
        (0x1F646, 0x2640),
        (0x1F646, 0x2642),
        (0x1F647, 0x2640),
        (0x1F647, 0x2642),
        (0x1F64B, 0x2640),
        (0x1F64B, 0x2642),
        (0x1F64D, 0x2640),
        (0x1F64D, 0x2642),
        (0x1F64E, 0x2640),
        (0x1F64E, 0x2642),
        (0x1F6A3, 0x2640),
        (0x1F6A3, 0x2642),
        (0x1F6B4, 0x2640),
        (0x1F6B4, 0x2642),
        (0x1F6B5, 0x2640),
        (0x1F6B5, 0x2642),
        (0x1F6B6, 0x2640),
        (0x1F6B6, 0x2642),
        (0x1F6B6, 0x27A1),
        (0x1F91D, 0x1F468),
        (0x1F91D, 0x1F469),
        (0x1F91D, 0x1F9D1),
        (0x1F926, 0x2640),
        (0x1F926, 0x2642),
        (0x1F935, 0x2640),
        (0x1F935, 0x2642),
        (0x1F937, 0x2640),
        (0x1F937, 0x2642),
        (0x1F938, 0x2640),
        (0x1F938, 0x2642),
        (0x1F939, 0x2640),
        (0x1F939, 0x2642),
        (0x1F93C, 0x2640),
        (0x1F93C, 0x2642),
        (0x1F93D, 0x2640),
        (0x1F93D, 0x2642),
        (0x1F93E, 0x2640),
        (0x1F93E, 0x2642),
        (0x1F9AF, 0x27A1),
        (0x1F9B8, 0x2640),
        (0x1F9B8, 0x2642),
        (0x1F9B9, 0x2640),
        (0x1F9B9, 0x2642),
        (0x1F9BC, 0x27A1),
        (0x1F9BD, 0x27A1),
        (0x1F9CD, 0x2640),
        (0x1F9CD, 0x2642),
        (0x1F9CE, 0x2640),
        (0x1F9CE, 0x2642),
        (0x1F9CE, 0x27A1),
        (0x1F9CF, 0x2640),
        (0x1F9CF, 0x2642),
        (0x1F9D1, 0x2695),
        (0x1F9D1, 0x2696),
        (0x1F9D1, 0x2708),
        (0x1F9D1, 0x2764),
        (0x1F9D1, 0x1F33E),
        (0x1F9D1, 0x1F373),
        (0x1F9D1, 0x1F37C),
        (0x1F9D1, 0x1F384),
        (0x1F9D1, 0x1F393),
        (0x1F9D1, 0x1F3A4),
        (0x1F9D1, 0x1F3A8),
        (0x1F9D1, 0x1F3EB),
        (0x1F9D1, 0x1F3ED),
        (0x1F9D1, 0x1F430),
        (0x1F9D1, 0x1F4BB),
        (0x1F9D1, 0x1F4BC),
        (0x1F9D1, 0x1F527),
        (0x1F9D1, 0x1F52C),
        (0x1F9D1, 0x1F680),
        (0x1F9D1, 0x1F692),
        (0x1F9D1, 0x1F91D),
        (0x1F9D1, 0x1F9AF),
        (0x1F9D1, 0x1F9B0),
        (0x1F9D1, 0x1F9B1),
        (0x1F9D1, 0x1F9B2),
        (0x1F9D1, 0x1F9B3),
        (0x1F9D1, 0x1F9BC),
        (0x1F9D1, 0x1F9BD),
        (0x1F9D1, 0x1F9D1),
        (0x1F9D1, 0x1F9D2),
        (0x1F9D1, 0x1FA70),
        (0x1F9D1, 0x1FAEF),
        (0x1F9D2, 0x1F9D2),
        (0x1F9D4, 0x2640),
        (0x1F9D4, 0x2642),
        (0x1F9D6, 0x2640),
        (0x1F9D6, 0x2642),
        (0x1F9D7, 0x2640),
        (0x1F9D7, 0x2642),
        (0x1F9D8, 0x2640),
        (0x1F9D8, 0x2642),
        (0x1F9D9, 0x2640),
        (0x1F9D9, 0x2642),
        (0x1F9DA, 0x2640),
        (0x1F9DA, 0x2642),
        (0x1F9DB, 0x2640),
        (0x1F9DB, 0x2642),
        (0x1F9DC, 0x2640),
        (0x1F9DC, 0x2642),
        (0x1F9DD, 0x2640),
        (0x1F9DD, 0x2642),
        (0x1F9DE, 0x2640),
        (0x1F9DE, 0x2642),
        (0x1F9DF, 0x2640),
        (0x1F9DF, 0x2642),
        (0x1FAEF, 0x1F468),
        (0x1FAEF, 0x1F469),
        (0x1FAEF, 0x1F9D1),
        (0x1FAF1, 0x1FAF2),
    }
)
_EMOJI_ZWJ_BASES = frozenset(
    code_point for pair in _EMOJI_ZWJ_PAIRS for code_point in pair
)


def _in_ranges(code_point: int, ranges: tuple[tuple[int, int], ...]) -> bool:
    return any(start <= code_point <= end for start, end in ranges)


def _is_variation_selector(character: str) -> bool:
    code_point = ord(character)
    return (
        code_point in _MONGOLIAN_VARIATION_SELECTORS
        or code_point == 0x180F
        or 0xFE00 <= code_point <= 0xFE0F
        or 0xE0100 <= code_point <= 0xE01EF
    )


def _script_family(character: str) -> str | None:
    if unicodedata.category(character)[0] != "L":
        return None
    code_point = ord(character)
    for family, ranges in _SCRIPT_FAMILY_RANGES:
        if _in_ranges(code_point, ranges):
            return family
    return None


def _is_emoji_range_base(character: str) -> bool:
    return _in_ranges(ord(character), _EMOJI_RANGES)


def _is_known_emoji_zwj_pair(previous_base: str, next_base: str) -> bool:
    return (ord(previous_base), ord(next_base)) in _EMOJI_ZWJ_PAIRS


def _is_explicit_format_removal(code_point: int) -> bool:
    return code_point in _REMOVABLE_FORMAT_CODE_POINTS or 0xE0000 <= code_point <= 0xE007F


def _is_emoji_modifier(character: str) -> bool:
    return 0x1F3FB <= ord(character) <= 0x1F3FF


def _is_base_character(character: str) -> bool:
    code_point = ord(character)
    category_group = unicodedata.category(character)[0]
    return not _is_emoji_modifier(character) and (
        code_point in _EMOJI_ZWJ_BASES or category_group in {"L", "N", "S"}
    )


def _is_context_extender(character: str) -> bool:
    return (
        unicodedata.category(character)[0] == "M"
        or _is_variation_selector(character)
        or _is_emoji_modifier(character)
    )


def _neighboring_bases(text: str) -> tuple[list[str | None], list[str | None]]:
    previous: list[str | None] = [None] * len(text)
    following: list[str | None] = [None] * len(text)
    last_base = None
    for index, character in enumerate(text):
        previous[index] = last_base
        if _is_base_character(character):
            last_base = character
        elif not _is_context_extender(character):
            last_base = None

    next_base = None
    for index in range(len(text) - 1, -1, -1):
        following[index] = next_base
        character = text[index]
        if _is_base_character(character):
            next_base = character
        elif not _is_context_extender(character):
            next_base = None
    return previous, following


def _classify(
    character: str,
    previous_base: str | None,
    next_base: str | None,
) -> tuple[str, str | None] | None:
    code_point = ord(character)

    if unicodedata.category(character) == "Zs" and character != " ":
        return "normalize", None

    if character in _JOINERS:
        if (
            character == "\u200d"
            and previous_base is not None
            and next_base is not None
            and _is_known_emoji_zwj_pair(previous_base, next_base)
        ):
            return "preserve", "matches a pinned Emoji 17 pair"
        previous_family = (
            _script_family(previous_base) if previous_base is not None else None
        )
        next_family = _script_family(next_base) if next_base is not None else None
        if previous_family is not None and previous_family == next_family:
            return "preserve", "required by surrounding complex-script orthography"
        return "remove", None

    if _is_variation_selector(character):
        if code_point in _MONGOLIAN_VARIATION_SELECTORS or code_point == 0x180F:
            if (
                previous_base is not None
                and _script_family(previous_base) == "mongolian"
            ):
                return "preserve", "Mongolian selector after Mongolian base"
            return "remove", None
        if (
            code_point in {0xFE0E, 0xFE0F}
            and previous_base is not None
            and _is_emoji_range_base(previous_base)
        ):
            presentation = "text" if code_point == 0xFE0E else "emoji"
            return (
                "preserve",
                f"{presentation}-presentation selector after emoji-range base",
            )
        return "remove", None

    if unicodedata.category(character) == "Cf":
        if _is_explicit_format_removal(code_point):
            return "remove", None
        return "preserve", "unclassified format control preserved conservatively"

    return None


def _code_point_label(character: str) -> str:
    return f"U+{ord(character):04X}"


def _process(text: str) -> tuple[str, dict[str, object]]:
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    previous_bases, next_bases = _neighboring_bases(text)
    findings: dict[tuple[str, str, str | None], dict[str, object]] = {}
    cleaned_characters: list[str] = []
    summary = {
        "detected": 0,
        "removed": 0,
        "normalized": 0,
        "preserved": 0,
        "actionable": 0,
    }

    for offset, character in enumerate(text):
        classification = _classify(
            character,
            previous_bases[offset],
            next_bases[offset],
        )
        if classification is None:
            cleaned_characters.append(character)
            continue

        action, reason = classification
        key = (character, action, reason)
        item = findings.get(key)
        if item is None:
            item = {
                "code_point": _code_point_label(character),
                "name": unicodedata.name(character, "UNNAMED CHARACTER"),
                "action": action,
                "count": 0,
                "offsets": [],
            }
            if reason is not None:
                item["reason"] = reason
            findings[key] = item

        item["count"] += 1
        if len(item["offsets"]) < 10:
            item["offsets"].append(offset)

        summary["detected"] += 1
        if action == "remove":
            summary["removed"] += 1
            summary["actionable"] += 1
        elif action == "normalize":
            summary["normalized"] += 1
            summary["actionable"] += 1
            cleaned_characters.append(" ")
        else:
            summary["preserved"] += 1
            cleaned_characters.append(character)

    manifest: dict[str, object] = {
        "policy_version": 1,
        "unicode_version": unicodedata.unidata_version,
        "emoji_zwj_version": EMOJI_ZWJ_VERSION,
        "findings": list(findings.values()),
        "summary": summary,
    }
    return "".join(cleaned_characters), manifest


def inspect_text(text: str) -> dict[str, object]:
    """Return a deterministic manifest without changing the supplied text."""
    return _process(text)[1]


def clean_text(text: str) -> tuple[str, dict[str, object]]:
    """Return a cleaned working copy and its deterministic manifest."""
    return _process(text)


class InputTooLargeError(ValueError):
    """Raised when input exceeds the documented byte cap."""


class UnsafeInputPathError(ValueError):
    """Raised when path input is not a stable regular file."""


def _read_limited_bytes(stream) -> bytes:
    data = stream.read(MAX_INPUT_BYTES + 1)
    if len(data) > MAX_INPUT_BYTES:
        raise InputTooLargeError
    return data


def _open_regular_file(path: str):
    before_open = os.lstat(path)
    if not stat.S_ISREG(before_open.st_mode):
        raise UnsafeInputPathError

    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NONBLOCK", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        after_open = os.fstat(descriptor)
        if (
            not stat.S_ISREG(after_open.st_mode)
            or before_open.st_dev != after_open.st_dev
            or before_open.st_ino != after_open.st_ino
        ):
            raise UnsafeInputPathError
        return os.fdopen(descriptor, "rb")
    except BaseException:
        os.close(descriptor)
        raise


def _read_input(path: str) -> str:
    if path == "-":
        data = _read_limited_bytes(sys.stdin.buffer)
    else:
        with _open_regular_file(path) as source:
            data = _read_limited_bytes(source)
    return data.decode("utf-8")


def _write_json(stream, value: dict[str, object]) -> None:
    json.dump(value, stream, ensure_ascii=True, separators=(",", ":"))
    stream.write("\n")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect or clean deterministic Unicode text artifacts."
    )
    subparsers = parser.add_subparsers(dest="operation", required=True)

    inspect_parser = subparsers.add_parser("inspect")
    inspect_parser.add_argument("path", nargs="?", default="-")

    clean_parser = subparsers.add_parser("clean")
    clean_parser.add_argument("--stats", action="store_true")
    clean_parser.add_argument("path", nargs="?", default="-")
    return parser


def main(arguments: list[str] | None = None) -> int:
    args = _parser().parse_args(arguments)
    try:
        text = _read_input(args.path)
        cleaned, manifest = clean_text(text)
    except InputTooLargeError:
        sys.stderr.write(
            f"text_hygiene: input exceeds {MAX_INPUT_BYTES}-byte limit\n"
        )
        return 2
    except UnsafeInputPathError:
        sys.stderr.write(
            "text_hygiene: path input must be a regular file and not a symbolic link\n"
        )
        return 2
    except UnicodeDecodeError:
        sys.stderr.write("text_hygiene: invalid UTF-8 input\n")
        return 2
    except OSError as error:
        sys.stderr.write(f"text_hygiene: could not read input: {error}\n")
        return 2
    except Exception as error:
        sys.stderr.write(f"text_hygiene: processing failed: {error}\n")
        return 2

    try:
        if args.operation == "inspect":
            _write_json(sys.stdout, manifest)
            return 1 if manifest["summary"]["actionable"] else 0

        sys.stdout.buffer.write(cleaned.encode("utf-8"))
        sys.stdout.buffer.flush()
        if args.stats:
            _write_json(sys.stderr, manifest)
        return 0
    except (BrokenPipeError, OSError) as error:
        sys.stderr.write(f"text_hygiene: could not write output: {error}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
