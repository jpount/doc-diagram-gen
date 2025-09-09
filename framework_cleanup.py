#!/usr/bin/env python3
"""
Framework Cleanup Utility
Fixes common issues with output file organization and naming
"""

import json
import shutil
from pathlib import Path
from typing import List

class FrameworkCleanup:
    """Utility to clean up framework execution issues"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.output_dir = self.project_root / "output"
        
    def fix_file_locations(self):
        """Move files to correct locations"""
        print("🧹 Fixing file locations...")
        
        # Move misplaced reports from docs to reports
        docs_dir = self.output_dir / "docs"
        reports_dir = self.output_dir / "reports"
        
        misplaced_reports = [
            "analysis-report.md",
            "analyst-report.md", 
            "*-summary.md",
            "*-analysis.md"
        ]
        
        moved = 0
        for pattern in misplaced_reports:
            for file_path in docs_dir.glob(pattern):
                target = reports_dir / file_path.name
                if not target.exists():
                    shutil.move(str(file_path), str(target))
                    print(f"   📁 Moved {file_path.name} -> reports/")
                    moved += 1
        
        print(f"✅ Moved {moved} files to correct locations")
    
    def clean_context_files(self):
        """Ensure all context files are JSON format"""
        print("🧹 Cleaning context files...")
        
        context_dir = self.output_dir / "context"
        md_files = list(context_dir.glob("*.md"))
        
        for md_file in md_files:
            # Convert .md context files to .json or remove if not needed
            if "context" in md_file.name.lower():
                json_name = md_file.stem + ".json"
                json_file = context_dir / json_name
                
                if not json_file.exists():
                    print(f"   ⚠️ Found .md context file: {md_file.name} (should be .json)")
                    # Move to reports instead of converting
                    target = self.output_dir / "reports" / md_file.name
                    shutil.move(str(md_file), str(target))
                    print(f"   📁 Moved {md_file.name} -> reports/")
                else:
                    md_file.unlink()
                    print(f"   🗑️ Removed duplicate: {md_file.name}")
        
        print("✅ Context directory cleaned")
    
    def fix_naming_consistency(self):
        """Fix inconsistent file naming"""
        print("🧹 Fixing naming consistency...")
        
        # Define standard naming patterns
        renames = {
            "analysis-report.md": "repomix-analysis.md",
            "analyst-report.md": "analyst-comprehensive.md",
        }
        
        renamed = 0
        for old_name, new_name in renames.items():
            # Check in both docs and reports
            for directory in [self.output_dir / "docs", self.output_dir / "reports"]:
                old_file = directory / old_name
                new_file = directory / new_name
                
                if old_file.exists() and not new_file.exists():
                    old_file.rename(new_file)
                    print(f"   📝 Renamed {old_name} -> {new_name}")
                    renamed += 1
        
        print(f"✅ Fixed {renamed} naming inconsistencies")
    
    def check_context_completeness(self):
        """Check that all expected contexts exist"""
        print("🧹 Checking context completeness...")
        
        # Read current configuration
        config_file = self.project_root / "analysis_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            print("   ⚠️ No analysis_config.json found")
            return
        
        # Expected contexts based on document types
        doc_types = config.get('document_types', [])
        context_dir = self.output_dir / "context"
        
        expected_contexts = ["mcp-orchestrator-summary.json", "repomix-analyzer-summary.json"]
        
        if 'architecture' in doc_types:
            expected_contexts.extend([
                "architect-java-summary.json",
                "architect-j2ee_jakarta_ee-summary.json"
            ])
        
        if 'business_rules' in doc_types:
            expected_contexts.append("analyst-business-summary.json")
        if 'performance' in doc_types:
            expected_contexts.append("analyst-performance-summary.json") 
        if 'ui_analysis' in doc_types:
            expected_contexts.append("analyst-ui-summary.json")
        if 'quality' in doc_types:
            expected_contexts.append("developer-quality-summary.json")
            
        expected_contexts.extend([
            "diagram-agent-summary.json",
            "doc-writer-agent-summary.json"
        ])
        
        missing = []
        present = []
        
        for context_name in expected_contexts:
            context_file = context_dir / context_name
            if context_file.exists():
                present.append(context_name)
                print(f"   ✅ {context_name}")
            else:
                missing.append(context_name)
                print(f"   ❌ {context_name}")
        
        print(f"📊 Context Status: {len(present)}/{len(expected_contexts)} present")
        if missing:
            print(f"⚠️ Missing contexts: {', '.join(missing)}")
            
        return len(missing) == 0
    
    def run_full_cleanup(self):
        """Run all cleanup operations"""
        print("🧹 Starting Framework Cleanup...")
        print("=" * 50)
        
        self.fix_file_locations()
        print()
        
        self.clean_context_files()
        print()
        
        self.fix_naming_consistency()
        print()
        
        complete = self.check_context_completeness()
        print()
        
        if complete:
            print("✅ Framework is clean and ready!")
        else:
            print("⚠️ Some issues remain - may need to re-run missing agents")
        
        print("=" * 50)

if __name__ == "__main__":
    cleanup = FrameworkCleanup()
    cleanup.run_full_cleanup()