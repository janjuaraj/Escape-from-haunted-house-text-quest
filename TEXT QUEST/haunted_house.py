
import random
import time
import json
import os

# --- GLOBAL VARIABLES ---
SAVE_FILE = "savegame.json"
INVENTORY = []
SCORE = 0
DEATHS = 0
HEALTH = 100
MAX_TRIES = 3
DIFFICULTY = "normal"
LOCK_ATTEMPTS = 3
RIDDLE_PENALTY = 20
GHOST_DAMAGE = 30

ROOMS = {
    "Dusty Room": ["Hallway", "Closet"],
    "Closet": [],
    "Hallway": ["Mirror Hall"],
    "Mirror Hall": ["Basement"],
    "Basement": []
}

# --- SAVE/LOAD FUNCTIONS ---
def save_game(current_room):
    global HEALTH, SCORE, DEATHS, INVENTORY
    data = {
        "HEALTH": HEALTH,
        "SCORE": SCORE,
        "DEATHS": DEATHS,
        "INVENTORY": INVENTORY,
        "current_room": current_room
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)
    print("💾 Game saved successfully.")

def load_game():
    global HEALTH, SCORE, DEATHS, INVENTORY
    if not os.path.exists(SAVE_FILE):
        return None
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
    HEALTH = data["HEALTH"]
    SCORE = data["SCORE"]
    DEATHS = data["DEATHS"]
    INVENTORY.clear()
    INVENTORY.extend(data["INVENTORY"])
    print(" Save file loaded.")
    return data["current_room"]

# --- UTILITY ---
def pause(seconds=1.5):
    time.sleep(seconds)

# --- RIDDLE HANDLING ---
def get_riddle(level):
    riddles = {
        "easy": {
            "riddle": "What has keys but can't open locks?",
            "answer": "piano"
        },
        "medium": {
            "riddle": "The more you take, the more you leave behind. What am I?",
            "answer": "footsteps"
        },
        "hard": {
            "riddle": "I speak without a mouth and hear without ears. What am I?",
            "answer": "echo"
        }
    }
    return riddles[level]["riddle"], riddles[level]["answer"]

def ask_riddle(level):
    global HEALTH, RIDDLE_PENALTY
    riddle, answer = get_riddle(level)
    print(f"\nRIDDLE: {riddle}")
    guess = input("Your answer: ").strip().lower()
    if guess == answer:
        print("Correct. The darkness pulls back slightly.")
        return True
    else:
        print(f"Wrong... Cold fear wraps around you. You lose {RIDDLE_PENALTY} health.")
        HEALTH -= RIDDLE_PENALTY
        return False

# --- GAME MECHANICS ---
def combination_lock():
    global HEALTH, SCORE, INVENTORY, LOCK_ATTEMPTS
    code = random.randint(191, 200)
    print("\nYou discover a chest with a glowing keypad.")
    print("A nearby note reads: 'The code is between 191 and 200.'")
    for _ in range(LOCK_ATTEMPTS):
        attempt = input("Enter the 3-digit code: ").strip()
        if attempt == str(code):
            print("The lock clicks! Inside is an Ancient Scroll.")
            INVENTORY.append("Ancient Scroll")
            SCORE += 10
            return True
        else:
            print("Incorrect. The lock hums angrily.")
            HEALTH -= 5
    print(f"The chest disappears into smoke... The code was {code}.")
    return False

def explore_room(room):
    global HEALTH, SCORE, INVENTORY, GHOST_DAMAGE
    print(f"\nYou enter the {room}...")
    pause()

    if room == "Closet":
        print("A skeleton drops with a clatter. You find a Rusty Key and a Health Potion.")
        INVENTORY.extend(["Rusty Key", "Health Potion"])
        SCORE += 10

    elif room == "Hallway":
        combination_lock()

    elif room == "Mirror Hall":
        print("A mirror flickers to life... glowing numbers appear: 731.")
        INVENTORY.append("Mirror Clue")
        INVENTORY.append("Torch")
        SCORE += 10

    elif room == "Basement":
        if "Torch" not in INVENTORY:
            print("It's too dark to see! You need a Torch.")
            return False

        print("A ghost blocks the final door. It speaks in riddles...")
        result = ask_riddle("hard")
        if result:
            print("The ghost vanishes into mist.")
            SCORE += 10
            code = input("Enter the 3-digit code: ").strip()
            if code == "731":
                print("The door creaks open. You escape the haunted house!")
                SCORE += 20
                return True
            else:
                print("Wrong code. The door locks permanently.")
                HEALTH -= GHOST_DAMAGE
                return False
        else:
            print("The ghost engulfs you...")
            HEALTH = 0
            return False

    return True

def choose_room(current_room):
    options = ROOMS[current_room]
    if not options:
        return None

    print("\nPaths available:")
    for i, opt in enumerate(options):
        print(f"{i + 1}. {opt}")

    choice = input("Choose a room number: ").strip()
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(options):
            return options[idx]

    print("Invalid choice.")
    return None

def use_items():
    global HEALTH, INVENTORY
    if "Health Potion" in INVENTORY and HEALTH <= 50:
        use = input("You have a Health Potion. Use it? (yes/no): ").strip().lower()
        if use == "yes":
            HEALTH = min(HEALTH + 40, 100)
            INVENTORY.remove("Health Potion")
            print("You feel restored. Health +40.")

def intro():
    print("\n🎮 Welcome to Text Quest: Escape the Haunted House 🎮")
    print("You awaken in a dusty, cold room. Whispers crawl along the walls...")
    pause()

# --- MAIN GAME LOOP ---
def main():
    global HEALTH, SCORE, DEATHS, INVENTORY, MAX_TRIES
    global DIFFICULTY, LOCK_ATTEMPTS, RIDDLE_PENALTY, GHOST_DAMAGE

    escaped = False
    current_room = "Dusty Room"

    # Difficulty Selection
    print("\nSelect Difficulty: easy / normal / hard")
    DIFFICULTY = input("Enter difficulty: ").strip().lower()

    if DIFFICULTY == "easy":
        HEALTH = 120
        MAX_TRIES = 5
        LOCK_ATTEMPTS = 5
        RIDDLE_PENALTY = 10
        GHOST_DAMAGE = 20
    elif DIFFICULTY == "hard":
        HEALTH = 80
        MAX_TRIES = 2
        LOCK_ATTEMPTS = 2
        RIDDLE_PENALTY = 30
        GHOST_DAMAGE = 50
    else:
        DIFFICULTY = "normal"
        HEALTH = 100
        MAX_TRIES = 3
        LOCK_ATTEMPTS = 3
        RIDDLE_PENALTY = 20
        GHOST_DAMAGE = 30

    # Load previous save or start new game
    if os.path.exists(SAVE_FILE):
        cont = input("Continue from last save? (yes/no): ").strip().lower()
        if cont == "yes":
            loaded_room = load_game()
            if loaded_room:
                current_room = loaded_room
            else:
                print("No valid save file found. Starting new game...")
                HEALTH = 100
                SCORE = 0
                DEATHS = 0
                INVENTORY = []
        else:
            os.remove(SAVE_FILE)
            print("Starting new game...")
            HEALTH = 100
            SCORE = 0
            DEATHS = 0
            INVENTORY = []
    else:
        print("No save file found. Starting new game...")
        HEALTH = 100
        SCORE = 0
        DEATHS = 0
        INVENTORY = []

    intro()
    tries = 0

    while tries < MAX_TRIES:
        if HEALTH <= 0:
            print("\nYou've been overcome by the haunted forces...")
            DEATHS += 1
            break

        print(f"\n--- STATUS ---\nHealth: {HEALTH}% | Score: {SCORE}")
        print(f"Inventory: {', '.join(INVENTORY) if INVENTORY else 'Empty'}")

        use_items()
        save_game(current_room)

        if current_room == "Basement":
            result = explore_room(current_room)
            if result:
                escaped = True
            else:
                DEATHS += 1
            break
        else:
            result = explore_room(current_room)
            if not result:
                DEATHS += 1
                break

        next_room = choose_room(current_room)
        if next_room:
            current_room = next_room
        else:
            print("\nYou’ve reached the end… or chosen poorly.")
            break

    if escaped:
        print(f"\n🎉 YOU SURVIVED THE HAUNTED HOUSE on {DIFFICULTY.upper()} mode! 🎉")
    else:
        print("\n💀 GAME OVER 💀")

    print(f"Deaths: {DEATHS} | Final Score: {SCORE} | Health: {HEALTH}%")
    print(f"Final Inventory: {', '.join(INVENTORY) if INVENTORY else 'Empty'}")

    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
        print("🧹 Save file deleted after game ended.")

if __name__ == "__main__":
    main()