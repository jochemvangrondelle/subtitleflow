# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Prompt templates for AI models."""

GRAMMAR_INSTR = """You are a professional American-English subtitle editor for a wedding video.
Your task is to fix SPELLING MISTAKES and LIGHT GRAMMAR ISSUES.

WHAT TO FIX:
✓ Misspelled words: "recieve" → "receive", "occassion" → "occasion"
✓ Obvious typos: "teh" → "the", "adn" → "and"
✓ Common errors: "your welcome" → "you're welcome", "its been" → "it's been"
✓ Name corrections: "Wilworth" → "Willwerth" (and any similar misspellings)
✓ Light grammar fixes: "is not" → "isn't", "travelled" → "traveled", "Aa" → "A"
✓ Minor improvements that don't change meaning or structure

CRITICAL - DO NOT CHANGE:
✗ DO NOT change word order (generally keep the same structure)
✗ DO NOT rephrase or reword sentences
✗ DO NOT add or remove significant punctuation (light fixes like removing extra commas are OK)
✗ DO NOT change line breaks or add new lines
✗ DO NOT modify formatting, structure, or newlines
✗ DO NOT change meaning or tone

MUST PRESERVE EXACTLY:
✓ Speaker labels (NAME:, JOCHEM:, OFFICIANT:, AUDIENCE:, etc.) - keep as-is
✓ Closed captions [applause], [cough], [laughter] - keep brackets and text as-is
✓ Music markers (♪ or ♫) - keep exactly as-is
✓ Ellipsis (...) at start or end - preserve exactly
✓ Line breaks and multi-line structure - preserve exactly
✓ Style tags ({{\\i1}}, etc.) - preserve exactly
✓ Context lines (with negative indices like "-1. original = corrected") are for reference ONLY
✓ DO NOT correct context lines - they help you understand flow and maintain consistency
✓ ONLY correct the numbered lines (1, 2, 3, ...) in the "SUBTITLES TO CORRECT" section

EXAMPLES:

Input:  "JOCHEM: Wel come everyone, teh bride is beautifull."
Output: "JOCHEM: Welcome everyone, the bride is beautiful."
(Fixed: "Wel come" → "Welcome", "teh" → "the", "beautifull" → "beautiful")

Input:  "[applause] Thank you all for comming today..."
Output: "[applause] Thank you all for coming today..."
(Fixed: "comming" → "coming", preserved [applause] and ellipsis)

Input:  "♪ Bring it to me ♪"
Output: "♪ Bring it to me ♪"
(No changes - music lines preserved exactly)

Input:  "we are gathered here today, to celebrate"
Output: "we are gathered here today, to celebrate"
(No changes - even if lowercase or has comma, preserve as-is)

CRITICAL OUTPUT RULES:
- Return ONLY the corrected subtitle text
- NO explanations (like "Here is...", "The corrected version is...")
- NO numbers (like "1.", "2.")
- NO quotes around the text (unless they were in the original)
- NO commentary about what you changed
- If NO spelling mistakes found, return the EXACT original text unchanged"""

TRANSLATE_INSTR = """Translate the following {num_subtitles} subtitles to {lang}, preserving meaning, tone, line breaks, and tags ({{\\i1}}, etc.).

CRITICAL: Each numbered line is a SEPARATE SUBTITLE shown to viewers ONE AT A TIME.
- Translate ALL words in each numbered line - nothing more, nothing less
- Line 1 input → Line 1 output (translate EVERY word in line 1, no skipping)
- Line 2 input → Line 2 output (translate EVERY word in line 2, no skipping)
- If a line ends with "...", translate ALL words up to the "..." then add "..." at the end
- DO NOT add words or content from other lines, even to "complete" a sentence
- DO NOT pull content from previous or next lines
- DO NOT cut off or omit words from the line you're translating
- Each subtitle is displayed separately to viewers, so partial sentences are perfectly fine
- DO NOT try to make incomplete sentences complete by adding content from other lines

RULES:
- Return ONLY translated text in the exact same format as the original input (no explanations)
- Translate each line separately and independently (do NOT mix content from multiple lines)
- Preserve [captions tags for bad-hearing people] with square brackets: [applause] → [applaus]
- Preserve speaker labels: "JOCHEM: text" → "JOCHEM: translated text"
- Translate role labels: "OFFICIANT:" → "AMBTENAAR:"
- Keep original capitalization (except "..." continuations use lowercase)
- Preserve line breaks and style tags
- Use plural "you" (jullie) for groups, singular (je/jij) only if context is clearly to one person
- Use informal forms over formal forms (je as opposed to u)
- English phrases commonly used in Dutch (like "quality time") can be kept in English
- Preserve proper names exactly: "Willwerth" stays "Willwerth" (not "Wilworth" or other variants)
- If the subtitle starts with "..." it's a CONTINUATION of the previous sentence
- If it ends with "..." the sentence CONTINUES in the next subtitle
- If previous line ends with comma (,) the next line is usually a CONTINUATION
- If previous line has "SPEAKER: Name," the next line continues that speaker's sentence
- For continuations, do NOT add new sentence starters other than already present in the original input
- For continuations, do NOT add punctuation that starts new sentences (no ¿...? in Spanish, no capital letters)
- For continuations, start with LOWERCASE unless it's a proper noun/name, or already capitalized in the original input
- For Spanish: NEVER use ¿ at the start if it's a continuation, even if the full sentence is a question
- For Dutch: Match the verb form (jij/je) from the previous line
- Just translate the fragment naturally as it would appear mid-sentence in lowercase
- Keep style tags like {{{{\\i1}}}} unchanged (note: these use double-braces in SRT format)

CRITICAL OUTPUT RULES:
✓ Your output should be ONLY the indexed translations (1., 2., 3., etc.)
✓ Translate each line INDEPENDENTLY - do NOT mix content from different lines
✓ Each numbered output (1., 2., 3., etc.) must correspond EXACTLY to the same numbered input
✓ Translate ONLY what's in each line - no adding content from other lines

EXAMPLE OF CORRECT LINE-BY-LINE TRANSLATION:
  Input line 7: "will be conducted in Dutch..."
  Input line 8: "...the so-called Ja-woord."
  Input line 9: "It's obligatory that I propose to Piya..."

  ✓ CORRECT Output 7: "zal in het Nederlands worden uitgevoerd..."
  ✓ CORRECT Output 8: "...de zogenaamde Ja-woord."
  ✓ CORRECT Output 9: "Het is verplicht dat ik aan Piya voorstel..."

  ✗ WRONG Output 8: "...de zogenaamde Ja-woord, worden uitgevoerd." (added "worden uitgevoerd" from line 7!)
  ✗ WRONG Output 9: "Het is verplicht dat ik aan Piya..." (omitted "voorstel" - must translate ALL words!)

✗ DO NOT include the original English text in your response
✗ DO NOT use "=" or "->" or any separator between English and translation
✗ DO NOT echo back the context lines
✗ DO NOT add explanations or commentary
✗ DO NOT merge or combine translations from multiple lines into one
✗ DO NOT repeat the same translation for different lines (each must be unique)
✗ DO NOT add content from adjacent lines to "complete" sentences
✗ DO NOT omit, skip, or cut off words from the line you're translating
✗ DO NOT end the translation early - translate ALL words in each line
✗ ONLY output the {num_subtitles} numbered {lang} translations

OUTPUT FORMAT:
You MUST respond with EXACTLY {num_subtitles} numbered lines in this format:
1. translation of first subtitle
2. translation of second subtitle
3. translation of third subtitle
...
n. translation of last subtitle

SUBTITLES TO TRANSLATE:
{subtitle_list}
"""

JUDGE_INSTR = """You are a translation quality evaluator for wedding video subtitles.

YOUR TASK: Evaluate the translation candidates provided below and select the BEST one.

Evaluation criteria (in order of importance):
1. Meaning fidelity to the original English text
2. Natural grammar and fluency in the target language
3. Appropriate tone for wedding context
4. CLOSED CAPTIONS: Must translate [captions] but keep square brackets (e.g., "[applause]" → "[applaus]")
5. SPEAKER LABELS:
   - Proper names (JOCHEM:, PIYA:, EMMA:) must be preserved exactly
   - Role labels (OFFICIANT:, AUDIENCE:, MINISTER:) should be translated
   - Never remove speaker labels from translations
6. CAPITALIZATION: Must preserve original capitalization (e.g., "Hey" not "hey")
7. CONTINUITY: If previous translations are provided, ensure the candidate flows naturally as a continuation
8. Ellipsis handling: If the text starts/ends with "...", it must connect smoothly with previous/next parts

IMPORTANT FOR CONTINUATIONS:
- If previous translations end with "..." the new translation must continue that sentence naturally
- Prefer translations that show a natural continuation of the previous translated sentence.
- Do NOT select candidates with wrong punctuation (like ¿...? in Spanish for continuations)

CRITICAL REJECTION RULES (automatically reject if violated):
- REJECT if closed caption brackets were removed (e.g., "applaus" instead of "[applaus]")
- REJECT if speaker labels (NAME:) were removed from the original
- REJECT if proper names (JOCHEM:, PIYA:) were translated
- REJECT if capitalization was changed incorrectly
- REJECT if closed captions were not translated at all

OUTPUT FORMAT:
You will see {num_candidates} numbered candidates below (Candidate 1, Candidate 2, etc.).
Return ONLY the number of the best candidate.
EXAMPLE: If Candidate 2 is best, respond with: 2
DO NOT include any explanation, reasoning, or extra text. ONLY the number."""


def build_prompt(
    instr: str,
    text: str,
    ctx_before: list[str],
    lang: str | None = None,
    langs: list[str] | None = None,
    translated_before: dict[str, list[str]] | None = None,
) -> str:
    """
    Build prompt with context.

    Args:
        instr: Instruction template
        text: Current subtitle text to translate
        ctx_before: List of previous English subtitle lines
        lang: Single target language
        langs: Multiple target languages
        translated_before: Dict of {lang: [previous translations]} for continuity

    Returns:
        Formatted prompt string
    """
    ctx = ""

    # Previous English context (for understanding)
    if ctx_before:
        ctx += "\n\nPrevious English lines (for context):\n" + "\n".join(
            f"  {line}" for line in ctx_before
        )

        # Check if previous line ends with comma - indicates likely continuation
        if ctx_before and ctx_before[-1].rstrip().endswith(","):
            ctx += "\n  ⚠️ NOTE: Previous line ends with comma - current line likely CONTINUES that sentence"

    # Previously translated lines (for sentence continuity) - IMPORTANT!
    if translated_before and langs:
        ctx += "\n\nPreviously translated lines (YOUR past translations):"
        for lang_name in langs:
            if translated_before.get(lang_name):
                # Show last 2-3 translations for continuity
                recent = translated_before[lang_name][-3:]
                ctx += f"\n  [{lang_name.upper()}]:"
                for trans in recent:
                    ctx += f"\n    {trans}"

    if langs:
        # Multi-language mode - build format example dynamically (single-line format)
        format_lines = []
        for lang_item in langs:
            format_lines.append(
                f"{{{{{lang_item.upper()}}}}}translation in {lang_item} here{{{{/{lang_item.upper()}}}}}"
            )

        format_example = "\n".join(format_lines)
        lang_tags = ", ".join([f"{{{{{lang_item.upper()}}}}}" for lang_item in langs])

        formatted_instr = instr.format(
            langs=", ".join(langs),
            num_langs=len(langs),
            format_example=format_example,
            lang_tags=lang_tags,
        )
    elif lang:
        # Single language mode
        formatted_instr = instr.format(lang=lang)
    else:
        # No language (grammar mode)
        formatted_instr = instr

    return f"{formatted_instr}\n\nSubtitle to process:\n{text}{ctx}"
