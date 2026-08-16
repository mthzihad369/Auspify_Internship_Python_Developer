import secrets
import string
import os
import time
import math
import sys
import subprocess
from datetime import datetime

COLORS = {
    'cyan': '\033[96m',
    'magenta': '\033[95m',
    'gold': '\033[93m',
    'green': '\033[92m',
    'red': '\033[91m',
    'bold': '\033[1m',
    'end': '\033[0m'
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print(f"{COLORS['cyan']}{COLORS['bold']}")
    print("╔══════════════════════════════════════════════════╗")
    print("║            🛡️  SECURE VAULT  🛡️                 ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"{COLORS['end']}")

def calculate_entropy(password, pool_size):
    length = len(password)
    if pool_size <= 0: return 0
    return length * math.log2(pool_size)

def get_strength_label(entropy):
    if entropy < 30: return "WEAK", COLORS['red']
    elif entropy < 50: return "MEDIUM", COLORS['gold']
    elif entropy < 70: return "STRONG", COLORS['green']
    else: return "FORTRESS", COLORS['magenta']

def print_strength_bar(entropy):
    filled = int(min(entropy, 100) / 10)
    bar = '█' * filled + '░' * (10 - filled)
    label, color = get_strength_label(entropy)
    print(f"  [{COLORS['cyan']}{bar}{COLORS['end']}] {color}{label}{COLORS['end']} ({entropy:.1f} bits)")

def generate_secure_password(length, use_letters, use_numbers, use_symbols):
    char_pool = ''
    required_chars = []
    if use_letters:
        char_pool += string.ascii_letters
        required_chars.append(secrets.choice(string.ascii_letters))
    if use_numbers:
        char_pool += string.digits
        required_chars.append(secrets.choice(string.digits))
    if use_symbols:
        char_pool += string.punctuation
        required_chars.append(secrets.choice(string.punctuation))
    if not char_pool: return None

    remaining = length - len(required_chars)
    if remaining > 0:
        required_chars.extend([secrets.choice(char_pool) for _ in range(remaining)])
    
    import random
    random.shuffle(required_chars)
    return ''.join(required_chars)

def get_password_composition(password):
    letters = sum(1 for c in password if c.isalpha())
    digits = sum(1 for c in password if c.isdigit())
    symbols = len(password) - letters - digits
    return letters, digits, symbols

def copy_to_clipboard(text):
    """Cross-platform clipboard copy without external dependencies."""
    try:
        if os.name == 'nt': # Windows
            process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
            process.communicate(text.encode('utf-8'))
        elif sys.platform == 'darwin': # macOS
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
        else: # Linux
            process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
        return True
    except Exception:
        return False

def print_password_box(password):
    """Display the password inside a cyberpunk box."""
    padding = 2
    width = len(password) + (padding * 2)
    top = "╔" + "═" * width + "╗"
    mid = "║" + " " * padding + f"{COLORS['bold']}{COLORS['cyan']}{password}{COLORS['end']}" + " " * padding + "║"
    bot = "╚" + "═" * width + "╝"
    print(f"  {COLORS['magenta']}{top}\n  {mid}\n  {bot}{COLORS['end']}")

def save_to_file(password):
    """Save the password to a local vault file."""
    filename = "vault_passwords.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(filename, "a") as f:
            f.write(f"[{timestamp}] {password}\n")
        return True
    except Exception:
        return False

def main():
    while True:
        clear_screen()
        print_banner()

        try:
            length = int(input(f"{COLORS['gold']}[>] Enter Password Length (min 4): {COLORS['end']}"))
            if length < 4:
                print(f"{COLORS['red']}[!] Minimum length is 4 for security.{COLORS['end']}")
                time.sleep(1.5); continue
        except ValueError:
            print(f"{COLORS['red']}[!] Invalid input. Please enter a number.{COLORS['end']}")
            time.sleep(1.5); continue

        print(f"\n{COLORS['cyan']}[?] Include character types?{COLORS['end']}")
        use_letters = input(f"  Letters (A-Z, a-z)? (y/n): ").strip().lower() == 'y'
        use_numbers = input(f"  Numbers (0-9)? (y/n): ").strip().lower() == 'y'
        use_symbols = input(f"  Symbols (!@#$)? (y/n): ").strip().lower() == 'y'

        if not (use_letters or use_numbers or use_symbols):
            print(f"{COLORS['red']}[!] You must select at least one character type!{COLORS['end']}")
            time.sleep(1.5); continue

        pool_size = 0
        if use_letters: pool_size += len(string.ascii_letters)
        if use_numbers: pool_size += len(string.digits)
        if use_symbols: pool_size += len(string.punctuation)

        # Animation
        print(f"\n{COLORS['magenta']}[...] Generating secure token{COLORS['end']}", end="")
        for _ in range(3):
            time.sleep(0.3); print(".", end="", flush=True)

        password = generate_secure_password(length, use_letters, use_numbers, use_symbols)
        if not password:
            print(f"\n{COLORS['red']}[!] Generation failed.{COLORS['end']}"); time.sleep(1.5); continue

        # Output Section
        print(f"\n\n{COLORS['green']}{COLORS['bold']}[✓] PASSWORD GENERATED SUCCESSFULLY{COLORS['end']}")
        print_password_box(password)

        # Clipboard
        if copy_to_clipboard(password):
            print(f"  {COLORS['gold']}[📋] Copied to clipboard!{COLORS['end']}")
        else:
            print(f"  {COLORS['red']}[!] Clipboard copy failed (OS limitation).{COLORS['end']}")

        # Composition & Strength
        letters, digits, symbols = get_password_composition(password)
        print(f"\n{COLORS['gold']}[📊] Composition:{COLORS['end']} Letters: {letters} | Numbers: {digits} | Symbols: {symbols}")
        entropy = calculate_entropy(password, pool_size)
        print(f"{COLORS['gold']}[⚡] Strength:{COLORS['end']}")
        print_strength_bar(entropy)

        # Save Option
        save_choice = input(f"\n{COLORS['cyan']}[?] Save to vault_passwords.txt? (y/n): {COLORS['end']}").strip().lower()
        if save_choice == 'y':
            if save_to_file(password): print(f"  {COLORS['green']}[💾] Saved successfully!{COLORS['end']}")
            else: print(f"  {COLORS['red']}[!] Failed to save.{COLORS['end']}")

        # Loop
        print(f"\n{COLORS['gold']}[?] Generate another password? (y/n): {COLORS['end']}", end="")
        if input().strip().lower() != 'y':
            print(f"\n{COLORS['cyan']}[*] Exiting Auspify Secure Vault. Stay safe!{COLORS['end']}")
            time.sleep(1); break

if __name__ == "__main__":
    main()