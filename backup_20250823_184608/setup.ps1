# Master Setup Script for Codebase Analysis Framework
# PowerShell version for Windows users

param(
    [switch]$NoColor
)

# Enable UTF-8 output
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Script paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrameworkDir = Join-Path $ScriptDir "framework"
$OutputDir = Join-Path $ScriptDir "output"
$CodebaseDir = Join-Path $ScriptDir "codebase"
$CacheDir = Join-Path $ScriptDir ".mcp-cache"

# Color functions
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    if ($NoColor) {
        Write-Host $Message
    } else {
        Write-Host $Message -ForegroundColor $Color
    }
}

function Show-Banner {
    Clear-Host
    Write-ColorOutput "╔════════════════════════════════════════════════════════════╗" "Cyan"
    Write-ColorOutput "║     Codebase Analysis & Documentation Framework           ║" "Cyan"
    Write-ColorOutput "║                    Setup Wizard                           ║" "Cyan"
    Write-ColorOutput "╚════════════════════════════════════════════════════════════╝" "Cyan"
    Write-Host ""
    Write-ColorOutput "This wizard will help you set up the framework for analyzing" "Blue"
    Write-ColorOutput "your codebase and generating comprehensive documentation." "Blue"
    Write-Host ""
    Write-Host "Platform: Windows $([System.Environment]::OSVersion.Version)"
    Write-Host "PowerShell: $($PSVersionTable.PSVersion)"
    Write-Host ""
}

function Test-Prerequisites {
    Write-ColorOutput "Checking prerequisites..." "Yellow"
    
    $missingTools = @()
    $optionalTools = @()
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 7)) {
                $missingTools += "Python 3.7+"
            }
        }
    } catch {
        $missingTools += "Python 3.7+"
    }
    
    # Check Node.js (optional)
    try {
        $null = node --version 2>&1
    } catch {
        $optionalTools += "Node.js (for Repomix and MCPs)"
    }
    
    # Check npm (optional)
    try {
        $null = npm --version 2>&1
    } catch {
        $optionalTools += "npm (for installing Repomix)"
    }
    
    # Check git (optional)
    try {
        $null = git --version 2>&1
    } catch {
        $optionalTools += "git (for version control)"
    }
    
    if ($missingTools.Count -gt 0) {
        Write-ColorOutput "Missing required tools:" "Red"
        foreach ($tool in $missingTools) {
            Write-Host "  - $tool"
        }
        Write-Host ""
        Write-Host "Please install missing tools and run setup again."
        return $false
    }
    
    if ($optionalTools.Count -gt 0) {
        Write-ColorOutput "Optional tools not found:" "Yellow"
        foreach ($tool in $optionalTools) {
            Write-Host "  - $tool"
        }
        Write-Host ""
        Write-ColorOutput "These tools enhance functionality but are not required." "Blue"
    }
    
    Write-ColorOutput "✓ Prerequisites check complete" "Green"
    Write-Host ""
    return $true
}

function Initialize-ProjectStructure {
    Write-ColorOutput "Setting up project structure..." "Yellow"
    
    $directories = @(
        $CodebaseDir,
        (Join-Path $OutputDir "docs"),
        (Join-Path $OutputDir "diagrams"),
        (Join-Path $OutputDir "reports"),
        $CacheDir,
        (Join-Path $CacheDir "repomix"),
        (Join-Path $CacheDir "serena")
    )
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            $relativePath = $dir.Replace($ScriptDir, "").TrimStart("\")
            Write-Host "  ✓ Created: $relativePath"
        }
    }
    
    Write-ColorOutput "✓ Project structure created" "Green"
    Write-Host ""
}

function Copy-McpTemplates {
    Write-ColorOutput "Setting up MCP configuration..." "Yellow"
    
    # Copy .mcp.json template
    $mcpFile = Join-Path $ScriptDir ".mcp.json"
    $mcpTemplate = Join-Path $FrameworkDir "mcp-configs\mcp.template.json"
    
    if (!(Test-Path $mcpFile) -and (Test-Path $mcpTemplate)) {
        Copy-Item $mcpTemplate $mcpFile
        Write-ColorOutput "✓ Created .mcp.json from template" "Green"
    } elseif (Test-Path $mcpFile) {
        Write-ColorOutput "ℹ .mcp.json already exists" "Blue"
    }
    
    # Copy Repomix config template
    $repomixFile = Join-Path $ScriptDir ".repomix.config.json"
    $repomixTemplate = Join-Path $FrameworkDir "mcp-configs\repomix.config.template.json"
    
    if (!(Test-Path $repomixFile) -and (Test-Path $repomixTemplate)) {
        Copy-Item $repomixTemplate $repomixFile
        Write-ColorOutput "✓ Created .repomix.config.json from template" "Green"
    } elseif (Test-Path $repomixFile) {
        Write-ColorOutput "ℹ .repomix.config.json already exists" "Blue"
    }
    
    Write-Host ""
}

function Set-CodebasePath {
    Write-ColorOutput "Configuring codebase path..." "Yellow"
    
    $projectName = $null
    
    if (Test-Path $CodebaseDir) {
        $projects = Get-ChildItem -Path $CodebaseDir -Directory | Select-Object -ExpandProperty Name
        
        if ($projects.Count -gt 0) {
            Write-Host "Found existing project(s):"
            foreach ($proj in $projects) {
                Write-Host "  - $proj"
            }
            
            $useExisting = Read-Host "`nUse existing project '$($projects[0])'? (y/n)"
            if ($useExisting -eq 'y') {
                $projectName = $projects[0]
            } else {
                $projectName = Read-Host "Enter new project name"
            }
        } else {
            Write-Host "No existing projects found."
            $projectName = Read-Host "Enter project name (will be created in codebase/)"
        }
    }
    
    # Update .mcp.json with the project path
    if ($projectName) {
        $mcpFile = Join-Path $ScriptDir ".mcp.json"
        if (Test-Path $mcpFile) {
            try {
                $mcpConfig = Get-Content $mcpFile -Raw | ConvertFrom-Json
                
                # Update Serena project path
                if ($mcpConfig.mcpServers -and $mcpConfig.mcpServers.serena) {
                    $args = $mcpConfig.mcpServers.serena.args
                    for ($i = 0; $i -lt $args.Count; $i++) {
                        if ($args[$i] -eq '${PWD}/codebase') {
                            $args[$i] = "`${PWD}/codebase/$projectName"
                            break
                        }
                    }
                }
                
                $mcpConfig | ConvertTo-Json -Depth 10 | Set-Content $mcpFile
                Write-ColorOutput "✓ Updated .mcp.json with project: codebase/$projectName" "Green"
            } catch {
                Write-ColorOutput "⚠ Could not update .mcp.json: $_" "Yellow"
            }
        }
    }
    
    Write-Host ""
    return $projectName
}

function Invoke-TechStackSetup {
    Write-ColorOutput "Step 1: Configure Target Technology Stack" "Magenta"
    Write-Host ("-" * 40)
    
    # Check for Python script first
    $techScriptPy = Join-Path $FrameworkDir "scripts\setup_tech_stack.py"
    $techScriptPs1 = Join-Path $FrameworkDir "scripts\setup-tech-stack.ps1"
    
    if (Test-Path $techScriptPy) {
        python $techScriptPy
    } elseif (Test-Path $techScriptPs1) {
        & $techScriptPs1
    } else {
        Write-ColorOutput "⚠ Technology stack setup script not found" "Yellow"
        Copy-DefaultTechStack
    }
    
    Write-Host ""
}

function Copy-DefaultTechStack {
    Write-ColorOutput "Creating default technology stack configuration..." "Yellow"
    
    $templateFile = Join-Path $FrameworkDir "templates\TARGET_TECH_STACK.template.md"
    $outputFile = Join-Path $ScriptDir "TARGET_TECH_STACK.md"
    
    if (Test-Path $templateFile) {
        Copy-Item $templateFile $outputFile
        Write-ColorOutput "✓ Created TARGET_TECH_STACK.md from template" "Green"
        Write-ColorOutput "ℹ Edit TARGET_TECH_STACK.md to customize your target stack" "Blue"
    } else {
        Write-ColorOutput "✗ Template not found" "Red"
    }
}

function Invoke-McpSetup {
    Write-ColorOutput "Step 2: Configure MCP Integration" "Magenta"
    Write-Host ("-" * 40)
    
    # Check for Python script first
    $mcpScriptPy = Join-Path $FrameworkDir "scripts\setup_mcp.py"
    $mcpScriptPs1 = Join-Path $FrameworkDir "scripts\setup-mcp.ps1"
    
    if (Test-Path $mcpScriptPy) {
        python $mcpScriptPy
    } elseif (Test-Path $mcpScriptPs1) {
        & $mcpScriptPs1
    } else {
        Write-ColorOutput "⚠ MCP setup script not found" "Yellow"
        Write-ColorOutput "ℹ MCP configuration files have been created" "Blue"
    }
    
    Write-Host ""
}

function Show-NextSteps {
    param(
        [string]$ProjectName
    )
    
    Write-ColorOutput "╔════════════════════════════════════════════════════════════╗" "Cyan"
    Write-ColorOutput "║                    Setup Complete!                        ║" "Cyan"
    Write-ColorOutput "╚════════════════════════════════════════════════════════════╝" "Cyan"
    Write-Host ""
    Write-ColorOutput "✓ Framework is ready for use!" "Green"
    Write-Host ""
    Write-ColorOutput "Next Steps:" "Blue"
    
    if ($ProjectName) {
        Write-Host "1. Place your codebase in: codebase\$ProjectName\"
    } else {
        Write-Host "1. Place your codebase in: codebase\[project-name]\"
    }
    
    Write-Host "2. Test MCP integration:"
    Write-Host "   python framework\scripts\test_mcp_integration.py"
    
    Write-Host "3. Generate Repomix summary (optional but recommended):"
    Write-Host "   repomix --config .repomix.config.json"
    
    Write-Host "4. Start analysis in Claude Code:"
    Write-Host "   - Use @serena to activate the project"
    Write-Host "   - Use @mcp-orchestrator to begin analysis"
    Write-Host "   - Run agents: @legacy-code-detective, @business-logic-analyst, etc."
    Write-Host ""
    
    Write-ColorOutput "Output will be generated in:" "Yellow"
    Write-Host "  - Documentation: output\docs\"
    Write-Host "  - Diagrams: output\diagrams\"
    Write-Host "  - Reports: output\reports\"
    Write-Host ""
    
    Write-ColorOutput "For detailed instructions, see:" "Magenta"
    Write-Host "  - README.md"
    Write-Host "  - framework\docs\MCP_USAGE_GUIDE.md"
    Write-Host "  - framework\docs\MCP_CONFIGURATION_GUIDE.md"
}

# Main execution
try {
    Show-Banner
    
    if (!(Test-Prerequisites)) {
        exit 1
    }
    
    Initialize-ProjectStructure
    Copy-McpTemplates
    $projectName = Set-CodebasePath
    Invoke-TechStackSetup
    Invoke-McpSetup
    Show-NextSteps -ProjectName $projectName
    
    exit 0
} catch {
    Write-ColorOutput "Error during setup: $_" "Red"
    exit 1
}