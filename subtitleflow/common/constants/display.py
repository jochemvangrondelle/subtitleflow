# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Display formatting constants."""

from rich.rule import Rule

# Separators for prompts and logs
SEPARATOR = "=" * 60
SEPARATOR_DOUBLE = "=" * 60
SEPARATOR_THIN = "━" * 60

# Rich display elements
RULER = Rule(style="dim")

# Common display strings
ARROW_FIX = "--FIX>"
ARROW_TRANSLATE = "--{lang}>"  # Format with language code

# Table column names
COL_INDEX = "Index"
COL_ORIGINAL = "Original"
COL_CORRECTED = "Corrected"
COL_TRANSLATION = "Translation"
COL_ARROW = "Arrow"

# Styles
STYLE_DIM = "dim"
STYLE_BOLD = "bold"
STYLE_CYAN = "cyan"
STYLE_YELLOW = "yellow"
STYLE_GREEN = "green"
STYLE_RED = "red"
STYLE_MAGENTA = "magenta"
STYLE_BLUE = "blue"

# Panel titles
PANEL_TRANSLATIONS = "[bold magenta]Translations: {model} → {language}[/bold magenta]"
