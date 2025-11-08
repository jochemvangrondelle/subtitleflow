# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Rich display utilities for CLI - only used in CLI layer."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from subtitleflow.common.constants.display import (
    ARROW_FIX,
    ARROW_TRANSLATE,
    COL_ARROW,
    COL_CORRECTED,
    COL_INDEX,
    COL_ORIGINAL,
    COL_TRANSLATION,
    PANEL_TRANSLATIONS,
    STYLE_BLUE,
    STYLE_BOLD,
    STYLE_CYAN,
    STYLE_DIM,
    STYLE_GREEN,
    STYLE_YELLOW,
)
from subtitleflow.common.models.subtitle import Subtitle


def display_translation_batch(
    console: Console,
    batch: list[Subtitle],
    translations: list[str],
    context_display: list[tuple[int, str, str]],
    language: str,
) -> None:
    """
    Display translation batch with Rich tables (CLI only).

    Args:
        console: Rich console instance
        batch: Original subtitles
        translations: Translated texts
        context_display: Context items for display
        language: Target language
    """
    screen_width = console.width
    col_width = int((screen_width - 20) * 0.45)
    lang_code = language[:2].upper()
    arrow = ARROW_TRANSLATE.format(lang=lang_code)

    console.print(
        f"\n[green]✓ Successfully parsed batch with {len(translations)} translations[/green]\n"
    )

    # Display context
    if context_display:
        console.print("[bold]Context (previous translations):[/bold]")
        for neg_idx, orig, trans in context_display:
            ctx_table = Table.grid(padding=(0, 2), expand=True)
            ctx_table.add_column(COL_INDEX, style=f"{STYLE_DIM} italic", width=6, justify="right")
            ctx_table.add_column(
                COL_ORIGINAL,
                style=f"{STYLE_DIM} {STYLE_CYAN}",
                width=col_width,
                overflow="fold",
                max_width=col_width,
            )
            ctx_table.add_column(COL_ARROW, style=STYLE_DIM, width=8, justify="center")
            ctx_table.add_column(
                COL_TRANSLATION,
                style=f"{STYLE_DIM} {STYLE_YELLOW}",
                width=col_width,
                overflow="fold",
                max_width=col_width,
            )
            ctx_table.add_row(f"{neg_idx}.", orig, arrow, trans)
            console.print(ctx_table)
        console.print()

    # Display current batch
    for i, (sub, translation) in enumerate(zip(batch, translations, strict=False), 1):
        table = Table.grid(padding=(0, 2), expand=True)
        table.add_column(COL_INDEX, style=f"{STYLE_BOLD} {STYLE_DIM}", width=6, justify="right")
        table.add_column(
            COL_ORIGINAL,
            style=STYLE_CYAN,
            width=col_width,
            overflow="fold",
            max_width=col_width,
        )
        table.add_column(COL_ARROW, style=f"{STYLE_GREEN} {STYLE_BOLD}", width=8, justify="center")
        table.add_column(
            COL_TRANSLATION,
            style=STYLE_YELLOW,
            width=col_width,
            overflow="fold",
            max_width=col_width,
        )

        original_display = sub.content.replace("\n", "\\n")
        translation_display = translation.replace("\n", "\\n")

        table.add_row(f"{i}.", original_display, arrow, translation_display)
        console.print(table)


def display_correction_batch(
    console: Console,
    batch: list[Subtitle],
    corrections: list[str],
    batch_idx: int,
    total_batches: int,
    model_name: str,
) -> None:
    """
    Display corrections for a batch using Rich tables (CLI only).

    Args:
        console: Rich console instance
        batch: Original subtitles
        corrections: Corrected texts
        batch_idx: Current batch index (0-based)
        total_batches: Total number of batches
        model_name: Name of the model used
    """
    screen_width = console.width
    col_width = int((screen_width - 20) * 0.45)

    console.print(
        f"\n[green]✓ [{model_name}] Batch {batch_idx + 1}/{total_batches} corrections[/green]\n"
    )

    for i, (sub, corr) in enumerate(zip(batch, corrections, strict=False), 1):
        no_change = sub.content == corr

        table = Table.grid(padding=(0, 2), expand=True)
        table.add_column(
            COL_INDEX,
            style=f"{STYLE_BOLD} {STYLE_DIM}",
            width=6,
            justify="right",
        )
        table.add_column(
            COL_ORIGINAL,
            style=f"{STYLE_DIM} {STYLE_CYAN}" if no_change else STYLE_CYAN,
            width=col_width,
            overflow="fold",
            max_width=col_width,
        )
        table.add_column(
            COL_ARROW,
            style=STYLE_DIM if no_change else f"{STYLE_GREEN} {STYLE_BOLD}",
            width=8,
            justify="center",
        )
        table.add_column(
            COL_CORRECTED,
            style=STYLE_DIM if no_change else STYLE_YELLOW,
            width=col_width,
            overflow="fold",
            max_width=col_width,
        )

        original_display = sub.content.replace("\n", "\\n")
        corrected_display = corr.replace("\n", "\\n")

        table.add_row(f"{i}.", original_display, ARROW_FIX, corrected_display)
        console.print(table)

    console.print()


def display_context(
    console: Console,
    context_items: list[tuple[int, str, str]],
    col_width: int,
    context_type: str = "corrections",
) -> None:
    """
    Display context using Rich tables (CLI only).

    Args:
        console: Rich console instance
        context_items: List of (index, original, corrected/translated) tuples
        col_width: Column width for display
        context_type: Type of context ("corrections" or "translations")
    """
    if not context_items:
        return

    console.print(f"[bold]Context (previous {context_type}):[/bold]")
    for neg_idx, orig, corr in context_items:
        ctx_table = Table.grid(padding=(0, 2), expand=True)
        ctx_table.add_column(COL_INDEX, style=f"{STYLE_DIM} italic", width=6, justify="right")
        ctx_table.add_column(
            COL_ORIGINAL,
            style=f"{STYLE_DIM} {STYLE_CYAN}",
            width=col_width,
            overflow="fold",
            max_width=col_width,
        )
        ctx_table.add_column(COL_ARROW, style=STYLE_DIM, width=8, justify="center")
        ctx_table.add_column(
            COL_CORRECTED if context_type == "corrections" else COL_TRANSLATION,
            style=f"{STYLE_DIM} {STYLE_YELLOW}",
            width=col_width,
            overflow="fold",
            max_width=col_width,
        )
        ctx_table.add_row(f"{neg_idx}.", orig, ARROW_FIX, corr)
        console.print(ctx_table)
    console.print()


def display_judged_batch(
    console: Console,
    batch: list[Subtitle],
    corrections: list[str],
    batch_idx: int,
    total_batches: int,
    context_items: list[tuple[int, str, str]],
) -> None:
    """
    Display judged batch corrections with context (CLI only).

    Args:
        console: Rich console instance
        batch: Original subtitles
        corrections: Judged corrections
        batch_idx: Current batch index (0-based)
        total_batches: Total number of batches
        context_items: Context items for display
    """
    screen_width = console.width
    col_width = int((screen_width - 20) * 0.45)

    console.print(
        f"\n[green]✓ Successfully parsed batch with {len(corrections)} corrections[/green]\n"
    )

    display_context(console, context_items, col_width, context_type="corrections")

    for i, (sub, corrected) in enumerate(zip(batch, corrections, strict=False), 1):
        no_change = sub.content == corrected

        table = Table.grid(padding=(0, 2), expand=True)
        table.add_column(COL_INDEX, style=f"{STYLE_BOLD} {STYLE_DIM}", width=6, justify="right")
        table.add_column(
            COL_ORIGINAL,
            style=f"{STYLE_DIM} {STYLE_CYAN}" if no_change else STYLE_CYAN,
            width=col_width,
            overflow="fold",
            max_width=col_width,
        )
        table.add_column(
            COL_ARROW,
            style=STYLE_DIM if no_change else f"{STYLE_GREEN} {STYLE_BOLD}",
            width=8,
            justify="center",
        )
        table.add_column(
            COL_CORRECTED,
            style=STYLE_DIM if no_change else STYLE_YELLOW,
            width=col_width,
            overflow="fold",
            max_width=col_width,
        )

        original_display = sub.content.replace("\n", "\\n")
        corrected_display = corrected.replace("\n", "\\n")

        table.add_row(f"{i}.", original_display, ARROW_FIX, corrected_display)
        console.print(table)


def display_translation_panel(
    console: Console,
    output_lines: list[Text],
    model: str,
    language: str,
) -> None:
    """
    Display translations in a Rich panel (CLI only).

    Args:
        console: Rich console instance
        output_lines: List of Text objects to display
        model: Model name
        language: Target language
    """
    if not output_lines:
        return

    try:
        panel_height = max(10, int(console.height * 0.8))
    except Exception:
        panel_height = 30

    full_output = Text()
    for line in output_lines:
        full_output.append(line)
        full_output.append("\n")

    panel = Panel(
        full_output,
        title=PANEL_TRANSLATIONS.format(model=model, language=language),
        border_style=STYLE_BLUE,
        padding=(1, 2),
        height=panel_height,
    )
    console.print(panel)
