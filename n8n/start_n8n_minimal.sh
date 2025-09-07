#!/bin/bash
# Start n8n Integration for Documentation Framework (Minimal Version)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}n8n Documentation Framework Starter${NC}"
echo -e "${YELLOW}(Minimal Version - No Redis/Celery)${NC}"
echo -e "${GREEN}=====================================${NC}"

# Check Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose first"
    exit 1
fi

# Navigate to docker directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/docker"

# Check if .env file exists, create if not
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file with defaults...${NC}"
    cat > .env << EOF
# n8n Configuration
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=changeme
N8N_PORT=5678

# API Configuration
API_PORT=8100
API_HOST=0.0.0.0
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}  Please edit docker/.env to change passwords!${NC}"
fi

# Build images
echo -e "${YELLOW}Building Docker images...${NC}"
docker-compose -f docker-compose.minimal.yml build

# Start services
echo -e "${YELLOW}Starting services (minimal mode)...${NC}"
docker-compose -f docker-compose.minimal.yml up -d

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Check service health
echo -e "${YELLOW}Checking service health...${NC}"

# Check API
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8100/health | grep -q "200"; then
    echo -e "${GREEN}✓ API Server is running${NC}"
else
    echo -e "${RED}✗ API Server is not responding${NC}"
    echo -e "${YELLOW}  Check logs: docker logs doc-framework-api${NC}"
fi

# Check n8n
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5678 | grep -q "200\|401"; then
    echo -e "${GREEN}✓ n8n is running${NC}"
else
    echo -e "${RED}✗ n8n is not responding${NC}"
    echo -e "${YELLOW}  Check logs: docker logs n8n-workflow${NC}"
fi

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Services Started Successfully!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo "Access points:"
echo -e "  • n8n UI:        ${GREEN}http://localhost:5678${NC}"
echo -e "    Username:      admin"
echo -e "    Password:      changeme"
echo ""
echo -e "  • API Server:    ${GREEN}http://localhost:8100${NC}"
echo -e "  • API Docs:      ${GREEN}http://localhost:8100/docs${NC}"
echo ""
echo -e "${YELLOW}Note: Running in minimal mode (no Redis/Celery/Monitoring)${NC}"
echo ""
echo "Next steps:"
echo "  1. Open n8n UI in your browser"
echo "  2. Import a workflow from n8n/workflows/"
echo "  3. Place your codebase in codebase/your-project/"
echo "  4. Run the workflow!"
echo ""
echo "To stop all services:"
echo "  cd $SCRIPT_DIR/docker && docker-compose -f docker-compose.minimal.yml down"
echo ""
echo -e "${YELLOW}Tip: Read n8n/N8N_INTEGRATION_GUIDE.md for detailed instructions${NC}"