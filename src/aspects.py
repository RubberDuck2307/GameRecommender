"""Aspect keyword vocabularies for Steam review analysis."""

GAMEPLAY_ASPECTS = {
    "combat": [
        "combat", "melee", "fighting", "weapons", "parry", "parrying",
        "blocking", "dodging", "combos", "duels", "brawling",
    ],
    "shooting": [
        "shooting", "gunplay", "guns", "gun", "firearms", "aiming", "recoil", "reload",
        "reloading", "ammo", "sniping", "headshots",
    ],
    "stealth": [
        "stealth", "sneaking", "sneak", "sneaky", "undetected", "concealment",
        "disguises", "infiltration", "pickpocketing", "lockpicking",
    ],
    "platforming": [
        "platforming", "platformer", "platformers", "jumping", "jumps", "parkour",
        "wallrunning", "grappling", "climbing", "mantling",
    ],
    "survival": [
        "survival", "surviving", "hunger", "starvation", "thirst", "shelter",
        "scavenging", "foraging", "hypothermia", "dehydration",
    ],
    "crafting": [
        "crafting", "craft", "recipes", "recipe", "blueprints", "smithing",
        "blacksmithing", "alchemy", "smelting", "forging", "crafting system",
    ],
    "sports": [
        "sport", "sports", "football", "soccer", "basketball", "tennis", "golf", "racing",
        "career mode",
    ],
    "strategy": ["strategy", "tactics", "tactical", "planning", "turns", "turn based", "tech tree"],
    "building": [
        "building", "construction", "base", "factories", "automation", "base building", "city builder",
    ],
    "horror": ["horror game", "horror", "scary", "jump scares", "creepy", "spooky", "fear", "terror", "survival horror", "resident evil", "zombies", "psychological"],
    "open_world": [
        "open world", "location", "locations", "exploration", "explorations",
        "explore", "exploring", "side quest", "side quests",
    ],
}

ASPECTS = {
    **GAMEPLAY_ASPECTS,
    "story": [
        "story", "plot", "narrative", "writing", "dialogue", "characters", "character",
        "quests", "quest", "ending", "lore", "cliché", "twists", "choices", "decision",
        "decisions", "backstory", "worldbuilding", "storytelling", "dialogues",
        "personalities",
    ],
    "graphics": [
        "graphics", "visuals", "textures", "lighting", "animation", "animations", "art",
        "scenery", "views", "effects", "cutscenes", "cutscene", "cinematics",
        "aesthetics", "pixel", "texture",
    ],
    "audio": [
        "audio", "sound", "sounds", "music", "soundtrack", "voice", "eargasm",
        "ambient", "songs", "soundtracks", "voice acting",
    ],
    "performance": [
        "performance", "optimization", "fps", "framerate", "stuttering", "lag", "bugs",
        "bug", "crashes", "crash", "loading", "stutters", "freeze", "freezes",
        "glitches", "glitch", "stability",
    ],
    "multiplayer": [
        "multiplayer", "friends", "server", "servers", "hackers", "online", "coop", "pvp",
        "co op", "split screen", "anti cheat"
    ],
    "modding": ["mod", "mods", "modding", "workshop"],
}
