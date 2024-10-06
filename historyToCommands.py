import re
import os
import argparse
from collections import Counter
from cmdLineTocmdAndArgs import parse_command_line

def extract_commands_from_history(history_file):
    """
    Extract commands from the given history file.
    
    Args:
    history_file (str): Path to the history file.
    
    Yields:
    str: Extracted command.
    """
    try:
        with open(history_file, 'r') as file:
            current_command = ""
            need_match = True
            for line in file:
                command_part = None
                if need_match:
                    match = re.match(r': \d+:\d+;(.*)', line)
                    if not match:
                        continue
                    command_part = match.group(1)
                else:
                    command_part = line.strip()
                if current_command:
                    current_command += " " + command_part
                else:
                    current_command = command_part
                need_match = False
                if not current_command.endswith("\\"):
                    yield current_command.replace("\\", '')
                    current_command = ""
                    need_match = True
    except IOError as e:
        print(f"Error reading history file: {e}")
        return []

def generate_alias_name(cmd, existing_aliases_names, new_aliases_names):
    """
    Generate a unique alias name for a command.
    
    Args:
    cmd (str): The command to generate an alias for.
    existing_aliases_names (set): Set of existing alias names.
    new_aliases_names (set): Set of new alias names.
    
    Returns:
    str: A unique alias name.
    """
    alias_name = ''.join(re.sub(r'\W+', '', word)[:2] for word in cmd.split())
    i = 1
    new_aliases_name = alias_name
    while new_aliases_name in existing_aliases_names or new_aliases_name in new_aliases_names:
        new_aliases_name = f"{alias_name}{i}"
        i += 1
    return new_aliases_name

def main(history_file, aliases_file, zshrc_file, threshold_percent, full_command, include_flags):
    commands = list(extract_commands_from_history(history_file))
    commands = [parse_command_line(command, full_command=full_command, include_flags=include_flags)[0] for command in commands]

    command_counts = Counter(commands)
    total_commands = len(commands)
    threshold = total_commands * (threshold_percent / 100)

    frequent_commands = {cmd: count for cmd, count in command_counts.items() if count > threshold}
    print(f"Frequent commands: {frequent_commands}")

    # Read existing aliases
    existing_aliases = set()
    existing_aliases_names = set()
    try:
        with open(aliases_file, 'r') as f:
            for alias in f:
                if len(alias.split('=', 1)) > 1:
                    existing_aliases.add(alias.split('=', 1)[1].rstrip().strip("'"))
                    existing_aliases_names.add(alias.split('=', 1)[0].split(" ")[1])
    except FileNotFoundError:
        print(f"Aliases file not found. Creating a new one: {aliases_file}")

    new_aliases = set()
    new_aliases_names = set()
    for cmd in frequent_commands:
        if cmd not in existing_aliases:
            new_aliases_name = generate_alias_name(cmd, existing_aliases_names, new_aliases_names)
            new_aliases_names.add(new_aliases_name)
            print(f"Alias name: {new_aliases_name}")
            alias = f"alias {new_aliases_name}='{cmd}'"
            new_aliases.add(alias)
            print(f"New command: {cmd}")
        else:
            print(f"Command already exists: {cmd}")

    try:
        with open(aliases_file, 'a') as f:
            for alias in new_aliases:
                f.write(f"\n{alias}")
    except IOError as e:
        print(f"Error writing to aliases file: {e}")
        return

    try:
        with open(zshrc_file, 'r+') as f:
            content = f.read()
            if 'source ~/.zsh_aliases' not in content:
                f.seek(0, 2)  # Move to the end of the file
                f.write('\n# Source aliases\nsource ~/.zsh_aliases\n')
    except IOError as e:
        print(f"Error updating .zshrc file: {e}")
        return

    print("New aliases added. .zshrc updated to source .zsh_aliases.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate aliases from command history.")
    parser.add_argument("--history", default=os.path.expanduser("~/.zsh_history"), help="Path to the history file")
    parser.add_argument("--aliases", default=os.path.expanduser("~/.zsh_aliases"), help="Path to the aliases file")
    parser.add_argument("--zshrc", default=os.path.expanduser("~/.zshrc"), help="Path to the .zshrc file")
    parser.add_argument("--threshold", type=float, default=1.0, help="Threshold percentage for frequent commands")
    parser.add_argument("--full-command", action="store_true", default=False, help="Use full command for aliases")
    parser.add_argument("--include-flags", action="store_true", default=True, help="Include flags in aliases")
    args = parser.parse_args()

    main(args.history, args.aliases, args.zshrc, args.threshold, args.full_command, args.include_flags)
