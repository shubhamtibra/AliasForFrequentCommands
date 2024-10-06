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

# Create a temporary file for new aliases
temp_aliases=$(mktemp)

while IFS= read -r cmd; do
    # Create a more informative alias name
    alias_name=$(echo "$cmd" | awk '{for(i=1;i<=NF;i++) print substr($i,1,3)}' | tr -d '\n' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g')
    
    # Only process non-empty commands and alias names
    if [[ -n "$cmd" && -n "$alias_name" ]]; then
        escaped_cmd=$(echo "$cmd" | sed "s/'/'\\\\''/g; s/^/'/; s/$/'/")
        echo "alias $alias_name=$escaped_cmd" >> "$temp_aliases"
    fi
done <<< "$frequent_commands"

# Merge new aliases with existing ones, removing duplicates and empty lines
if [ -f ~/.zsh_aliases ]; then
    cat ~/.zsh_aliases "$temp_aliases" | grep -v '^$' | sort -u > ~/.zsh_aliases.new
    mv ~/.zsh_aliases.new ~/.zsh_aliases
else
    grep -v '^$' "$temp_aliases" > ~/.zsh_aliases
fi

# Ensure source line is in .zshrc, but only once
if ! grep -q 'source ~/.zsh_aliases' ~/.zshrc; then
    echo 'source ~/.zsh_aliases' >> ~/.zshrc
fi

echo "Improved aliases have been created and added to ~/.zsh_aliases"
echo "Please restart your terminal or run 'source ~/.zshrc' to apply changes."

# Clean up
rm -f "$temp_aliases"

# Add logging statements throughout the script
echo "$(date): New aliases added to ~/.zsh_aliases" >> "$LOG_FILE"
echo "$(date): Script completed" >> "$LOG_FILE"
