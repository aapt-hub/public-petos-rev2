#!/bin/bash

# This script scaffolds the expected stack directories and index.md files
# based on the PETOS vNext structure.
# It should be run from the repository root.

# Exit immediately if a command exits with a non-zero status.
set -e

REPO_ROOT=$(dirname "$(dirname "$(readlink -f "$0")")")
STACKS_DIR="$REPO_ROOT/stacks"

# Define the expected stack names
EXPECTED_STACKS=(
    "infrastructure"
    "cloud-platforms"
    "digital-workplace"
    "cybersecurity"
    "development-automation"
    "data-platforms"
    "ai-engineering"
    "operations-observability"
    "service-management"
    "migration-engineering"
    "business-continuity"
    "architecture"
    "governance-compliance"
    "documentation-engineering"
    "career-development"
    "lessons-learned"
)

echo "Scaffolding PETOS vNext stack directories and index files..."

# Ensure the main stacks directory exists
mkdir -p "$STACKS_DIR"

for stack in "${EXPECTED_STACKS[@]}"; do
    STACK_PATH="$STACKS_DIR/$stack"
    CAPABILITIES_PATH="$STACK_PATH/capabilities"

    echo "Processing stack: $stack"

    # Create the stack directory
    mkdir -p "$STACK_PATH"
    # Create the stack's main index.md
    echo "# $(echo "$stack" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++){ $i=toupper(substr($i,1,1)) substr($i,2) }}1') Stack" > "$STACK_PATH/index.md"
    
    # Create the capabilities directory and its index.md
    mkdir -p "$CAPABILITIES_PATH"
    echo "# $(echo "$stack" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++){ $i=toupper(substr($i,1,1)) substr($i,2) }}1') Capabilities" > "$CAPABILITIES_PATH/index.md"
done

echo "Scaffolding complete. You can now run 'python validate.py structure' to verify."