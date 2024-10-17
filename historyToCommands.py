
import re
import os
import stat
import argparse
import logging
from collections import Counter
from datetime import datetime
from cmdLineTocmdAndArgs import parse_command_line

# Set up logging
log_file = os.path.join(os.path.dirname(__file__), 'alias.log')
print(f"__file__: {__file__}")
print(f"os.path.dirname(__file__): {os.path.dirname(__file__)}")
print(
    f"os.path.join(os.path.dirname(__file__), 'alias.log'): {os.path.join(os.path.dirname(__file__), 'alias.log')}")
logging.basicConfig(filename=log_file, level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def extract_commands_from_history(history_file):
    """
    Extract commands from the given history file.

    Args:
    history_file (str): Path to the history file.

    Yields:
    str: Extracted command.
    """
    logging.info(f"=== Extracting commands from {history_file} ===")
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
        logging.info(f"Error reading history file: {e}")
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
    logging.info(f"=== Generating alias name for command: {cmd} ===")
    alias_name = ''.join(re.sub(r'\W+', '', word)[:2] for word in cmd.split())
    i = 1
    new_aliases_name = alias_name
    while new_aliases_name in existing_aliases_names or new_aliases_name in new_aliases_names:
        new_aliases_name = f"{alias_name}{i}"
        i += 1
    return new_aliases_name


def main(history_file, aliases_file, zshrc_file, threshold_percent, full_command, include_flags):
    logging.info("=== Starting historyToCommands script ===")
    logging.info(
        f"Parameters: history_file={history_file}, aliases_file={aliases_file}, zshrc_file={zshrc_file}")
    logging.info(
        f"threshold_percent={threshold_percent}, full_command={full_command}, include_flags={include_flags}")
    commands = list(extract_commands_from_history(history_file))
    commands = [parse_command_line(command, full_command=full_command, include_flags=include_flags)[
        0] for command in commands]
    # Filter out commands with less than 2 words
    commands = [command.strip()
                for command in commands if len(command.split(" ")) > 1]

    command_counts = Counter(commands)
    total_commands = len(commands)
    threshold = total_commands * (threshold_percent / 100)

    frequent_commands = {cmd: count for cmd,
                         count in command_counts.items() if count > threshold}
    logging.info(f"Frequent commands: {frequent_commands}")

    # Read existing aliases
    existing_aliases = set()
    existing_aliases_names = set()
    try:
        with open(aliases_file, 'r') as f:
            for alias in f:
                if len(alias.split('=', 1)) > 1:
                    existing_aliases.add(alias.split(
                        '=', 1)[1].rstrip().strip("'"))
                    existing_aliases_names.add(
                        alias.split('=', 1)[0].split(" ")[1])
    except FileNotFoundError:
        logging.info(
            f"Aliases file not found. Creating a new one: {aliases_file}")

    new_aliases = set()
    new_aliases_names = set()
    for cmd in frequent_commands:
        if cmd not in existing_aliases:
            new_aliases_name = generate_alias_name(
                cmd, existing_aliases_names, new_aliases_names)
            if not new_aliases_name:
                continue
            new_aliases_names.add(new_aliases_name)
            logging.info(f"Alias name: {new_aliases_name}")
            alias = f"alias {new_aliases_name}='{cmd}'"
            new_aliases.add(alias)
            logging.info(f"New command: {cmd}")
        else:
            logging.info(f"Command already exists: {cmd}")

    try:
        with open(aliases_file, 'a') as f:
            for alias in new_aliases:
                f.write(f"\n{alias}")
    except IOError as e:
        logging.info(f"Error writing to aliases file: {e}")
        return

    try:
        with open(zshrc_file, 'r+') as f:
            content = f.read()
            if 'source ~/.zsh_aliases' not in content:
                f.seek(0, 2)  # Move to the end of the file
                f.write('\n# Source aliases\nsource ~/.zsh_aliases\n')
    except IOError as e:
        logging.info(f"Error updating .zshrc file: {e}")
        return

    logging.info("New aliases added. .zshrc updated to source .zsh_aliases.")
    logging.info("=== historyToCommands script completed ===")


# def  ensure_file_writable(path):
# if not os.access(path, os.W_OK):
#     current_mode = os.stat(path).st_mode
#     new_mode = current_mode | stat.S_IWUSR
#     os.chmod(path, new_mode)


if __name__ == "__main__":
    current_dir = os.getcwd()
    # (current_dir)
    user_home = os.path.expanduser('~')
    history_file = os.path.join(user_home, '.zsh_history')
    aliases_file = os.path.join(user_home, '.zsh_aliases')
    zshrc_file = os.path.join(user_home, '.zshrc')
    # (history_file)
    # (aliases_file)
    # (zshrc_file)
    logging.info("=== historyToCommands script initiated ===")
    parser = argparse.ArgumentParser(
        description="Generate aliases from command history.")
    parser.add_argument("--history", default=history_file,
                        help="Path to the history file")
    parser.add_argument("--aliases", default=aliases_file,
                        help="Path to the aliases file")
    parser.add_argument("--zshrc", default=zshrc_file,
                        help="Path to the .zshrc file")
    parser.add_argument("--threshold", type=float, default=1.0,
                        help="Threshold percentage for frequent commands")
    parser.add_argument("--full-command", action="store_true",
                        default=False, help="Use full command for aliases")
    parser.add_argument("--include-flags", action="store_true",
                        default=True, help="Include flags in aliases")
    args = parser.parse_args()

    main(args.history, args.aliases, args.zshrc,
         args.threshold, args.full_command, args.include_flags)
