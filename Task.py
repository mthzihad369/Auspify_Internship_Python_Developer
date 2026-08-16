import os
import time
import json
from datetime import datetime

# --- PREMIUM CYBERPUNK COLORS ---
C = {
    'cyan': '\033[96m', 'magenta': '\033[95m', 'gold': '\033[93m',
    'green': '\033[92m', 'red': '\033[91m', 'bold': '\033[1m', 
    'muted': '\033[90m', 'end': '\033[0m'
}
DB_FILE = "nexus_tasks.json"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_tasks():
    try:
        with open(DB_FILE, 'r') as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return []

def save_tasks(tasks):
    with open(DB_FILE, 'w') as f: json.dump(tasks, f, indent=4)

def print_banner():
    print(f"{C['cyan']}{C['bold']}")
    print("╔══════════════════════════════════════════════════╗")
    print("║          🛡️  PYTHON TASK MANAGER  🛡️            ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"{C['end']}")

def format_cell(text, width):
    """Formats text to fit exactly within the cell width without breaking boxes."""
    text = str(text)
    if len(text) > width:
        return text[:width-2] + ".." # Truncate if too long
    return text.ljust(width) # Pad with spaces if too short

def show_progress_bar(tasks):
    if not tasks: return
    done = sum(1 for t in tasks if t['status'] == 'DONE')
    total = len(tasks)
    pct = int((done / total) * 100)
    filled = int(pct / 10)
    bar = '█' * filled + '░' * (10 - filled)
    print(f"\n{C['gold']} [⚡] Overall Progress: [{C['cyan']}{bar}{C['end']}{C['gold']}] {pct}% ({done}/{total} Done){C['end']}")

def view_tasks(tasks):
    if not tasks:
        print(f"\n{C['red']}[!] No tasks found. Add some first!{C['end']}")
        return

    # Define exact column widths
    w_id, w_status, w_title, w_start, w_end, w_prog = 4, 10, 24, 14, 14, 10

    # Create exact-width headers
    h_id = format_cell("ID", w_id)
    h_status = format_cell("STATUS", w_status)
    h_title = format_cell("TASK TITLE", w_title)
    h_start = format_cell("START", w_start)
    h_end = format_cell("END", w_end)
    h_prog = format_cell("PROGRESS", w_prog)

    # Build dynamic borders based on widths
    top_border = f"╔{'═'*w_id}╦{'═'*w_status}╦{'═'*w_title}╦{'═'*w_start}╦{'═'*w_end}╦{'═'*w_prog}╗"
    mid_border = f"╠{'═'*w_id}╬{'═'*w_status}╬{'═'*w_title}╬{'═'*w_start}╬{'═'*w_end}╬{'═'*w_prog}╣"
    bot_border = f"╚{'═'*w_id}╩{'═'*w_status}╩{'═'*w_title}╩{'═'*w_start}╩{'═'*w_end}╩{'═'*w_prog}╝"

    print(f"\n{C['bold']}{C['magenta']}  {top_border}")
    print(f"  ║{h_id}║{h_status}║{h_title}║{h_start}║{h_end}║{h_prog}║")
    print(f"  {mid_border}{C['end']}")

    for t in tasks:
        status_color = C['green'] if t['status'] == 'DONE' else C['gold']
        
        id_str = format_cell(t['id'], w_id)
        status_str = format_cell(t['status'], w_status)
        title_str = format_cell(t['title'], w_title)
        start_str = format_cell(t.get('start_date', 'N/A'), w_start)
        end_str = format_cell(t.get('end_date', 'N/A'), w_end)
        prog_str = format_cell(str(t.get('progress', 0))+'%', w_prog)

        print(f"  ║{id_str}║{status_color}{status_str}{C['end']}║{C['cyan']}{title_str}{C['end']}║{start_str}║{end_str}║{prog_str}║")

    print(f"{C['bold']}{C['magenta']}  {bot_border}{C['end']}")
    show_progress_bar(tasks)

def add_task(tasks):
    print(f"\n{C['cyan']}[+] ADD NEW TASK{C['end']}")
    title = input(f"  Headline: ").strip()
    if not title:
        print(f"{C['red']}[!] Title cannot be empty.{C['end']}"); return tasks

    start_date = input(f"  Start Date (YYYY-MM-DD) [Enter to skip]: ").strip()
    if not start_date: start_date = "N/A"
        
    end_date = input(f"  End Date (YYYY-MM-DD) [Enter to skip]: ").strip()
    if not end_date: end_date = "N/A"

    new_id = max([t['id'] for t in tasks], default=0) + 1
    new_task = {
        "id": new_id, "title": title, "status": "PENDING",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "start_date": start_date, "end_date": end_date, "progress": 0
    }
    tasks.append(new_task)
    
    print(f"\n{C['magenta']}[...] Saving to database{C['end']}", end="")
    for _ in range(3): time.sleep(0.3); print(".", end="", flush=True)
    save_tasks(tasks)
    print(f"\n{C['green']}[✓] Task Added Successfully!{C['end']}")
    return tasks

def update_task(tasks):
    view_tasks(tasks)
    if not tasks: return tasks
    try:
        task_id = int(input(f"\n{C['gold']}[>] Enter Task ID to update: {C['end']}"))
        task = next((t for t in tasks if t['id'] == task_id), None)
        if not task:
            print(f"{C['red']}[!] Task not found.{C['end']}"); return tasks

        print(f"\n{C['cyan']}[?] Update Options:{C['end']}")
        print("  1. Mark as DONE (100%)")
        print("  2. Update Progress %")
        choice = input(f"  Choice (1/2): ").strip()

        if choice == '1':
            task['status'] = 'DONE'; task['progress'] = 100
        elif choice == '2':
            pct = int(input(f"  Enter new progress (0-100): "))
            task['progress'] = min(100, max(0, pct))
            if pct == 100: task['status'] = 'DONE'
            else: task['status'] = 'PENDING'
        else: return tasks

        save_tasks(tasks)
        print(f"{C['green']}[✓] Task Updated!{C['end']}")
    except ValueError: print(f"{C['red']}[!] Invalid input.{C['end']}")
    return tasks

def delete_task(tasks):
    view_tasks(tasks)
    if not tasks: return tasks
    try:
        task_id = int(input(f"\n{C['gold']}[>] Enter Task ID to delete: {C['end']}"))
        original_len = len(tasks)
        tasks = [t for t in tasks if t['id'] != task_id]
        if len(tasks) == original_len:
            print(f"{C['red']}[!] Task not found.{C['end']}"); return tasks
        save_tasks(tasks)
        print(f"{C['green']}[✓] Task Deleted!{C['end']}")
    except ValueError: print(f"{C['red']}[!] Invalid ID.{C['end']}")
    return tasks

def main():
    tasks = load_tasks()
    while True:
        clear_screen()
        print_banner()
        print(f" {C['gold']}[1]{C['end']} ➕ ADD TASK")
        print(f" {C['gold']}[2]{C['end']} 📋 VIEW ALL TASKS")
        print(f" {C['gold']}[3]{C['end']} ✅ UPDATE STATUS / PROGRESS")
        print(f" {C['gold']}[4]{C['end']} 🗑️  DELETE TASK")
        print(f" {C['gold']}[5]{C['end']} 🚪 EXIT & SAVE")

        choice = input(f"\n{C['cyan']}[>] Select Option: {C['end']}").strip()

        if choice == '1': tasks = add_task(tasks)
        elif choice == '2': view_tasks(tasks)
        elif choice == '3': tasks = update_task(tasks)
        elif choice == '4': tasks = delete_task(tasks)
        elif choice == '5':
            print(f"\n{C['magenta']}[*] Data saved to {DB_FILE}. Exiting...{C['end']}")
            break
        else: print(f"{C['red']}[!] Invalid choice.{C['end']}")

        input(f"\n{C['muted']}Press Enter to continue...{C['end']}")

if __name__ == "__main__":
    main()