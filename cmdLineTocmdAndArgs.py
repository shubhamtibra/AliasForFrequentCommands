import re

def parse_command_line(command_line, include_flags=True, full_command=False):
    tokens = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', command_line)
    #print(command_line, tokens)
    if full_command:
        return " ".join(tokens), {}
    command = []
    i = 0
    while i < len(tokens) and not tokens[i].startswith('-'):
        command.append(tokens[i])
        i += 1
    command = ' '.join(command)
    options = {}
    i = 1
    while i < len(tokens):
        token = tokens[i]
        if token.startswith('-'):
            if token.startswith('--'):
                # Long option
                if '=' in token:
                    option, value = token.split('=', 1)
                    options[option] = value
                elif ':' in token:
                    option, value = token.split(':', 1)
                    options[option] = value
                else:
                    option = token
                    if i + 1 < len(tokens) and not tokens[i + 1].startswith('-'):
                        options[option] = tokens[i + 1]
                        i += 1
                    else:
                        if include_flags:
                            command += ' ' + option
                        else:
                            options[option] = None
            else:
                # Short option
                option = token
                if i + 1 < len(tokens) and not tokens[i + 1].startswith('-'):
                    options[option] = tokens[i + 1]
                    i += 1
                else:
                    if include_flags:
                        command += ' ' + option
                    else:
                        options[option] = None
        i += 1
    return command, options
if __name__ == "__main__":
    # Example usage
    command_line = 'git commit -m "Initial commit" --amend --author:"John Doe <john@example.com>" --no-edit'
    command, options = parse_command_line(command_line)

    print(f"Command: {command}")
    print("Options:")
    for option, value in options.items():
        if value:
            print(f"  {option}: {value}")
        else:
            print(f"  {option}: (flag, no value)")
