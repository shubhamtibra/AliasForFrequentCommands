import re
from parseCommand import parse_command_line

def extract_commands_from_history(history_file):
    with open(history_file, 'r') as file:
        current_command = ""
        for line in file:
            match = re.match(r': \d+:\d+;(.*)', line)
            if match:
                command_part = match.group(1)
                if current_command:
                    current_command += " " + command_part
                else:
                    current_command = command_part
                
                if not current_command.endswith('\\'):
                    yield current_command.replace('\\', '')
                    current_command = ""

history_file = '/Users/subhamtibra/.zsh_history'

for command in extract_commands_from_history(history_file):
    parsed_command, options = parse_command_line(command)
    
    print(f"Original command: {command}")
    print(f"Parsed command: {parsed_command}")
    print("Options:")
    for option, value in options.items():
        if value:
            print(f"  {option}: {value}")
        else:
            print(f"  {option}: (flag, no value)")
    print("\n" + "-"*50 + "\n")
