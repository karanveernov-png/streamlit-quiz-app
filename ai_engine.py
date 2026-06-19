"""
ai_engine.py — All Groq/OpenRouter AI calls: question generation,
validation/repair pipeline, AI hints, AI study tips, custom-topic
question generation, and YouTube resource generation for custom topics.
"""
import json
import re
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import groq_client, openrouter_client, GROK_MODEL, OPENROUTER_MODEL, MAX_TOKENS
from data import PRESET_QUESTIONS

# ── JSON / API call helpers ──────────────────────────────────────────────
def _clean_json_text(text):
    """Robustly strip markdown fences and extract the JSON object/array."""
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ``` fences
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```\s*$", "", text)
    text = text.strip()
    # Extract from first { or [ to last } or ]
    start = min(
        (text.find("{") if text.find("{") != -1 else len(text)),
        (text.find("[") if text.find("[") != -1 else len(text)),
    )
    if start < len(text):
        text = text[start:]
    # Find the matching closing bracket
    for end_char, open_char in [("}", "{"), ("]", "[")]:
        if text.startswith(open_char):
            depth, last = 0, 0
            for i, c in enumerate(text):
                if c == open_char: depth += 1
                elif c == end_char:
                    depth -= 1
                    if depth == 0: last = i; break
            text = text[:last+1]
            break
    return text


def _call_api(api_client, model, prompt, max_tokens=MAX_TOKENS, retries=2):
    """Call a single API client and return parsed JSON, or raise on failure.
    Retries once with a stricter reminder if JSON parse fails first time."""
    system_msg = (
        "You are a precise quiz generator. "
        "Output ONLY valid raw JSON — no markdown, no code fences, no explanation, "
        "no text before or after the JSON. The first character of your response must be { or [."
    )
    last_err = None
    for attempt in range(retries):
        try:
            chat_completion = api_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user",   "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.2,  # Lower temp = more deterministic, more accurate
            )
            text = chat_completion.choices[0].message.content
            text = _clean_json_text(text)
            return json.loads(text)
        except json.JSONDecodeError as e:
            last_err = e
            # On retry, add a stricter reminder
            prompt = prompt + "\n\nCRITICAL: Return ONLY the JSON object. No extra text."
            continue
    raise last_err


def _build_question_prompt(subj, difficulty, count=5):
    """Build a highly structured, accurate prompt for one difficulty level."""
    diff_guidance = {
        "Easy":   "fundamental facts, basic definitions, and simple recall. Suitable for beginners.",
        "Medium": "conceptual understanding, application, and cause-effect reasoning.",
        "Hard":   "deep analysis, nuanced distinctions, advanced terminology, and multi-step reasoning.",
    }[difficulty]

    return (
        f"Generate exactly {count} multiple-choice quiz questions about '{subj}' at {difficulty} difficulty.\n"
        f"{difficulty} questions should test: {diff_guidance}\n\n"
        "STRICT RULES — violating ANY rule means the question is WRONG:\n"
        "  1. Every question has exactly 4 options: A, B, C, D.\n"
        "  2. ALL FOUR option values MUST be completely different — never repeat.\n"
        "  3. Only ONE option is correct. The other three are clearly wrong but plausible.\n"
        "  4. The 'answer' field must be the letter (A/B/C/D) that holds the correct value.\n"
        "  5. Vary which letter is correct — use A, B, C, D roughly equally across questions.\n"
        "  6. Explanation format EXACTLY: 'The correct answer is [LETTER] - [VALUE], because [2-sentence reason].'\n"
        "  7. The explanation letter and value MUST match the answer field.\n"
        "  8. Questions must be factually accurate and unambiguous.\n\n"
        "Return ONLY a raw JSON array of objects (no markdown, no fences, no extra text):\n"
        '[\n'
        '  {"question": "...", "options": {"A": "...", "B": "...", "C": "...", "D": "..."}, '
        '"answer": "C", "explanation": "The correct answer is C - [value], because ..."}\n'
        ']\n\n'
        "EXAMPLE (for reference only — generate about the actual subject, NOT this example):\n"
        '{"question": "What is the powerhouse of the cell?", '
        '"options": {"A": "Nucleus", "B": "Ribosome", "C": "Mitochondria", "D": "Golgi apparatus"}, '
        '"answer": "C", '
        '"explanation": "The correct answer is C - Mitochondria, because mitochondria produce ATP through cellular respiration. They convert nutrients into usable energy for the cell."}'
    )


def _generate_one_difficulty(api_client, model, subj, difficulty, count=5):
    """Generate questions for ONE difficulty level. Returns (difficulty, validated_list) or raises."""
    prompt = _build_question_prompt(subj, difficulty, count)
    result = _call_api(api_client, model, prompt, max_tokens=1800)

    # Handle both array and {"Easy":[...]} response formats
    if isinstance(result, list):
        qs = result
    elif isinstance(result, dict):
        qs = result.get(difficulty, result.get(difficulty.lower(), []))
        if not qs:
            # Maybe the model returned the list under a random key
            for v in result.values():
                if isinstance(v, list) and len(v) > 0:
                    qs = v; break
    else:
        qs = []

    validated = _validate_questions(qs)
    return difficulty, validated


def refresh_subject_questions(subj):
    """
    Generate questions for all 3 difficulties IN PARALLEL using threads.
    Each difficulty is its own API call — faster and more focused.
    Stores results in session_state as q_cache_{subj}_{difficulty}.
    Returns True on success, False on failure.
    """
    client = groq_client or openrouter_client
    model  = GROK_MODEL if groq_client else OPENROUTER_MODEL
    if client is None:
        return False

    difficulties = ["Easy", "Medium", "Hard"]
    stored = 0

    # Run 3 API calls concurrently
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(_generate_one_difficulty, client, model, subj, diff): diff
            for diff in difficulties
        }
        for future in as_completed(futures):
            try:
                diff, validated = future.result()
                if validated:
                    st.session_state[f"q_cache_{subj}_{diff}"] = validated
                    stored += 1
            except Exception:
                pass

    # Fallback: if parallel failed, try sequential with the other client
    if stored == 0:
        fallback_client = openrouter_client if groq_client else None
        fallback_model  = OPENROUTER_MODEL  if groq_client else None
        if fallback_client:
            for diff in difficulties:
                try:
                    _, validated = _generate_one_difficulty(fallback_client, fallback_model, subj, diff)
                    if validated:
                        st.session_state[f"q_cache_{subj}_{diff}"] = validated
                        stored += 1
                except Exception:
                    pass

    return stored > 0


def get_ai_study_tip(subj, diff, score, total):
    """Use the AI API to generate a personalised study tip for the result page."""
    pct = int((score / total) * 100) if total > 0 else 0
    prompt = (
        f"A student just completed a {diff}-difficulty quiz on {subj} and scored {score}/{total} ({pct}%).\n"
        "Write a SHORT, encouraging, personalised study tip (3-4 sentences max). "
        "Mention one specific concept or area from this subject they should focus on next. "
        "Keep it warm, motivating, and actionable. No bullet points, just flowing text."
    )
    client = groq_client or openrouter_client
    model  = GROK_MODEL if groq_client else OPENROUTER_MODEL
    if client is None:
        return None
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.8,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return None


def get_ai_hint(question_text, options_dict):
    """Generate a short hint for the current question without revealing the answer."""
    opts_str = " | ".join(f"{k}: {v}" for k, v in options_dict.items())
    prompt = (
        f"Question: {question_text}\n"
        f"Options: {opts_str}\n\n"
        "Give a SHORT hint (1-2 sentences) that helps the student think toward the correct answer "
        "WITHOUT directly stating or spelling out the answer. "
        "Focus on the key concept or elimination strategy. Be concise and clever."
    )
    client = groq_client or openrouter_client
    model  = GROK_MODEL if groq_client else OPENROUTER_MODEL
    if client is None:
        return "💡 Think carefully about each option — eliminate the clearly wrong ones first!"
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return "💡 Think carefully about each option — eliminate the clearly wrong ones first!"

# ── Question validation / repair pipeline, custom-topic generation,
# and extended Hard-mode question helpers ───────────────────────────────
def _shuffle_options(q):
    """
    Randomly reassign A/B/C/D labels to the option values so the correct
    answer is never biased to a particular letter.  Updates q["answer"] and
    the letter reference in q["explanation"] to match the new assignment.
    """
    import random as _random, re as _re3

    opts      = q["options"]
    ans_letter = q["answer"]
    ans_value  = opts[ans_letter]

    values = list(opts.values())
    _random.shuffle(values)

    letters = ["A", "B", "C", "D"]
    new_opts = dict(zip(letters, values))

    # Find which letter now holds the correct value
    new_ans = next(l for l, v in new_opts.items() if v == ans_value)

    # Update explanation letter reference (e.g. "answer is C" → "answer is B")
    expl = q.get("explanation", "")
    expl = _re3.sub(
        r"((?:correct )?answer is\s+)[A-D]",
        lambda m: m.group(1) + new_ans,
        expl, flags=_re3.IGNORECASE
    )

    q["options"]      = new_opts
    q["answer"]       = new_ans
    q["explanation"]  = expl
    return q


def _deduplicate_options(q):
    """
    Detect duplicate option values (the A==C bug) and replace them with
    clearly distinct placeholders so the question is still usable.

    Key rule: ALWAYS keep the answer letter's value intact.
    Any other letter that duplicates the answer letter's value is replaced.
    If two NON-answer letters duplicate each other, replace the later one.
    Returns the fixed question, or None if it cannot be salvaged.
    """
    import random as _random2

    opts = q["options"]
    ans  = q["answer"]

    placeholders = [
        "None of the above", "All of the above",
        "Cannot be determined", "Insufficient information",
        "Not applicable", "Other"
    ]
    _random2.shuffle(placeholders)

    # Build a canonical mapping: value → the ONE letter that should keep it.
    # The answer letter always wins; for duplicates among wrong options,
    # the first occurrence wins.
    keep = {}   # normalised_value → letter to keep
    replace = []  # letters that must be replaced

    # Process answer letter first so it always wins
    ans_val_norm = opts[ans].strip().lower()
    keep[ans_val_norm] = ans

    for letter in ["A", "B", "C", "D"]:
        if letter == ans:
            continue
        val_norm = opts[letter].strip().lower()
        if val_norm in keep:
            replace.append(letter)   # duplicate — must be replaced
        else:
            keep[val_norm] = letter

    if not replace:
        return q   # no duplicates

    # Collect values already legitimately used so placeholders are truly distinct
    used_vals = {opts[l].strip().lower() for l in ["A", "B", "C", "D"] if l not in replace}
    ph_iter = iter(p for p in placeholders if p.strip().lower() not in used_vals)

    for letter in replace:
        try:
            opts[letter] = next(ph_iter)
        except StopIteration:
            return None   # ran out of placeholders — drop the question

    q["options"] = opts
    return q


def _validate_questions(questions):
    """
    Full pipeline per question:
      1. Structural check (A-D present, answer letter valid)
      2. Deduplicate options  (fix A==C bug)
      3. Repair answer/explanation mismatch
      4. Shuffle option labels  (eliminate letter bias)
    """
    valid = []
    for q in questions:
        try:
            opts = q.get("options", {})
            ans  = q.get("answer", "").strip().upper()
            if ans not in ("A", "B", "C", "D"):
                continue
            if not all(k in opts for k in ("A", "B", "C", "D")):
                continue
            q["answer"] = ans

            # Step 2 — remove duplicate option values
            q = _deduplicate_options(q)
            if q is None:
                continue   # unsalvageable, skip

            # Step 3 — fix answer/explanation letter mismatch
            q = _repair_question(q)

            # Step 4 — shuffle labels so correct answer isn't always C
            q = _shuffle_options(q)

            valid.append(q)
        except Exception:
            continue
    return valid


def _repair_question(q):
    """
    Detect and fix the AI bug where options[answer] does not match the correct
    value described in the explanation.

    Uses ONE reliable strategy:
      Parse 'correct answer is X - VALUE' from the explanation, then find
      whichever option letter *actually holds that VALUE* in options{}.
      Update q["answer"] to that letter (and sync the letter in the explanation).

    Strategy A (numeric regex) is intentionally absent — it misreads fractions
    such as 1/4 as the integer 1, corrupting math questions.

    Double-check rule: if stated_val is not found in ANY option we leave the
    question untouched rather than guessing.
    """
    import re as _re2

    ans  = q["answer"]
    opts = q["options"]
    expl = q.get("explanation", "")

    # Parse "correct answer is X - VALUE" (dash, em-dash, colon, en-dash)
    m = _re2.search(
        r"correct answer is\s+([A-D])\s*[\u2014\-:\u2013]\s*([^,\.;]+)",
        expl, _re2.IGNORECASE
    )
    if not m:
        return q  # no structured explanation — leave unchanged

    stated_val = m.group(2).strip().rstrip(".,; ")

    # Find which option letter actually holds stated_val (exact, case-insensitive)
    matched_letter = None
    for letter, opt_val in opts.items():
        if opt_val.strip().lower() == stated_val.lower():
            matched_letter = letter
            break

    if matched_letter is None:
        # stated_val not in any option — explanation may be garbled; do not corrupt
        return q

    # If current answer already holds the right value, nothing to fix
    if opts.get(ans, "").strip().lower() == stated_val.lower():
        return q

    # Fix: update answer letter and sync the letter reference in explanation
    q["answer"] = matched_letter
    q["explanation"] = _re2.sub(
        r"(correct answer is\s+)[A-D]",
        lambda mx: mx.group(1) + matched_letter,
        expl, flags=_re2.IGNORECASE
    )
    return q


def _build_custom_question_prompt(subj_name, topic, difficulty, count=5):
    """Same idea as _build_question_prompt but for a user-typed custom subject/topic."""
    diff_guidance = {
        "Easy":   "basic facts and definitions suitable for beginners.",
        "Medium": "application, reasoning, and conceptual understanding.",
        "Hard":   "advanced analysis, edge cases, and expert-level knowledge.",
    }[difficulty]
    return (
        f"Generate exactly {count} multiple-choice quiz questions about the topic '{topic}' "
        f"in the subject '{subj_name}' at {difficulty} difficulty.\n"
        f"{difficulty} questions should test: {diff_guidance}\n\n"
        "STRICT RULES:\n"
        "  1. Every question has exactly 4 options: A, B, C, D.\n"
        "  2. ALL FOUR options MUST be different — never repeat a value.\n"
        "  3. Only ONE option is correct. The other three are plausible but wrong.\n"
        "  4. 'answer' must be the LETTER of the correct option.\n"
        "  5. Vary which letter is correct — distribute A/B/C/D roughly equally.\n"
        "  6. Explanation EXACTLY: 'The correct answer is [LETTER] - [VALUE], because [reason].'\n"
        "  7. Questions must be factually accurate and unambiguous.\n\n"
        "Return ONLY a raw JSON array (no markdown, no fences):\n"
        '[{"question": "...", "options": {"A": "...", "B": "...", "C": "...", "D": "..."}, '
        '"answer": "B", "explanation": "The correct answer is B - [value], because ..."}]'
    )


def generate_custom_questions(subj_name, topic):
    """
    AI generates 5 Easy + 5 Medium + 5 Hard MCQs for a user-defined subject & topic.
    Uses parallel API calls per difficulty for speed and accuracy.
    Cache key: q_cache_CUSTOM_{subj_name}_{topic}_{difficulty}
    Returns True on success, False on failure.
    """
    client = groq_client or openrouter_client
    model  = GROK_MODEL if groq_client else OPENROUTER_MODEL
    if client is None:
        return False

    difficulties = ["Easy", "Medium", "Hard"]
    stored = 0
    cache_key_prefix = f"q_cache_CUSTOM_{subj_name}_{topic}"

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(_call_api, client, model, _build_custom_question_prompt(subj_name, topic, diff), 1800): diff
            for diff in difficulties
        }
        for future in as_completed(futures):
            diff = futures[future]
            try:
                result = future.result()
                # Handle array or dict
                if isinstance(result, list):
                    qs = result
                elif isinstance(result, dict):
                    qs = result.get(diff, [])
                else:
                    qs = []
                validated = _validate_questions(qs)
                if validated:
                    st.session_state[f"{cache_key_prefix}_{diff}"] = validated
                    stored += 1
            except Exception:
                pass

    return stored > 0

def generate_custom_yt_resources(subj_name, topic):
    """
    Use AI to generate 4 YouTube search resource cards for a custom subject+topic.
    Returns a list of dicts matching the YOUTUBE_RESOURCES format, or [].
    """
    prompt = (
        f"Generate exactly 4 YouTube study resource cards for the subject '{subj_name}' and topic '{topic}'.\n"
        "Return ONLY a raw JSON array (no markdown, no code fences) like this:\n"
        "[{\"icon\": \"📘\", \"title\": \"Short card title (max 5 words)\", "
        "\"desc\": \"One sentence description\", "
        # FIX: Removed the markdown brackets and parentheses from the URL example
        "\"url\": \"https://www.youtube.com/results?search_query=relevant+search+terms\", "
        "\"tag\": \"Short Tag\"}]\n"
        "Make the search_query URL-encoded with + between words. "
        "Use 4 different learning angles: full course, beginner tutorial, exam prep, and advanced deep-dive."
    )
    client = groq_client or openrouter_client
    model  = GROK_MODEL if groq_client else OPENROUTER_MODEL
    
    if client is None:
        return []
        
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Reply with raw JSON only. No markdown, no code fences, no extra text."},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=600,
            temperature=0.4,
        )
        text = resp.choices[0].message.content.strip()
        text = re.sub(r"```[a-z]*", "", text).replace("```", "").strip()
        cards = json.loads(text)
        
        if isinstance(cards, list) and len(cards) > 0:
            # Sanitize URLs: AI sometimes wraps them in markdown [text](url)
            for card in cards:
                raw_url = str(card.get("url", "")).strip()
                md_match = re.search(r'https?://[^\s\)\"\'\]]+', raw_url)
                if md_match:
                    card["url"] = md_match.group(0)
                elif not raw_url.startswith("http"):
                    fallback_q = "+".join(card.get("title", "study").split())
                    card["url"] = f"https://www.youtube.com/results?search_query={fallback_q}"
            return cards[:4]

    except Exception as e:
        # It's often helpful to print the error to your console during development
        print(f"Error generating YouTube resources: {e}") 
        pass
        
    return []

def get_extended_hard_questions(subj, want_count):
    """
    Return Hard-difficulty questions for a preset subject, topped up to `want_count`.
    Reuses existing preset/cached Hard questions first and only asks the AI for
    the extra ones that are missing. Result is cached so it isn't regenerated
    every time the user replays the same subject.
    """
    base_key = f"q_cache_{subj}_Hard"
    if base_key in st.session_state:
        base = list(st.session_state[base_key])
    elif subj in PRESET_QUESTIONS:
        base = list(PRESET_QUESTIONS[subj]["Hard"])
    else:
        base = []

    if len(base) >= want_count:
        return base[:want_count]

    extended_key = f"{base_key}_x{want_count}"
    if extended_key in st.session_state:
        return st.session_state[extended_key]

    client = groq_client or openrouter_client
    model  = GROK_MODEL if groq_client else OPENROUTER_MODEL
    extra = []
    if client:
        try:
            _, extra = _generate_one_difficulty(client, model, subj, "Hard", count=want_count - len(base))
        except Exception:
            extra = []

    seen = {q["question"] for q in base}
    for q in extra:
        if q["question"] not in seen:
            base.append(q)
            seen.add(q["question"])

    st.session_state[extended_key] = base
    return base


def get_extended_custom_hard_questions(subj_name, topic, want_count):
    """Same idea as get_extended_hard_questions but for a custom AI-generated subject."""
    base_key = f"q_cache_CUSTOM_{subj_name}_{topic}_Hard"
    base = list(st.session_state.get(base_key, []))

    if len(base) >= want_count:
        return base[:want_count]

    extended_key = f"{base_key}_x{want_count}"
    if extended_key in st.session_state:
        return st.session_state[extended_key]

    client = groq_client or openrouter_client
    model  = GROK_MODEL if groq_client else OPENROUTER_MODEL
    extra = []
    if client:
        try:
            prompt = _build_custom_question_prompt(subj_name, topic, "Hard", want_count - len(base))
            result = _call_api(client, model, prompt, max_tokens=1800)
            qs = result if isinstance(result, list) else (result.get("Hard", []) if isinstance(result, dict) else [])
            extra = _validate_questions(qs)
        except Exception:
            extra = []

    seen = {q["question"] for q in base}
    for q in extra:
        if q["question"] not in seen:
            base.append(q)
            seen.add(q["question"])

    st.session_state[extended_key] = base
    return base