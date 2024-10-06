#!/bin/zsh

# Set up logging
LOG_FILE="$(dirname "$0")/frequent_commands.log"
echo "$(date): Script started" >> "$LOG_FILE"

# Calculate minimum occurrences based on history length
HISTORY_LENGTH=$(wc -l < ~/.zsh_history)
MIN_OCCURRENCES=$((HISTORY_LENGTH / 1000 + 5))
echo "History length: $HISTORY_LENGTH, Minimum occurrences: $MIN_OCCURRENCES" >> "$LOG_FILE"

# Get frequent commands
frequent_commands=$(sed 's/^: [0-9]*:[0-9]*;//' ~/.zsh_history | sort | uniq -c | sort -rn | awk '$1 >= '$MIN_OCCURRENCES' {$1=""; print substr($0,2)}')
echo "$(date): Frequent commands extracted" >> "$LOG_FILE"

# Create a temporary file for new aliases
temp_aliases=$(mktemp)
echo "$(date): Temporary file created: $temp_aliases" >> "$LOG_FILE"

while IFS= read -r cmd; do
    # Create a more informative alias name
    alias_name=$(echo "$cmd" | awk '{for(i=1;i<=NF;i++) print substr($i,1,3)}' | tr -d '\n' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g')
    
    # Only process non-empty commands and alias names
    if [[ -n "$cmd" && -n "$alias_name" ]]; then
        escaped_cmd=$(echo "$cmd" | sed "s/'/'\\\\''/g; s/^/'/; s/$/'/")
        echo "alias $alias_name=$escaped_cmd" >> "$temp_aliases"
        echo "$(date): Added alias: $alias_name for command: $cmd" >> "$LOG_FILE"
    fi
done <<< "$frequent_commands"

# Merge new aliases with existing ones, removing duplicates and empty lines
if [ -f ~/.zsh_aliases ]; then
    # Ensure the existing file ends with a newline
    sed -i '' -e '$a\' ~/.zsh_aliases
    # Append new aliases to the existing file
    cat "$temp_aliases" | grep -v "^'" >> ~/.zsh_aliases
    # Sort and remove duplicates while preserving order
    awk '!seen[$0]++' ~/.zsh_aliases > ~/.zsh_aliases.new
    mv ~/.zsh_aliases.new ~/.zsh_aliases
    echo "$(date): Merged new aliases with existing ones" >> "$LOG_FILE"
else
    grep -v "^'" "$temp_aliases" > ~/.zsh_aliases
    echo "$(date): Created new .zsh_aliases file" >> "$LOG_FILE"
fi

# Ensure source line is in .zshrc, but only once
if ! grep -q 'source ~/.zsh_aliases' ~/.zshrc; then
    echo 'source ~/.zsh_aliases' >> ~/.zshrc
    echo "$(date): Added source line to .zshrc" >> "$LOG_FILE"
else
    echo "$(date): Source line already exists in .zshrc" >> "$LOG_FILE"
fi

echo "Improved aliases have been created and added to ~/.zsh_aliases"
echo "Please restart your terminal or run 'source ~/.zshrc' to apply changes."

# Clean up
rm -f "$temp_aliases"
echo "$(date): Temporary file removed" >> "$LOG_FILE"

# Add logging statements throughout the script
echo "$(date): New aliases added to ~/.zsh_aliases" >> "$LOG_FILE"
echo "$(date): Script completed" >> "$LOG_FILE"
