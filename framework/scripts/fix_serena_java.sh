#!/bin/bash
# Fix Serena Java language server issues on macOS

echo "Fixing Serena Java configuration on macOS..."

# Check if java_home exists and is executable
if [ -f "/usr/libexec/java_home" ]; then
    echo "✓ java_home found"
    # Check permissions
    if [ ! -x "/usr/libexec/java_home" ]; then
        echo "⚠️ java_home not executable, fixing..."
        sudo chmod +x /usr/libexec/java_home
    fi
else
    echo "⚠️ java_home not found - Java may not be installed correctly"
    echo "Install Java via: brew install openjdk@21"
fi

# Alternative: Disable Java language server in Serena
echo ""
echo "Alternative: You can disable the Java language server in Serena config"
echo "Edit ~/.serena/serena_config.yml and set:"
echo "  language_server:"
echo "    enabled: false"
echo ""
echo "This will disable Java-specific features but keep memory/search working."