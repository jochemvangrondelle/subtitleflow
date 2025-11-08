# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Judge service for selecting best translation candidates."""

import logging
import re

from subtitleflow.common.clients.ollama import OllamaClient
from subtitleflow.common.constants.prompts import JUDGE_INSTR
from subtitleflow.common.models.translation import Candidate
from subtitleflow.common.utils.text_processing import clean_ai_response

logger = logging.getLogger(__name__)


class JudgeService:
    """Service for judging and selecting best translation candidates."""

    def __init__(self, client: OllamaClient, judge_model: str) -> None:
        """
        Initialize judge service.

        Args:
            client: Ollama client
            judge_model: Model to use for judging
        """
        self.client = client
        self.judge_model = judge_model

    def select_best(
        self,
        original_text: str,
        candidates: list[Candidate],
        language: str | None = None,
        previous_translations: list[str] | None = None,
    ) -> Candidate:
        """
        Select best candidate from a list.

        Args:
            original_text: Original text being translated
            candidates: List of translation candidates
            language: Target language name
            previous_translations: Previously selected translations (for continuity)

        Returns:
            Best candidate
        """
        if len(candidates) == 1:
            logger.debug(f"Single candidate for: '{original_text[:240]}...'")
            return candidates[0]

        logger.debug(f"Judging {len(candidates)} candidates for: '{original_text[:240]}...'")

        # Build context from previous translations
        context_section = ""
        if previous_translations and len(previous_translations) > 0:
            # Show last 2-3 translations for context
            recent = previous_translations[-3:]
            context_section = (
                "\n\nPreviously selected translations (for continuity):\n"
                + "\n".join(f"  {t}" for t in recent)
            )

        # Build numbered candidates
        num_candidates = len(candidates)
        numbered = "\n\n".join([f"Candidate {i + 1}:\n{c.text}" for i, c in enumerate(candidates)])

        # Format instruction with number of candidates
        instr = JUDGE_INSTR.format(num_candidates=num_candidates)

        prompt = f"{instr}\n\nOriginal text:\n---\n{original_text}\n---{context_section}\n\nCandidates:\n{numbered}\n\nYour choice (number 1-{num_candidates} only):"

        # Judge only needs to output a number (1-2 tokens) + brief reasoning
        # Use small max_tokens to prevent runaway generation (was 16384!)
        resp = self.client.generate(
            self.judge_model,
            prompt,
            temperature=0.0,
            max_tokens=100,  # Enough for number + brief explanation
        )

        # Clean response (handles reasoning output from DeepSeek-R1 and other models)
        resp = clean_ai_response(resp)

        # Extract number from response (handle various formats)
        numbers = re.findall(r"\d+", resp)
        if numbers:
            choice = int(numbers[0])
            if 1 <= choice <= len(candidates):
                selected = candidates[choice - 1]
                logger.debug(f"Judge selected candidate {choice}: {selected.preview}")
                return selected
            logger.warning(
                f"⚠️ Judge returned invalid number {choice} (valid range: 1-{len(candidates)})"
            )

        # Fallback: check if response matches any candidate (old behavior)
        for i, c in enumerate(candidates):
            if resp.strip() == c.text.strip():
                logger.debug(f"Judge matched candidate {i + 1} via text match")
                return c

        # Final fallback: use first candidate (best model from translation)
        logger.warning(
            f"⚠️ Judge response invalid for [{language or 'unknown'}], using first candidate (best model)"
        )
        logger.warning(f"Expected: number 1-{len(candidates)}")
        logger.warning(f"Received: {resp}")
        return candidates[0]

    def select_best_multi(
        self,
        original_text: str,
        candidates_by_lang: dict[str, list[Candidate]],
        previous_translations_by_lang: dict[str, list[str]] | None = None,
    ) -> dict[str, Candidate]:
        """
        Select best candidates for multiple languages.

        Args:
            original_text: Original text being translated
            candidates_by_lang: Dict of language -> list of candidates
            previous_translations_by_lang: Dict of language -> previous translations

        Returns:
            Dict of language -> best candidate
        """
        results = {}

        for language, candidates in candidates_by_lang.items():
            prev_trans = None
            if previous_translations_by_lang:
                prev_trans = previous_translations_by_lang.get(language, [])

            best = self.select_best(
                original_text, candidates, language=language, previous_translations=prev_trans
            )
            results[language] = best

        return results
