#!/bin/bash
# Stop n8n Integration for Documentation Framework

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=====================================${NC}"
echo -e "${YELLOW}Stopping n8n Documentation Framework${NC}"
echo -e "${YELLOW}=====================================${NC}"

# Navigate to docker directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/docker"

# Stop services
echo -e "${YELLOW}Stopping services...${NC}"
docker-compose down

echo -e "${GREEN}✓ All services stopped${NC}"

# Ask about data cleanup
read -p "Do you want to remove volumes (this will delete all data)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Removing volumes...${NC}"
    docker-compose down -v
    echo -e "${GREEN}✓ Volumes removed${NC}"
fi

echo ""
echo -e "${GREEN}Services stopped successfully!${NC}"