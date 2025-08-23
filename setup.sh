#!/bin/bash

# Master Setup Script for Codebase Analysis Framework
# Run this to initialize the framework for a new project

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

show_banner() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║     Codebase Analysis & Documentation Framework           ║${NC}"
    echo -e "${CYAN}║                    Setup Wizard                           ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}This wizard will help you set up the framework for analyzing${NC}"
    echo -e "${BLUE}your codebase and generating comprehensive documentation.${NC}"
    echo ""
}

check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    missing_tools=()
    
    # Check for required tools
    if ! command -v node &> /dev/null; then
        missing_tools+=("Node.js")
    fi
    
    if ! command -v npm &> /dev/null; then
        missing_tools+=("npm")
    fi
    
    if ! command -v python3 &> /dev/null; then
        missing_tools+=("Python 3")
    fi
    
    if [ ${#missing_tools[@]} -gt 0 ]; then
        echo -e "${RED}Missing required tools:${NC}"
        for tool in "${missing_tools[@]}"; do
            echo -e "  - $tool"
        done
        echo ""
        echo "Please install missing tools and run setup again."
        exit 1
    fi
    
    echo -e "${GREEN}✅ All prerequisites met${NC}"
    echo ""
}

setup_project_structure() {
    echo -e "${YELLOW}Setting up project structure...${NC}"
    
    # Create necessary directories if they don't exist
    mkdir -p "$SCRIPT_DIR/codebase"
    mkdir -p "$SCRIPT_DIR/output/docs"
    mkdir -p "$SCRIPT_DIR/output/diagrams"
    mkdir -p "$SCRIPT_DIR/output/reports"
    mkdir -p "$SCRIPT_DIR/.mcp-cache"
    
    echo -e "${GREEN}✅ Project structure created${NC}"
    echo ""
}

copy_mcp_templates() {
    echo -e "${YELLOW}Setting up MCP configuration...${NC}"
    
    # Copy MCP template if .mcp.json doesn't exist
    if [ ! -f "$SCRIPT_DIR/.mcp.json" ]; then
        cp "$SCRIPT_DIR/framework/mcp-configs/mcp.template.json" "$SCRIPT_DIR/.mcp.json"
        echo -e "${GREEN}✅ Created .mcp.json from template${NC}"
    else
        echo -e "${BLUE}ℹ️  .mcp.json already exists${NC}"
    fi
    
    # Copy Repomix config if it doesn't exist
    if [ ! -f "$SCRIPT_DIR/.repomix.config.json" ]; then
        cp "$SCRIPT_DIR/framework/mcp-configs/repomix.config.template.json" "$SCRIPT_DIR/.repomix.config.json"
        echo -e "${GREEN}✅ Created .repomix.config.json from template${NC}"
    else
        echo -e "${BLUE}ℹ️  .repomix.config.json already exists${NC}"
    fi
    
    echo ""
}

configure_codebase_path() {
    echo -e "${YELLOW}Configuring codebase path...${NC}"
    
    if [ -d "$SCRIPT_DIR/codebase" ]; then
        # Check if there's already a project
        projects=($(ls -d "$SCRIPT_DIR/codebase"/*/ 2>/dev/null | xargs -n 1 basename))
        
        if [ ${#projects[@]} -gt 0 ]; then
            echo "Found existing project(s):"
            for proj in "${projects[@]}"; do
                echo "  - $proj"
            done
            
            read -p "Use existing project '${projects[0]}'? (y/n): " use_existing
            if [[ "$use_existing" == "y" ]]; then
                PROJECT_NAME="${projects[0]}"
            else
                read -p "Enter new project name: " PROJECT_NAME
            fi
        else
            echo "No existing projects found."
            read -p "Enter project name (will be created in codebase/): " PROJECT_NAME
        fi
        
        # Update .mcp.json with the correct path
        if [ -n "$PROJECT_NAME" ]; then
            sed -i.bak "s|\${PWD}/codebase|\${PWD}/codebase/$PROJECT_NAME|g" "$SCRIPT_DIR/.mcp.json" 2>/dev/null || \
            sed -i '' "s|\${PWD}/codebase|\${PWD}/codebase/$PROJECT_NAME|g" "$SCRIPT_DIR/.mcp.json"
            echo -e "${GREEN}✅ Updated .mcp.json with project path: codebase/$PROJECT_NAME${NC}"
        fi
    fi
    
    echo ""
}

run_framework_setup() {
    echo -e "${YELLOW}Running framework configuration scripts...${NC}"
    echo ""
    
    # Run technology stack setup
    echo -e "${MAGENTA}Step 1: Configure Target Technology Stack${NC}"
    echo "----------------------------------------"
    if [ -x "$SCRIPT_DIR/framework/scripts/setup-tech-stack.sh" ]; then
        "$SCRIPT_DIR/framework/scripts/setup-tech-stack.sh"
    else
        echo -e "${YELLOW}⚠️  Technology stack setup script not found${NC}"
    fi
    
    echo ""
    
    # Run MCP setup
    echo -e "${MAGENTA}Step 2: Configure MCP Integration${NC}"
    echo "----------------------------------------"
    if [ -x "$SCRIPT_DIR/framework/scripts/setup-mcp.sh" ]; then
        "$SCRIPT_DIR/framework/scripts/setup-mcp.sh"
    else
        echo -e "${YELLOW}⚠️  MCP setup script not found${NC}"
    fi
    
    echo ""
}

show_next_steps() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    Setup Complete!                        ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}✅ Framework is ready for use!${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Place your codebase in: codebase/$PROJECT_NAME/"
    echo "2. Test MCP integration:"
    echo "   ./framework/scripts/test-mcp-integration.sh"
    echo "3. Generate Repomix summary (optional but recommended):"
    echo "   repomix --config .repomix.config.json"
    echo "4. Start analysis in Claude Code:"
    echo "   - Use @serena to activate the project"
    echo "   - Use @mcp-orchestrator to begin analysis"
    echo "   - Run agents: @legacy-code-detective, @business-logic-analyst, etc."
    echo ""
    echo -e "${YELLOW}Output will be generated in:${NC}"
    echo "  - Documentation: output/docs/"
    echo "  - Diagrams: output/diagrams/"
    echo "  - Reports: output/reports/"
    echo ""
    echo -e "${MAGENTA}For detailed instructions, see:${NC}"
    echo "  - README.md"
    echo "  - framework/docs/MCP_USAGE_GUIDE.md"
    echo "  - framework/docs/MCP_CONFIGURATION_GUIDE.md"
}

# Main execution
main() {
    clear
    show_banner
    check_prerequisites
    setup_project_structure
    copy_mcp_templates
    configure_codebase_path
    run_framework_setup
    show_next_steps
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi