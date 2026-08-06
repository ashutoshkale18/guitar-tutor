"""
LLM Client Service - Sends prompts to LM Studio and gets responses.
Direct HTTP calls, no subprocess needed.
"""

import requests
import logging

from config import LM_STUDIO_URL, LM_STUDIO_TIMEOUT, SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def build_prompt(
    user_text: str,
    chord_data: list[dict] | None = None,
    note_data: list[dict] | None = None,
    strum_data: dict | None = None
) -> str:
    """
    Build a combined prompt from user speech, chord data, note data, and strum data.
    
    Args:
        user_text: Transcribed speech from the user.
        chord_data: List of chord dicts from madmom.
        note_data: List of note dicts from madmom RNN.
        strum_data: Strum/tempo analysis dict from librosa.
        
    Returns:
        Combined prompt string for the LLM.
    """
    parts = []

    if chord_data:
        # Filter out "N" (no chord) segments for cleaner output
        meaningful_chords = [c for c in chord_data if c.get("chord", "N") != "N"]
        if meaningful_chords:
            chord_str = ", ".join(
                [f"{c['chord']} ({c['start']:.1f}s-{c['end']:.1f}s)" for c in meaningful_chords]
            )
            parts.append(f"[Detected chords from student's guitar playing]: {chord_str}")

    if note_data:
        # Show top notes (limit to avoid prompt bloat)
        note_summary = ", ".join(
            [f"{n['name']} (at {n['onset']:.1f}s)" for n in note_data[:20]]
        )
        unique_notes = sorted(list(set(n["name"] for n in note_data)))
        parts.append(f"[Detected individual notes]: {note_summary}")
        parts.append(f"[Unique notes played]: {', '.join(unique_notes)}")

    if strum_data:
        strum_parts = []
        if strum_data.get("tempo_bpm"):
            strum_parts.append(f"Tempo: {strum_data['tempo_bpm']:.0f} BPM")
        if strum_data.get("pattern"):
            strum_parts.append(f"Strum pattern: {strum_data['pattern']}")
        if strum_data.get("total_strums"):
            strum_parts.append(f"Total strums: {strum_data['total_strums']}")
        if strum_data.get("tempo_stability") is not None:
            stability_pct = strum_data['tempo_stability'] * 100
            strum_parts.append(f"Tempo stability: {stability_pct:.0f}%")
        if strum_parts:
            parts.append(f"[Strumming analysis]: {', '.join(strum_parts)}")

    if user_text and user_text.strip():
        parts.append(f"[Student's question]: {user_text}")

    if not parts:
        return "The student played guitar but didn't say anything. Provide brief encouraging feedback."

    return "\n".join(parts)


async def query_llm(
    user_text: str,
    chord_data: list[dict] | None = None,
    note_data: list[dict] | None = None,
    strum_data: dict | None = None
) -> str:
    """
    Query LM Studio with the combined user text and analysis data.
    
    Args:
        user_text: Transcribed user speech.
        chord_data: Optional list of chord detections.
        note_data: Optional list of note detections.
        strum_data: Optional strum/tempo analysis.
        
    Returns:
        LLM response text.
        
    Raises:
        RuntimeError: If LM Studio is unreachable or returns an error.
    """
    prompt = build_prompt(user_text, chord_data, note_data, strum_data)
    
    logger.info(f"Querying LLM with prompt: {prompt[:100]}...")
    
    payload = {
        "model": "local-llm",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }
    
    try:
        response = requests.post(
            LM_STUDIO_URL,
            json=payload,
            timeout=LM_STUDIO_TIMEOUT
        )
        response.raise_for_status()
        
        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        
        logger.info(f"LLM response: {reply[:80]}...")
        return reply
        
    except requests.exceptions.ConnectionError:
        raise RuntimeError("LM Studio is not running. Start LM Studio server on port 1234.")
    except requests.exceptions.Timeout:
        raise RuntimeError("LM Studio request timed out.")
    except KeyError:
        raise RuntimeError(f"Unexpected LM Studio response format: {response.text[:200]}")
    except Exception as e:
        raise RuntimeError(f"LLM query failed: {str(e)}")


async def check_llm_health() -> bool:
    """Check if LM Studio is reachable."""
    try:
        response = requests.get(
            "http://localhost:1234/v1/models",
            timeout=5
        )
        return response.status_code == 200
    except Exception:
        return False
