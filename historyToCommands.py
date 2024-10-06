import re
from cmdLineTocmdAndArgs import parse_command_line
from collections import Counter

def extract_commands_from_history(history_file):
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

history_file = '/Users/subhamtibra/.zsh_history'
commands = list(extract_commands_from_history(history_file))
commands = [parse_command_line(command)[0] for command in commands]


command_counts = Counter(commands)
most_common_commands = command_counts.most_common()

total_commands = len(commands)
threshold = total_commands * 0.01

frequent_commands = {cmd: count for cmd, count in command_counts.items() if count > threshold}
print(f"Frequent commands: {len(frequent_commands)}")

# Read existing aliases
existing_aliases = set()
existing_aliases_names = set()
try:
    with open('/Users/subhamtibra/.zsh_aliases', 'r') as f:
        for alias in f:
            if len(alias.split('=', 1)) > 1:
                existing_aliases.add(alias.split('=', 1)[1].rstrip().strip("'"))
                existing_aliases_names.add(
                    alias.split('=', 1)[0].split(" ")[1])
except FileNotFoundError:
    pass

new_aliases = set()
new_aliases_names = set()
for cmd in frequent_commands:
    if cmd not in existing_aliases:
        alias_name = ''.join(re.sub(r'\W+', '', word)[:2] for word in cmd.split())
        i=1
        new_aliases_name = alias_name
        while new_aliases_name in existing_aliases_names or new_aliases_name in new_aliases_names:
            new_aliases_name = f"{alias_name}{i}"
            i += 1
        new_aliases_names.add(new_aliases_name)
        print(f"Alias name: {new_aliases_name}")
        alias = f"alias {new_aliases_name}='{cmd}'"
        new_aliases.add(alias)
        print(f"New command: {cmd}")
    else:
        print(f"Command already exists: {cmd}")

with open('/Users/subhamtibra/.zsh_aliases', 'a') as f:
    for alias in new_aliases:
        f.write(f"\n{alias}")

with open('/Users/subhamtibra/.zshrc', 'r+') as f:
    content = f.read()
    if 'source ~/.zsh_aliases' not in content:
        f.seek(0, 2)  # Move to the end of the file
        f.write('\n# Source aliases\nsource ~/.zsh_aliases\n')

print("New aliases added. .zshrc updated to source .zsh_aliases.")

