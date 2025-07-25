"""Tests for the ansi_output module."""

from __future__ import annotations

import logging

import pytest

from molecule.ansi_output import AnsiOutput, should_do_markup, to_bool


@pytest.mark.parametrize(
    ("input_value", "expected"),
    (
        (None, False),
        (True, True),
        (False, False),
        ("yes", True),
        ("YES", True),
        ("on", True),
        ("ON", True),
        ("1", True),
        ("true", True),
        ("TRUE", True),
        ("no", False),
        ("off", False),
        ("0", False),
        ("false", False),
        ("random", False),
        (1, True),
        (0, False),
        (42, False),
    ),
)
def test_to_bool(input_value: object, expected: bool) -> None:  # noqa: FBT001
    """Test to_bool function with various inputs."""
    assert to_bool(input_value) is expected


@pytest.mark.parametrize(
    ("env_vars", "expected"),
    (
        ({"NO_COLOR": "1"}, False),
        ({"FORCE_COLOR": "1"}, True),
        ({"TERM": "xterm-256color"}, True),
        ({"TERM": "dumb"}, False),
    ),
)
def test_should_do_markup(
    env_vars: dict[str, str],
    expected: bool,  # noqa: FBT001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test should_do_markup function with various environment variables."""
    # Clear all color-related environment variables first
    for var in ["NO_COLOR", "FORCE_COLOR", "PY_COLORS", "CLICOLOR", "ANSIBLE_FORCE_COLOR", "TERM"]:
        monkeypatch.delenv(var, raising=False)

    # Set the test environment variables
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    assert should_do_markup() is expected


def test_ansi_output_initialization() -> None:
    """Test AnsiOutput class initialization."""
    output = AnsiOutput()
    assert hasattr(output, "markup_enabled")
    assert hasattr(output, "markup_map")
    assert isinstance(output.markup_map, dict)


def test_ansi_color_constants() -> None:
    """Test that ANSI color constants are defined."""
    output = AnsiOutput()
    assert output.RESET == "\033[0m"
    assert output.RED == "\033[31m"
    assert output.GREEN == "\033[32m"
    assert output.BLUE == "\033[34m"
    assert output.BOLD == "\033[1m"
    assert output.DIM == "\033[2m"


@pytest.mark.parametrize(
    ("input_text", "expected_output"),
    (
        ("[red]Error message[/] with [bold]bold text[/]", "Error message with bold text"),
        ("Plain text message", "Plain text message"),
        ("[info]Running [scenario]test[/] > [action]create[/][/]", "Running test > create"),
    ),
)
def test_strip_markup(input_text: str, expected_output: str) -> None:
    """Test markup stripping functionality."""
    output = AnsiOutput()
    assert output.strip_markup(input_text) == expected_output


def test_process_markup_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test markup processing when markup is disabled."""
    monkeypatch.setenv("NO_COLOR", "1")
    output = AnsiOutput()

    text_with_markup = "[red]Error message[/] with [bold]bold text[/]"
    expected = "Error message with bold text"
    assert output.process_markup(text_with_markup) == expected


def test_process_markup_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test markup processing when markup is enabled."""
    # Clear NO_COLOR and set a color environment
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")
    output = AnsiOutput()

    text_with_markup = "[red]Error[/] message"
    result = output.process_markup(text_with_markup)

    # Should contain ANSI codes
    assert "\033[31m" in result  # Red color
    assert "\033[0m" in result  # Reset


def test_process_markup_with_unknown_tags(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test markup processing with unknown tags."""
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")
    output = AnsiOutput()

    text_with_unknown = "[unknown_tag]Text[/] with [red]known tag[/]"
    result = output.process_markup(text_with_unknown)

    # Should process known tags and ignore unknown ones
    assert "\033[31m" in result  # Red color for known tag
    assert "\033[0m" in result  # Reset
    assert "Text" in result
    assert "known tag" in result


@pytest.mark.parametrize(
    ("markup_enabled", "scenario_name", "expected_pattern"),
    (
        (False, "test_scenario", "[test_scenario]"),
        (True, "test_scenario", r"\033\[32m.*\[test_scenario\].*\033\[0m"),
    ),
)
def test_format_scenario(
    markup_enabled: bool,  # noqa: FBT001
    scenario_name: str,
    expected_pattern: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test scenario formatting with markup enabled/disabled."""
    if markup_enabled:
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.setenv("FORCE_COLOR", "1")
    else:
        monkeypatch.setenv("NO_COLOR", "1")

    output = AnsiOutput()
    result = output.format_scenario(scenario_name)

    if markup_enabled:
        assert "\033[32m" in result  # Green color
        assert "\033[0m" in result  # Reset
        assert "[test_scenario]" in result
    else:
        assert result == expected_pattern


@pytest.mark.parametrize(
    ("level_name", "level_no", "expected_ansi"),
    (
        ("INFO", logging.INFO, "\033[34m"),  # Blue for INFO
        ("WARNING", logging.WARNING, "\033[31m"),  # Red for WARNING
        ("ERROR", logging.ERROR, "\033[1m"),  # Bold for ERROR
    ),
)
def test_format_log_level_markup_enabled(
    level_name: str,
    level_no: int,
    expected_ansi: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test log level formatting when markup is enabled."""
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")
    output = AnsiOutput()

    result = output.format_log_level(level_name, level_no)
    assert expected_ansi in result
    assert "\033[0m" in result  # Reset


def test_format_log_level_markup_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test log level formatting when markup is disabled."""
    monkeypatch.setenv("NO_COLOR", "1")
    output = AnsiOutput()

    result = output.format_log_level("INFO", logging.INFO)
    assert result == "INFO    "  # 8 characters, left-aligned
    assert "\033[" not in result  # No ANSI codes


def test_markup_map_contains_expected_styles() -> None:
    """Test that markup_map contains expected style mappings."""
    output = AnsiOutput()

    # Test basic styles from Molecule's theme
    expected_styles = [
        "info",
        "warning",
        "danger",
        "scenario",
        "action",
        "logging.level.info",
        "logging.level.warning",
        "logging.level.error",
        "red",
        "green",
        "blue",
        "bold",
        "dim",
    ]

    for style in expected_styles:
        assert style in output.markup_map


def test_markup_map_values_are_ansi_codes() -> None:
    """Test that markup_map values are valid ANSI escape codes."""
    output = AnsiOutput()

    for ansi_code in output.markup_map.values():
        assert isinstance(ansi_code, str)
        if ansi_code:  # Some might be empty strings
            assert ansi_code.startswith("\033[")


def test_complex_markup_processing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test processing of complex markup with nested tags."""
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")
    output = AnsiOutput()

    complex_markup = "[info]Running [scenario]test[/] > [action]create[/][/]"
    result = output.process_markup(complex_markup)

    # Should contain multiple ANSI codes and resets
    assert result.count("\033[") > 1  # Multiple ANSI sequences
    assert "\033[0m" in result  # Reset codes
    assert "Running" in result
    assert "test" in result
    assert "create" in result
