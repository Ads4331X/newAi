import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "data", "memory.json")

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def update_memory(new_data):
    memory = load_memory()
    memory.update(new_data)
    save_memory(memory)

def get_memory():
    return load_memory()

def clear_memory():
    save_memory({})

if __name__ == "__main__":
    # Example usage
    update_memory({"favorite_color": "blue", "hobby": "coding"})
    print(get_memory())
    clear_memory()