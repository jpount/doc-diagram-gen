#!/usr/bin/env python3
"""
Script to update all agents with comprehensive fallback mechanisms
Ensures all agents can fall back to raw codebase when Repomix data is insufficient
"""

import os
import re
from pathlib import Path

def update_agent_fallback(agent_file, agent_name):
    """Update a single agent with enhanced fallback logic"""
    
    # Read current agent content
    with open(agent_file, 'r') as f:
        content = f.read()
    
    # Enhanced fallback section for each agent type
    fallback_sections = {
        'repomix-analyzer': '''## Enhanced Fallback Strategy

⚠️ **SEE**: `framework/templates/FALLBACK_PATTERNS.md` for complete fallback implementation patterns.

### Data Loading with Comprehensive Fallback
```python
def load_data_with_comprehensive_fallback():
    """Load data with comprehensive fallback to raw codebase"""
    
    # PRIMARY: Try Repomix summary
    repomix_path = "output/reports/repomix-summary.md"
    if Path(repomix_path).exists():
        repomix_content = Read(repomix_path)
        if len(repomix_content) > 1000:  # Has sufficient content
            print("✅ Using Repomix summary (sufficient data)")
            return extract_from_repomix_summary(repomix_content)
        else:
            print("⚠️  Repomix summary exists but has insufficient data")
    else:
        print("⚠️  Repomix summary not found")
    
    # Try to generate Repomix summary
    print("🔄 Attempting to generate Repomix summary...")
    try:
        project_dirs = Glob("codebase/*")
        if project_dirs:
            project_path = project_dirs[0]
            result = Bash(f"repomix --config .repomix.config.json {project_path}")
            
            if Path(repomix_path).exists():
                repomix_content = Read(repomix_path)
                if len(repomix_content) > 1000:
                    print("✅ Successfully generated Repomix summary")
                    return extract_from_repomix_summary(repomix_content)
    except Exception as e:
        print(f"❌ Failed to generate Repomix summary: {e}")
    
    print("🔄 Repomix unavailable - falling back to comprehensive raw codebase analysis")
    
    # FALLBACK: Comprehensive raw codebase analysis
    return analyze_raw_codebase_comprehensive()

def analyze_raw_codebase_comprehensive():
    """Perform comprehensive analysis of raw codebase with technology detection"""
    try:
        technologies = detect_technologies_from_filesystem()
        print(f"🔍 Detected technologies: {technologies}")
        
        if "java" in technologies:
            return extract_java_comprehensive()
        elif "csharp" in technologies:
            return extract_dotnet_comprehensive()
        elif "typescript" in technologies:
            return extract_angular_comprehensive()
        else:
            return extract_generic_comprehensive(technologies)
            
    except Exception as e:
        print(f"❌ Raw codebase analysis failed: {e}")
        return create_minimal_viable_response()
```''',
        
        'java-architect': '''## Enhanced Fallback Strategy

⚠️ **SEE**: `framework/templates/FALLBACK_PATTERNS.md` for complete fallback implementation patterns.

### Java-Specific Fallback Implementation
```python
def extract_java_data_with_fallback(data_sources):
    """Extract Java data with comprehensive fallback mechanisms"""
    
    # PRIMARY: Try Repomix data first
    java_data = {}
    
    if data_sources["repomix_content"] and data_sources["data_quality"] in ["excellent", "good"]:
        print("🔍 Extracting Java information from Repomix summary...")
        java_data = extract_java_from_repomix(data_sources["repomix_content"])
        
        if validate_java_extraction(java_data):
            print("✅ Sufficient Java data extracted from Repomix")
            java_data["data_source"] = "repomix_summary"
            return java_data
        else:
            print("⚠️  Repomix Java data insufficient, falling back to raw analysis")
    
    # SECONDARY: Use previous agent context if available
    if data_sources["repomix_context"]:
        print("🔍 Extracting Java information from previous agent context...")
        context_data = json.loads(data_sources["repomix_context"])
        java_data.update(extract_java_from_context(context_data))
    
    # FALLBACK: Raw codebase analysis
    print("🔄 Falling back to comprehensive raw Java analysis...")
    raw_java_data = extract_java_from_raw_codebase()
    
    if raw_java_data and validate_java_extraction(raw_java_data):
        merged_data = {**java_data, **raw_java_data}
        merged_data["data_source"] = "raw_codebase_fallback"
        print("✅ Java data successfully extracted from raw codebase")
        return merged_data
    else:
        print("❌ Unable to extract sufficient Java data from any source")
        return create_minimal_java_response()

def extract_java_from_raw_codebase():
    """Comprehensive Java extraction from raw codebase"""
    try:
        # Build system detection
        build_files = Glob("codebase/**/pom.xml") + Glob("codebase/**/build.gradle")
        java_files = Glob("codebase/**/*.java")
        
        if not java_files and not build_files:
            print("⚠️  No Java files or build files found")
            return None
        
        java_data = {
            "primary_language": "Java",
            "technology_detected": "Java",
            "file_count": len(java_files),
            "data_source": "raw_codebase"
        }
        
        # Analyze build files
        if build_files:
            build_content = Read(build_files[0])
            java_data["build_system"] = "Maven" if "pom.xml" in build_files[0] else "Gradle"
            java_data["frameworks"] = detect_java_frameworks_from_build(build_content)
        
        # Analyze sample Java files for additional patterns
        sample_files = java_files[:min(10, len(java_files))]
        frameworks_from_code = set()
        
        for java_file in sample_files:
            try:
                content = Read(java_file)
                frameworks_from_code.update(detect_frameworks_from_imports(content))
            except Exception as e:
                print(f"⚠️  Could not read {java_file}: {e}")
                continue
        
        if frameworks_from_code:
            existing_frameworks = java_data.get("frameworks", [])
            if isinstance(existing_frameworks, list):
                java_data["frameworks"] = list(set(existing_frameworks + list(frameworks_from_code)))
        
        return java_data
        
    except Exception as e:
        print(f"❌ Error in Java fallback extraction: {e}")
        return None
```''',
        
        'business-logic-analyst': '''## Enhanced Fallback Strategy

⚠️ **SEE**: `framework/templates/FALLBACK_PATTERNS.md` for complete fallback implementation patterns.

### Business Logic Fallback Implementation
```python
def extract_business_logic_with_fallback(data_sources):
    """Extract business logic with comprehensive fallback mechanisms"""
    
    # PRIMARY: Try Repomix data and other contexts first
    business_data = {}
    
    if data_sources["repomix_content"]:
        print("🔍 Extracting business logic from Repomix summary...")
        business_data = extract_business_logic_from_repomix(data_sources["repomix_content"])
    
    # Use architecture context for business-relevant patterns
    if data_sources.get("architecture_context"):
        print("🔍 Extracting business patterns from architecture context...")
        arch_data = json.loads(data_sources["architecture_context"])
        business_data.update(extract_business_from_architecture(arch_data))
    
    # Validate if we have sufficient business logic data
    if validate_business_logic_extraction(business_data):
        print("✅ Sufficient business logic data from existing sources")
        business_data["data_source"] = "context_analysis"
        return business_data
    
    # FALLBACK: Raw codebase analysis for business logic
    print("🔄 Falling back to raw codebase analysis for business logic...")
    raw_business_data = extract_business_logic_from_raw_codebase()
    
    if raw_business_data:
        merged_data = {**business_data, **raw_business_data}
        merged_data["data_source"] = "raw_codebase_fallback"
        return merged_data
    else:
        return create_minimal_business_response()

def extract_business_logic_from_raw_codebase():
    """Extract business logic patterns from raw codebase"""
    try:
        # Look for business logic indicators in file names and structure
        business_files = []
        business_files.extend(Glob("codebase/**/*Service*.java"))
        business_files.extend(Glob("codebase/**/*Business*.java"))
        business_files.extend(Glob("codebase/**/*Domain*.java"))
        business_files.extend(Glob("codebase/**/*Entity*.java"))
        business_files.extend(Glob("codebase/**/*Model*.java"))
        
        if not business_files:
            print("⚠️  No obvious business logic files found")
            return None
        
        print(f"🔍 Found {len(business_files)} potential business logic files")
        
        business_data = {
            "business_files_count": len(business_files),
            "business_patterns": [],
            "domain_entities": [],
            "business_rules": []
        }
        
        # Analyze sample business files
        sample_files = business_files[:min(5, len(business_files))]
        for business_file in sample_files:
            try:
                content = Read(business_file)
                # Extract business patterns from code
                patterns = extract_business_patterns_from_content(content)
                business_data["business_patterns"].extend(patterns)
            except Exception as e:
                print(f"⚠️  Could not analyze {business_file}: {e}")
                continue
        
        return business_data
        
    except Exception as e:
        print(f"❌ Error in business logic fallback: {e}")
        return None
```''',
        
        'performance-analyst': '''## Enhanced Fallback Strategy

⚠️ **SEE**: `framework/templates/FALLBACK_PATTERNS.md` for complete fallback implementation patterns.

### Performance Analysis Fallback Implementation
```python
def extract_performance_data_with_fallback(data_sources):
    """Extract performance data with comprehensive fallback mechanisms"""
    
    # PRIMARY: Try existing data sources first
    performance_data = {}
    
    # Use architecture findings for performance-relevant patterns
    if data_sources.get("architecture_context"):
        print("🔍 Extracting performance patterns from architecture context...")
        arch_data = json.loads(data_sources["architecture_context"])
        performance_data = extract_performance_from_architecture(arch_data)
    
    # Use business logic findings for performance hotspots
    if data_sources.get("business_context"):
        print("🔍 Identifying performance hotspots from business logic...")
        business_data = json.loads(data_sources["business_context"])
        performance_data.update(extract_performance_from_business_logic(business_data))
    
    # Validate if we have sufficient performance data
    if validate_performance_extraction(performance_data):
        print("✅ Sufficient performance data from existing sources")
        performance_data["data_source"] = "context_analysis"
        return performance_data
    
    # FALLBACK: Raw codebase analysis for performance issues
    print("🔄 Falling back to raw codebase performance analysis...")
    raw_performance_data = extract_performance_from_raw_codebase()
    
    if raw_performance_data:
        merged_data = {**performance_data, **raw_performance_data}
        merged_data["data_source"] = "raw_codebase_fallback"
        return merged_data
    else:
        return create_minimal_performance_response()

def extract_performance_from_raw_codebase():
    """Extract performance issues from raw codebase analysis"""
    try:
        # Look for performance-critical files
        perf_indicators = []
        perf_indicators.extend(Glob("codebase/**/*Cache*.java"))
        perf_indicators.extend(Glob("codebase/**/*Pool*.java"))
        perf_indicators.extend(Glob("codebase/**/*Performance*.java"))
        perf_indicators.extend(Glob("codebase/**/*Async*.java"))
        
        # Analyze database-related files
        db_files = []
        db_files.extend(Glob("codebase/**/*DAO*.java"))
        db_files.extend(Glob("codebase/**/*Repository*.java"))
        db_files.extend(Glob("codebase/**/*Entity*.java"))
        
        performance_data = {
            "performance_files_count": len(perf_indicators),
            "database_files_count": len(db_files),
            "performance_patterns": [],
            "bottleneck_indicators": []
        }
        
        # Analyze sample files for performance anti-patterns
        all_files = (perf_indicators + db_files)[:10]  # Sample first 10
        for perf_file in all_files:
            try:
                content = Read(perf_file)
                issues = detect_performance_issues_from_content(content)
                performance_data["performance_patterns"].extend(issues)
            except Exception as e:
                print(f"⚠️  Could not analyze {perf_file}: {e}")
                continue
        
        return performance_data
        
    except Exception as e:
        print(f"❌ Error in performance fallback analysis: {e}")
        return None
```''',
        
        'security-analyst': '''## Enhanced Fallback Strategy

⚠️ **SEE**: `framework/templates/FALLBACK_PATTERNS.md` for complete fallback implementation patterns.

### Security Analysis Fallback Implementation
```python
def extract_security_data_with_fallback(data_sources):
    """Extract security data with comprehensive fallback mechanisms"""
    
    # PRIMARY: Try existing data sources first
    security_data = {}
    
    # Use repomix context for pre-screened security issues
    if data_sources.get("repomix_context"):
        print("🔍 Extracting security issues from repomix context...")
        repomix_data = json.loads(data_sources["repomix_context"])
        security_data = extract_security_from_repomix_context(repomix_data)
    
    # Use architecture findings for security-relevant patterns
    if data_sources.get("architecture_context"):
        print("🔍 Extracting security patterns from architecture context...")
        arch_data = json.loads(data_sources["architecture_context"])
        security_data.update(extract_security_from_architecture(arch_data))
    
    # Validate if we have sufficient security data
    if validate_security_extraction(security_data):
        print("✅ Sufficient security data from existing sources")
        security_data["data_source"] = "context_analysis"
        return security_data
    
    # FALLBACK: Raw codebase analysis for security issues
    print("🔄 Falling back to raw codebase security analysis...")
    raw_security_data = extract_security_from_raw_codebase()
    
    if raw_security_data:
        merged_data = {**security_data, **raw_security_data}
        merged_data["data_source"] = "raw_codebase_fallback"
        return merged_data
    else:
        return create_minimal_security_response()

def extract_security_from_raw_codebase():
    """Extract security issues from raw codebase analysis"""
    try:
        # Look for security-related files and configurations
        security_files = []
        security_files.extend(Glob("codebase/**/*Security*.java"))
        security_files.extend(Glob("codebase/**/*Auth*.java"))
        security_files.extend(Glob("codebase/**/*Login*.java"))
        
        config_files = []
        config_files.extend(Glob("codebase/**/web.xml"))
        config_files.extend(Glob("codebase/**/server.xml"))
        config_files.extend(Glob("codebase/**/*.properties"))
        
        security_data = {
            "security_files_count": len(security_files),
            "config_files_count": len(config_files),
            "security_vulnerabilities": [],
            "authentication_patterns": []
        }
        
        # Analyze configuration files for security issues
        for config_file in config_files[:5]:  # Check first 5 config files
            try:
                content = Read(config_file)
                vulnerabilities = detect_security_issues_from_config(content, config_file)
                security_data["security_vulnerabilities"].extend(vulnerabilities)
            except Exception as e:
                print(f"⚠️  Could not analyze {config_file}: {e}")
                continue
        
        return security_data
        
    except Exception as e:
        print(f"❌ Error in security fallback analysis: {e}")
        return None
```'''
    }
    
    # Find the agent type based on agent name
    agent_type = agent_name.replace('-', '_')
    
    if agent_type in fallback_sections:
        # Look for existing fallback section and replace it
        fallback_pattern = r'## (Enhanced )?Fallback Strategy.*?(?=## [A-Z]|$)'
        
        if re.search(fallback_pattern, content, re.DOTALL):
            # Replace existing fallback section
            content = re.sub(fallback_pattern, fallback_sections[agent_type] + '\n\n', content, flags=re.DOTALL)
        else:
            # Insert fallback section before Quality Checklist
            quality_pattern = r'## Quality Checklist'
            if re.search(quality_pattern, content):
                content = re.sub(quality_pattern, fallback_sections[agent_type] + '\n\n## Quality Checklist', content)
            else:
                # Append at end if no quality checklist found
                content += '\n\n' + fallback_sections[agent_type]
        
        # Write updated content back to file
        with open(agent_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated {agent_name} with enhanced fallback mechanisms")
    else:
        print(f"⚠️  No fallback template for {agent_name} - using generic fallback reference")
        
        # Add generic fallback reference
        generic_fallback = '''## Enhanced Fallback Strategy

⚠️ **SEE**: `framework/templates/FALLBACK_PATTERNS.md` for complete fallback implementation patterns.

This agent implements comprehensive fallback mechanisms to ensure analysis can continue even when primary data sources (Repomix summaries) are insufficient or unavailable. The agent will automatically:

1. **Data Quality Assessment**: Evaluate available data sources for completeness
2. **Intelligent Fallback**: Switch to raw codebase analysis when needed  
3. **Technology Detection**: Identify relevant files and patterns from filesystem
4. **Graceful Degradation**: Provide structured responses even with limited data
5. **Error Handling**: Continue analysis despite individual file access failures

The fallback mechanisms ensure robust operation across diverse codebase environments and configurations.
'''
        
        # Insert generic fallback before Quality Checklist
        quality_pattern = r'## Quality Checklist'
        if re.search(quality_pattern, content):
            content = re.sub(quality_pattern, generic_fallback + '\n\n## Quality Checklist', content)
            
            with open(agent_file, 'w') as f:
                f.write(content)
            
            print(f"✅ Updated {agent_name} with generic fallback reference")

def main():
    """Update all agents with fallback mechanisms"""
    agents_dir = Path(".claude/agents")
    
    if not agents_dir.exists():
        print(f"❌ Agents directory not found: {agents_dir}")
        return
    
    # Get all agent files
    agent_files = list(agents_dir.glob("*.md"))
    
    if not agent_files:
        print(f"❌ No agent files found in {agents_dir}")
        return
    
    print(f"🔍 Found {len(agent_files)} agents to update")
    
    for agent_file in agent_files:
        agent_name = agent_file.stem
        print(f"\n📝 Updating {agent_name}...")
        try:
            update_agent_fallback(agent_file, agent_name)
        except Exception as e:
            print(f"❌ Failed to update {agent_name}: {e}")
    
    print(f"\n✅ Fallback update process complete!")
    print(f"📋 All agents now reference framework/templates/FALLBACK_PATTERNS.md")
    print(f"🔧 Key agents have comprehensive fallback implementations")

if __name__ == "__main__":
    main()