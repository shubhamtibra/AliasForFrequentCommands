# HistoryToCommands

**HistoryToCommands** is a Python-based tool that automatically generates shell aliases for your most frequently used commands by analyzing your command history. This utility enhances your workflow by simplifying and speeding up command execution in your terminal.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Logging](#logging)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Automatic Alias Generation:** Scans your `.zsh_history` file to identify and create aliases for frequently used commands.
- **Customizable Threshold:** Set a threshold percentage to determine which commands are considered frequent.
- **Periodic Execution:** Runs automatically at system load and at specified intervals (default is every 24 hours).
- **Logging:** Maintains logs for monitoring and debugging purposes.
- **Seamless Integration:** Updates your `.zshrc` to source the generated aliases, ensuring they are available in your shell sessions.

## Prerequisites

- **Operating System:** macOS (due to the use of `launchd` for scheduling).
- **Python:** Version 3.x installed at `/usr/bin/python3`.
- **Shell:** Zsh (since it modifies `.zshrc` and uses `.zsh_history`).

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/HistoryToCommands.git
   ```

2. **Navigate to the Project Directory**

   ```bash
   cd HistoryToCommands
   ```

3. **Ensure Script Executability**

   Although the script is executed using Python, it's good practice to make it executable.

   ```bash
   chmod +x historyToCommands.py
   ```

4. **Set Up the LaunchAgent**

   Copy the `com.user.historytocommands.plist` file to your LaunchAgents directory.

   ```bash
   cp com.user.historytocommands.plist ~/Library/LaunchAgents/
   ```

5. **Load the LaunchAgent**

   This will load the agent and run the script immediately, as well as schedule it to run at defined intervals.

   ```bash
   launchctl load ~/Library/LaunchAgents/com.user.historytocommands.plist
   ```

## Configuration

The behavior of HistoryToCommands can be customized using command-line arguments or by modifying the plist file.

### Command-Line Arguments

- `--history`: Path to the history file. (Default: `~/.zsh_history`)
- `--aliases`: Path to the aliases file. (Default: `~/.zsh_aliases`)
- `--zshrc`: Path to the .zshrc file. (Default: `~/.zshrc`)
- `--threshold`: Threshold percentage for frequent commands. (Default: 1.0)
- `--full-command`: Use the full command for aliases. (Default: False)
- `--include-flags`: Include flags in aliases. (Default: True)

### Modifying the Plist File

If you need to change the default behavior or configuration, edit the `com.user.historytocommands.plist` file located in `~/Library/LaunchAgents/`.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.historytocommands</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/subhamtibra/PersonalProjects/AliasForFrequentCommands/historyToCommands.py</string>
        <string>--threshold</string>
        <string>2.0</string>
        <!-- Add more arguments as needed -->
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>StartInterval</key>
    <integer>86400</integer> <!-- 24 hours in seconds -->

    <key>WorkingDirectory</key>
    <string>/Users/subhamtibra/PersonalProjects/AliasForFrequentCommands</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>HOME</key>
        <string>/Users/subhamtibra</string>
    </dict>

    <key>StandardOutPath</key>
    <string>/tmp/com.user.historytocommands.stdout</string>

    <key>StandardErrorPath</key>
    <string>/tmp/com.user.historytocommands.stderr</string>
</dict>
</plist>
```

#### Adjusting the Threshold

To change the threshold percentage for determining frequent commands, modify the `--threshold` argument in the plist file or when running the script manually.

## Usage

Once installed and configured, HistoryToCommands operates automatically. However, you can also run the script manually if needed.

### Automatic Execution

The LaunchAgent ensures that the script runs:

- **At Load Time:** Immediately after loading the plist.
- **Periodically:** Every `StartInterval` seconds (default is every 24 hours).

### Manual Execution

To execute the script manually:

```bash
/usr/bin/python3 /Users/subhamtibra/PersonalProjects/AliasForFrequentCommands/historyToCommands.py
```

You can also pass custom arguments:

```bash
/usr/bin/python3 /Users/subhamtibra/PersonalProjects/AliasForFrequentCommands/historyToCommands.py --threshold 2.5 --full-command
```

## Logging

HistoryToCommands maintains logs to help you monitor its activities and troubleshoot issues.

- **Standard Output:** `/tmp/com.user.historytocommands.stdout`
- **Standard Error:** `/tmp/com.user.historytocommands.stderr`
- **Alias Log:** `alias.log` located in the project directory.

### Viewing Logs

To view the standard output log:

```bash
cat /tmp/com.user.historytocommands.stdout
```

To view the standard error log:

```bash
cat /tmp/com.user.historytocommands.stderr
```

To view the alias generation log:

```bash
cat /Users/subhamtibra/PersonalProjects/AliasForFrequentCommands/alias.log
```

## Troubleshooting

### Error Code 78

If you encounter Error Code 78 when loading the plist, it indicates a configuration error.

Possible Solutions:

1. **Check ProgramArguments:**

   - Ensure that the Python executable is the first argument.
   - Ensure the script path is correct.

2. **Verify File Permissions:**

   - Ensure that `historyToCommands.py` is executable.
   - Verify read/write permissions for `.zsh_history`, `.zsh_aliases`, and `.zshrc`.

   ```bash
   chmod +x /Users/subhamtibra/PersonalProjects/AliasForFrequentCommands/historyToCommands.py
   chmod u+rw ~/.zsh_history ~/.zsh_aliases ~/.zshrc
   chmod u+rwx /Users/subhamtibra/PersonalProjects/AliasForFrequentCommands
   ```

3. **Validate Plist Syntax:**

   - Ensure the plist file is well-formed XML.
   - Use `plutil` to check for syntax errors.

   ```bash
   plutil ~/Library/LaunchAgents/com.user.historytocommands.plist
   ```

4. **Reload the LaunchAgent:**
   After making corrections, unload and load the plist again.

   ```bash
   launchctl unload ~/Library/LaunchAgents/com.user.historytocommands.plist
   launchctl load ~/Library/LaunchAgents/com.user.historytocommands.plist
   ```

5. **Review Logs:**
   Check the error log for detailed information.

   ```bash
   cat /tmp/com.user.historytocommands.stderr
   ```

### Script Execution Issues

If the script does not behave as expected:

1. **Run Manually:**
   Execute the script manually to identify runtime errors.

   ```bash
   /usr/bin/python3 /Users/subhamtibra/PersonalProjects/AliasForFrequentCommands/historyToCommands.py
   ```

2. **Check Dependencies:**
   Ensure that all imported modules are available. The script primarily uses Python's standard library, but it relies on `cmdLineTocmdAndArgs.py`. Ensure this module is present in the project directory.

3. **Verify History File Format:**
   The script expects a specific format in `.zsh_history`. Ensure your history file adheres to this format.

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**

2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "Add some feature"
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Open a Pull Request**

## License

This project is licensed under the MIT License.

**Note:** Always back up your configuration files before running automated scripts that modify them to prevent unintended data loss.
