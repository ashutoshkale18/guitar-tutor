from config import SYSTEM_PROMPT

def build_system_prompt(profile: dict) -> str:
    """Builds a dynamic system prompt by appending the user's profile to the base prompt."""
    prefs = profile.get("preferences", {})
    learned_chords = profile.get("learned_chords", [])
    
    skill_level = prefs.get("skill_level", "Beginner")
    genre = prefs.get("genre", "Any")
    learning_style = prefs.get("learning_style", "Balanced")
    
    chords_str = ", ".join(learned_chords) if learned_chords else "None yet"
    
    dynamic_prompt = f"""{SYSTEM_PROMPT}

=======================================
STUDENT PROFILE (LONG-TERM MEMORY):
- Skill Level: {skill_level}
- Preferred Genre: {genre}
- Learning Style: {learning_style}
- Mastered Chords: {chords_str}
=======================================

IMPORTANT INSTRUCTIONS:
- Tailor your language and feedback strictly to the student's skill level ({skill_level}).
- If their learning style is "Encouraging", be extra positive. If "Strict", be direct and precise. If "Balanced", maintain a supportive but objective tone.
- Keep their preferred genre ({genre}) in mind when suggesting examples or techniques, if relevant.
- They have already mastered these chords: {chords_str}. You don't need to re-explain these unless they explicitly ask.
"""
    return dynamic_prompt
