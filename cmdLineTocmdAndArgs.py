import re
import logging
import os
from datetime import datetime

log_file = os.path.join(os.path.dirname(__file__), 'alias.log')
logging.basicConfig(filename=log_file, level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def parse_command_line(command_line, include_flags=True, full_command=False):
    """
    Parse a command line into command and options.

    Args:
    command_line (str): The command line to parse.
    include_flags (bool): Whether to include flags in the command.
    full_command (bool): Whether to return the full command as-is.

    Returns:
    tuple: A tuple containing the command and a dictionary of options.
    """
    logging.info(f"=== Parsing command line: {command_line} ===")
    logging.info(f"Include flags: {include_flags}, Full command: {full_command}")
    
    tokens = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', command_line)
    logging.info(f"Tokens: {tokens}")

    if full_command:
        logging.info("Returning full command")
        return " ".join(tokens), {}
    
    command = []
    i = 0
    while i < len(tokens) and not tokens[i].startswith('-'):
        command.append(tokens[i])
        i += 1
    command = ' '.join(command)
    logging.info(f"Extracted command: {command}")
    
    options = {}
    i = 1
    while i < len(tokens):
        token = tokens[i]
        logging.info(f"Processing token: {token}")
        if token.startswith('-'):
            if token.startswith('--'):
                # Long option
                logging.info("Processing long option")
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
                logging.info("Processing short option")
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
    logging.info(f"Final parsed command: {command}")
    logging.info(f"Final options: {options}")
    return command, options

if __name__ == "__main__":
    # Example usage
    command_line = 'git commit -m "Initial commit" --amend --author:"John Doe <john@example.com>" --no-edit'
    command, options = parse_command_line(command_line)

    logging.info(f"Command: {command}")
    logging.info("Options:")
    for option, value in options.items():
        if value:
            logging.info(f"  {option}: {value}")
        else:
            logging.info(f"  {option}: (flag, no value)")
