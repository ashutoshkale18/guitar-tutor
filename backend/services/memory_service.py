from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.dialects.mysql import insert
from database.models import UserMemory

async def get_user_profile(user_id: str, db: AsyncSession) -> dict:
    """Fetch all memories for a user and return as a structured dictionary."""
    result = await db.execute(select(UserMemory).where(UserMemory.user_id == user_id))
    memories = result.scalars().all()
    
    profile = {
        "preferences": {},
        "learned_chords": [],
        "chord_counts": {}
    }
    
    for mem in memories:
        if mem.memory_type == "preference":
            profile["preferences"][mem.key] = mem.value
        elif mem.memory_type == "learned_chords":
            if mem.value == "true":
                profile["learned_chords"].append(mem.key)
        elif mem.memory_type == "chord_count":
            profile["chord_counts"][mem.key] = int(mem.value)
            
    # Default preferences if missing
    if "skill_level" not in profile["preferences"]:
        profile["preferences"]["skill_level"] = "Beginner"
    if "genre" not in profile["preferences"]:
        profile["preferences"]["genre"] = "Any"
    if "learning_style" not in profile["preferences"]:
        profile["preferences"]["learning_style"] = "Balanced"
        
    return profile

async def update_user_preference(user_id: str, key: str, value: str, db: AsyncSession):
    """Upsert a user preference (e.g., genre, skill_level)."""
    stmt = insert(UserMemory).values(
        user_id=user_id,
        memory_type="preference",
        key=key,
        value=value
    )
    # MySQL ON DUPLICATE KEY UPDATE
    stmt = stmt.on_duplicate_key_update(value=stmt.inserted.value)
    await db.execute(stmt)
    await db.commit()

async def record_detected_chords(user_id: str, chords: list[str], required_plays: int = 3, db: AsyncSession = None):
    """Increment play counts for chords, and mark as learned if they hit the threshold."""
    if not chords or not db:
        return
        
    # Get current counts and learned status
    result = await db.execute(select(UserMemory).where(
        UserMemory.user_id == user_id, 
        UserMemory.memory_type.in_(["chord_count", "learned_chords"])
    ))
    memories = result.scalars().all()
    
    counts = {}
    learned = set()
    for mem in memories:
        if mem.memory_type == "chord_count":
            counts[mem.key] = int(mem.value)
        elif mem.memory_type == "learned_chords":
            learned.add(mem.key)
            
    for chord in set(chords):
        if chord in learned:
            continue
            
        new_count = counts.get(chord, 0) + 1
        
        # Upsert the new count
        stmt = insert(UserMemory).values(
            user_id=user_id,
            memory_type="chord_count",
            key=chord,
            value=str(new_count)
        )
        stmt = stmt.on_duplicate_key_update(value=stmt.inserted.value)
        await db.execute(stmt)
        
        # If threshold reached, mark as learned
        if new_count >= required_plays:
            stmt_learn = insert(UserMemory).values(
                user_id=user_id,
                memory_type="learned_chords",
                key=chord,
                value="true"
            )
            stmt_learn = stmt_learn.on_duplicate_key_update(value=stmt_learn.inserted.value)
            await db.execute(stmt_learn)
            
    await db.commit()
