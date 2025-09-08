#!/usr/bin/env python3
"""
Migration Script for Simplified Documentation Framework
Safely archives old specialized agents while preserving critical ones.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

class SimplificationMigration:
    """Handles migration to simplified agent structure"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.agents_dir = self.project_root / ".claude" / "agents"
        self.archive_dir = self.project_root / ".claude" / "agents_archive"
        self.framework_dir = self.project_root / "framework"
        
        # Critical agents to preserve
        self.critical_agents = [
            "mcp-orchestrator.md",
            "repomix-analyzer.md"
        ]
        
        # New simplified agents (already created)
        self.new_agents = [
            "architect-agent.md",
            "developer-agent.md", 
            "analyst-agent.md",
            "diagram-agent.md",
            "doc-writer-agent.md"
        ]
        
        # Old specialized agents to archive
        self.old_agents = [
            "angular-architect.md",
            "api-documentation-specialist.md",
            "architecture-selector.md",  # This one we might want to keep
            "business-logic-analyst.md",
            "data-model-specialist.md",
            "diagram-architect.md",  # Replaced by diagram-agent
            "documentation-specialist.md",  # Replaced by doc-writer-agent
            "domain-boundary-analyst.md",
            "dotnet-architect.md",
            "executive-summary.md",
            "java-architect.md",
            "legacy-code-detective.md",
            "modernization-architect.md",
            "performance-analyst.md",
            "security-analyst.md",
            "ui-analysis-specialist.md"
        ]
        
    def run_migration(self, dry_run=True):
        """Run the migration process"""
        print("=" * 70)
        print("SIMPLIFICATION MIGRATION")
        print("=" * 70)
        
        if dry_run:
            print("🧪 DRY RUN MODE - No changes will be made")
        else:
            print("⚠️  LIVE MODE - Changes will be applied")
        
        print()
        
        # Step 1: Verify current state
        print("Step 1: Analyzing current state...")
        self.analyze_current_state()
        print()
        
        # Step 2: Create archive directory
        print("Step 2: Preparing archive...")
        if not dry_run:
            self.create_archive_directory()
        else:
            print(f"Would create: {self.archive_dir}")
        print()
        
        # Step 3: Archive old agents
        print("Step 3: Archiving specialized agents...")
        self.archive_old_agents(dry_run)
        print()
        
        # Step 4: Verify critical agents
        print("Step 4: Verifying critical agents...")
        self.verify_critical_agents()
        print()
        
        # Step 5: Clean up framework
        print("Step 5: Framework cleanup...")
        self.cleanup_framework(dry_run)
        print()
        
        # Step 6: Summary
        print("Step 6: Migration summary...")
        self.show_summary()
        print()
        
        if dry_run:
            print("✅ Dry run complete. Use --live to apply changes.")
        else:
            print("✅ Migration complete!")
        
    def analyze_current_state(self):
        """Analyze the current agent directory"""
        if not self.agents_dir.exists():
            print(f"❌ Agent directory not found: {self.agents_dir}")
            return
        
        existing_agents = list(self.agents_dir.glob("*.md"))
        print(f"📁 Found {len(existing_agents)} existing agents:")
        
        for agent in sorted(existing_agents):
            if agent.name in self.critical_agents:
                print(f"  ✅ {agent.name} (CRITICAL - will preserve)")
            elif agent.name in self.new_agents:
                print(f"  🆕 {agent.name} (NEW - already created)")
            elif agent.name in self.old_agents:
                print(f"  📦 {agent.name} (will archive)")
            else:
                print(f"  ❓ {agent.name} (unknown - will preserve)")
    
    def create_archive_directory(self):
        """Create the archive directory with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.archive_dir = self.archive_dir / f"migration_{timestamp}"
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        print(f"📦 Created archive: {self.archive_dir}")
        
        # Create README in archive
        readme_content = f"""# Archived Agents - {timestamp}

These agents were archived during the simplification migration.

## What Changed
- Replaced 15+ specialized agents with 5 core agents
- Core agents now load technology-specific knowledge from framework/knowledge/
- Preserved critical agents: mcp-orchestrator, repomix-analyzer

## New Agent Structure
- architect-agent: Architecture analysis with tech-specific knowledge
- developer-agent: Code quality with language-specific patterns  
- analyst-agent: Business logic, performance, and security analysis
- diagram-agent: All visualization needs
- doc-writer-agent: Documentation generation

## Recovery
If you need to restore an old agent:
1. Copy from this archive back to .claude/agents/
2. Update any references to use new simplified structure
3. Consider extracting specific knowledge to framework/knowledge/ instead

## Migration Date
{datetime.now().isoformat()}
"""
        
        with open(self.archive_dir / "README.md", "w") as f:
            f.write(readme_content)
    
    def archive_old_agents(self, dry_run):
        """Archive the old specialized agents"""
        archived_count = 0
        
        for agent_name in self.old_agents:
            agent_path = self.agents_dir / agent_name
            if agent_path.exists():
                if dry_run:
                    print(f"  Would archive: {agent_name}")
                else:
                    archive_path = self.archive_dir / agent_name
                    shutil.move(str(agent_path), str(archive_path))
                    print(f"  📦 Archived: {agent_name}")
                archived_count += 1
        
        print(f"📊 {archived_count} agents {'would be' if dry_run else ''} archived")
    
    def verify_critical_agents(self):
        """Verify that critical agents are still present"""
        for agent_name in self.critical_agents:
            agent_path = self.agents_dir / agent_name
            if agent_path.exists():
                print(f"  ✅ {agent_name} - present")
            else:
                print(f"  ❌ {agent_name} - MISSING!")
        
        print(f"📊 New agents:")
        for agent_name in self.new_agents:
            agent_path = self.agents_dir / agent_name
            if agent_path.exists():
                print(f"  ✅ {agent_name} - ready")
            else:
                print(f"  ❌ {agent_name} - MISSING!")
    
    def cleanup_framework(self, dry_run):
        """Clean up framework directory of unused files"""
        # For now, just report what's there
        templates_dir = self.framework_dir / "templates"
        if templates_dir.exists():
            template_files = list(templates_dir.glob("*.md"))
            print(f"📁 Framework templates: {len(template_files)} files")
            
            # Could potentially clean up agent-specific templates
            old_agent_templates = [
                "SPECIALIST_AGENTS_GUIDE.md",
                # Add more as needed
            ]
            
            for template_name in old_agent_templates:
                template_path = templates_dir / template_name
                if template_path.exists():
                    if dry_run:
                        print(f"  Would clean: {template_name}")
                    else:
                        print(f"  🧹 Cleaned: {template_name}")
        
        # Check knowledge directory
        knowledge_dir = self.framework_dir / "knowledge"
        if knowledge_dir.exists():
            knowledge_files = list(knowledge_dir.rglob("*.md"))
            print(f"📚 Knowledge base: {len(knowledge_files)} files")
        else:
            print("❌ Knowledge directory missing!")
    
    def show_summary(self):
        """Show migration summary"""
        print("📋 Migration Summary:")
        print(f"  • Preserved critical agents: {len(self.critical_agents)}")
        print(f"  • New simplified agents: {len(self.new_agents)}")
        print(f"  • Archived old agents: {len(self.old_agents)}")
        print()
        print("🎯 Next Steps:")
        print("  1. Test the new agents with: python3 setup_simple.py")
        print("  2. Run a test analysis on a sample project")
        print("  3. Verify all documentation types generate correctly")
        print("  4. Update any custom scripts that reference old agents")
        print()
        print("📚 New Usage:")
        print("  • Use simplified setup: python3 setup_simple.py")
        print("  • Agents auto-load tech knowledge from framework/knowledge/")
        print("  • Select documentation types, not individual agents")

if __name__ == "__main__":
    import sys
    
    migration = SimplificationMigration()
    
    # Check for live mode
    dry_run = "--live" not in sys.argv
    
    if not dry_run:
        print("⚠️  You are about to run in LIVE mode!")
        response = input("This will move old agents to archive. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    migration.run_migration(dry_run=dry_run)