# 🔄 Agent Fallback Patterns

## Overview

All agents MUST implement robust fallback mechanisms to access raw codebase data when Repomix summaries are insufficient or missing. This ensures agents can always complete their analysis regardless of data source availability.

## Data Source Hierarchy

ALL agents MUST follow this strict priority order:

1. **PRIMARY**: `output/reports/repomix-summary.md` (compressed codebase)
2. **SECONDARY**: `output/context/*.json` (previous agent outputs)
3. **FALLBACK**: Raw codebase access (codebase/ directory)

## Implementation Pattern

### Step 1: Data Source Detection and Loading

```python
def load_data_sources():
    """Load data sources with fallback detection"""
    data_sources = {
        "repomix_content": None,
        "repomix_context": None,
        "other_contexts": {},
        "fallback_needed": False,
        "data_quality": "unknown"
    }
    
    # PRIMARY: Try to read Repomix summary
    try:
        if Path("output/reports/repomix-summary.md").exists():
            data_sources["repomix_content"] = Read("output/reports/repomix-summary.md")
            print("✅ Repomix summary loaded successfully")
        else:
            print("⚠️  Repomix summary not found - will use raw codebase")
            data_sources["fallback_needed"] = True
    except Exception as e:
        print(f"❌ Failed to load Repomix summary: {e}")
        data_sources["fallback_needed"] = True
    
    # SECONDARY: Try to read previous agent contexts
    try:
        if Path("output/context/repomix-analyzer-summary.json").exists():
            data_sources["repomix_context"] = Read("output/context/repomix-analyzer-summary.json")
            print("✅ Repomix analyzer context loaded")
        else:
            print("⚠️  No repomix analyzer context found")
    except Exception as e:
        print(f"⚠️  Failed to load repomix analyzer context: {e}")
    
    # Load other agent contexts
    try:
        context_files = Glob("output/context/*-summary.json")
        for context_file in context_files:
            if context_file not in ["output/context/repomix-analyzer-summary.json", 
                                    f"output/context/{AGENT_NAME}-summary.json"]:
                agent_name = context_file.split('/')[-1].replace('-summary.json', '')
                data_sources["other_contexts"][agent_name] = Read(context_file)
                print(f"✅ Loaded context from {agent_name}")
    except Exception as e:
        print(f"⚠️  Error loading additional contexts: {e}")
    
    # Assess data quality
    data_sources["data_quality"] = assess_data_quality(data_sources)
    
    return data_sources

def assess_data_quality(data_sources):
    """Assess quality of available data sources"""
    if data_sources["repomix_content"] and len(data_sources["repomix_content"]) > 1000:
        return "excellent"  # Rich Repomix data available
    elif data_sources["repomix_context"] and len(data_sources["other_contexts"]) > 0:
        return "good"  # Context data available
    elif data_sources["repomix_content"]:
        return "limited"  # Minimal Repomix data
    else:
        return "fallback_required"  # Must use raw codebase
```

### Step 2: Intelligent Fallback Logic

```python
def extract_technology_info_with_fallback(data_sources):
    """Extract technology information with fallback to raw codebase"""
    tech_info = {}
    
    # Try PRIMARY source first
    if data_sources["repomix_content"] and data_sources["data_quality"] in ["excellent", "good"]:
        print("🔍 Extracting from Repomix summary...")
        tech_info = extract_from_repomix(data_sources["repomix_content"])
        
        # Validate extraction quality
        if tech_info and has_sufficient_data(tech_info):
            print("✅ Sufficient data extracted from Repomix")
            return tech_info
        else:
            print("⚠️  Repomix data insufficient, falling back to raw codebase")
    
    # FALLBACK: Raw codebase analysis
    print("🔄 Falling back to raw codebase analysis...")
    tech_info = extract_from_raw_codebase()
    
    if tech_info and has_sufficient_data(tech_info):
        print("✅ Data successfully extracted from raw codebase")
    else:
        print("❌ Unable to extract sufficient data from any source")
        tech_info = create_minimal_response()
    
    return tech_info

def extract_from_raw_codebase():
    """Extract information directly from raw codebase"""
    try:
        # Technology-specific file patterns
        tech_indicators = detect_technologies_from_files()
        
        # Extract based on detected technologies
        if "java" in tech_indicators:
            return extract_java_from_raw_codebase()
        elif "csharp" in tech_indicators:
            return extract_dotnet_from_raw_codebase()
        elif "typescript" in tech_indicators:
            return extract_angular_from_raw_codebase()
        else:
            return extract_generic_from_raw_codebase()
            
    except Exception as e:
        print(f"❌ Error during raw codebase extraction: {e}")
        return create_minimal_response()

def detect_technologies_from_files():
    """Detect technologies from file extensions and structure"""
    technologies = []
    
    try:
        # Java detection
        java_files = Glob("codebase/**/*.java")
        if java_files:
            technologies.append("java")
            print(f"🔍 Found {len(java_files)} Java files")
        
        # .NET detection
        csharp_files = Glob("codebase/**/*.cs") 
        project_files = Glob("codebase/**/*.csproj")
        if csharp_files or project_files:
            technologies.append("csharp")
            print(f"🔍 Found {len(csharp_files)} C# files, {len(project_files)} project files")
        
        # Angular/TypeScript detection
        ts_files = Glob("codebase/**/*.ts")
        angular_json = Glob("codebase/**/angular.json")
        if ts_files or angular_json:
            technologies.append("typescript")
            print(f"🔍 Found {len(ts_files)} TypeScript files, Angular config: {len(angular_json) > 0}")
        
        # Web files detection
        html_files = Glob("codebase/**/*.html")
        jsp_files = Glob("codebase/**/*.jsp")
        if html_files or jsp_files:
            technologies.append("web")
            print(f"🔍 Found {len(html_files)} HTML files, {len(jsp_files)} JSP files")
        
    except Exception as e:
        print(f"⚠️  Error detecting technologies: {e}")
    
    return technologies

def has_sufficient_data(tech_info):
    """Check if extracted data is sufficient for analysis"""
    if not tech_info:
        return False
    
    # Check for minimum required data
    required_fields = ["technology_detected", "file_count", "primary_language"]
    
    for field in required_fields:
        if field not in tech_info or not tech_info[field]:
            return False
    
    # Check data richness
    if tech_info.get("file_count", 0) < 1:
        return False
    
    return True

def create_minimal_response():
    """Create minimal response when no data can be extracted"""
    return {
        "technology_detected": "Unable to determine",
        "file_count": "Unable to determine", 
        "primary_language": "Unable to determine",
        "frameworks": "None detected",
        "architecture_pattern": "Unable to determine",
        "data_source": "insufficient_data",
        "fallback_attempted": True,
        "error_message": "Insufficient data in both Repomix summary and raw codebase"
    }
```

### Step 3: Technology-Specific Fallback Implementations

#### Java Fallback
```python
def extract_java_from_raw_codebase():
    """Java-specific raw codebase extraction"""
    try:
        java_info = {}
        
        # Find build files
        pom_files = Glob("codebase/**/pom.xml")
        gradle_files = Glob("codebase/**/build.gradle")
        
        if pom_files:
            java_info["build_system"] = "Maven"
            java_info["dependencies"] = extract_maven_dependencies(pom_files[0])
        elif gradle_files:
            java_info["build_system"] = "Gradle" 
            java_info["dependencies"] = extract_gradle_dependencies(gradle_files[0])
        
        # Find Java files and analyze
        java_files = Glob("codebase/**/*.java")
        java_info["file_count"] = len(java_files)
        java_info["primary_language"] = "Java"
        
        # Analyze key Java files
        java_info["frameworks"] = detect_java_frameworks(java_files[:10])  # Sample first 10
        java_info["architecture_pattern"] = detect_java_architecture(java_files)
        
        # Find configuration files
        config_files = Glob("codebase/**/persistence.xml") + Glob("codebase/**/application.properties")
        java_info["configuration_files"] = len(config_files)
        
        java_info["data_source"] = "raw_codebase"
        java_info["technology_detected"] = "Java"
        
        return java_info
        
    except Exception as e:
        print(f"❌ Error in Java fallback extraction: {e}")
        return None

def detect_java_frameworks(java_files):
    """Detect Java frameworks from import statements"""
    frameworks = []
    
    for file_path in java_files[:5]:  # Sample first 5 files
        try:
            content = Read(file_path)
            
            # Check for common frameworks
            if "import javax.ejb" in content:
                frameworks.append("EJB")
            if "import org.springframework" in content:
                frameworks.append("Spring Framework")
            if "import javax.persistence" in content:
                frameworks.append("JPA")
            if "import javax.jms" in content:
                frameworks.append("JMS")
            if "import javax.ws.rs" in content:
                frameworks.append("JAX-RS")
                
        except Exception as e:
            print(f"⚠️  Error reading Java file {file_path}: {e}")
            continue
    
    return list(set(frameworks))  # Remove duplicates
```

#### .NET Fallback
```python
def extract_dotnet_from_raw_codebase():
    """C#/.NET-specific raw codebase extraction"""
    try:
        dotnet_info = {}
        
        # Find project files
        csproj_files = Glob("codebase/**/*.csproj")
        sln_files = Glob("codebase/**/*.sln")
        
        if csproj_files:
            dotnet_info["project_files"] = len(csproj_files)
            dotnet_info["dotnet_version"] = extract_dotnet_version(csproj_files[0])
        
        # Find C# files and analyze
        cs_files = Glob("codebase/**/*.cs")
        dotnet_info["file_count"] = len(cs_files)
        dotnet_info["primary_language"] = "C#"
        
        # Analyze key C# files
        dotnet_info["frameworks"] = detect_dotnet_frameworks(cs_files[:10])
        dotnet_info["web_technology"] = detect_dotnet_web_tech(cs_files)
        
        # Check for specific file types
        aspx_files = Glob("codebase/**/*.aspx")
        razor_files = Glob("codebase/**/*.razor")
        
        if aspx_files:
            dotnet_info["ui_technology"] = "Web Forms"
        elif razor_files:
            dotnet_info["ui_technology"] = "Razor/MVC"
        
        dotnet_info["data_source"] = "raw_codebase"
        dotnet_info["technology_detected"] = ".NET"
        
        return dotnet_info
        
    except Exception as e:
        print(f"❌ Error in .NET fallback extraction: {e}")
        return None
```

#### Angular Fallback
```python
def extract_angular_from_raw_codebase():
    """Angular-specific raw codebase extraction"""
    try:
        angular_info = {}
        
        # Find Angular configuration
        angular_json = Glob("codebase/**/angular.json")
        package_json = Glob("codebase/**/package.json")
        
        if angular_json:
            angular_info["angular_config"] = True
            angular_info["angular_version"] = extract_angular_version_from_config(angular_json[0])
        elif package_json:
            angular_info["angular_version"] = extract_angular_version_from_package(package_json[0])
        
        # Find TypeScript files
        ts_files = Glob("codebase/**/*.ts")
        component_files = Glob("codebase/**/*.component.ts") 
        service_files = Glob("codebase/**/*.service.ts")
        
        angular_info["file_count"] = len(ts_files)
        angular_info["component_count"] = len(component_files)
        angular_info["service_count"] = len(service_files)
        angular_info["primary_language"] = "TypeScript"
        
        # Analyze key files for patterns
        angular_info["frameworks"] = detect_angular_frameworks(ts_files[:10])
        angular_info["ui_library"] = detect_angular_ui_libraries(ts_files)
        
        angular_info["data_source"] = "raw_codebase"
        angular_info["technology_detected"] = "Angular"
        
        return angular_info
        
    except Exception as e:
        print(f"❌ Error in Angular fallback extraction: {e}")
        return None
```

## Quality Assurance

### Fallback Validation
```python
def validate_fallback_results(extraction_results):
    """Validate that fallback extraction produced useful results"""
    if not extraction_results:
        return False, "No extraction results"
    
    # Check for minimum viable data
    essential_fields = ["technology_detected", "primary_language", "data_source"]
    missing_fields = [f for f in essential_fields if f not in extraction_results]
    
    if missing_fields:
        return False, f"Missing essential fields: {missing_fields}"
    
    # Check data quality
    if extraction_results["technology_detected"] == "Unable to determine":
        return False, "Technology could not be determined"
    
    return True, "Fallback extraction successful"
```

### Logging and Monitoring
```python
def log_fallback_usage(agent_name, fallback_reason, success):
    """Log fallback usage for monitoring"""
    fallback_log = {
        "agent": agent_name,
        "timestamp": datetime.now().isoformat(),
        "fallback_reason": fallback_reason,
        "success": success,
        "data_source_used": "raw_codebase" if success else "none"
    }
    
    # Append to fallback log file
    try:
        log_file = Path("logs/fallback_usage.json")
        if log_file.exists():
            existing_logs = json.loads(Read(str(log_file)))
        else:
            existing_logs = []
        
        existing_logs.append(fallback_log)
        Write(str(log_file), json.dumps(existing_logs, indent=2))
        
    except Exception as e:
        print(f"⚠️  Could not log fallback usage: {e}")
```

## Usage in Agents

Each agent should implement this pattern in their data loading section:

```python
# Step 1: Load data sources with fallback detection
data_sources = load_data_sources()

# Step 2: Extract technology information with intelligent fallback
tech_info = extract_technology_info_with_fallback(data_sources)

# Step 3: Validate results
is_valid, message = validate_fallback_results(tech_info)
if not is_valid:
    print(f"⚠️  Fallback extraction issues: {message}")
    tech_info = create_minimal_response()

# Step 4: Log fallback usage
if tech_info.get("data_source") == "raw_codebase":
    log_fallback_usage(AGENT_NAME, "repomix_insufficient", is_valid)

# Step 5: Proceed with analysis using extracted data
continue_with_analysis(tech_info)
```

## Error Handling

All fallback mechanisms MUST handle errors gracefully:

1. **File Access Errors**: Continue with available files
2. **Parsing Errors**: Log error and skip problematic files  
3. **Permission Errors**: Gracefully degrade functionality
4. **Memory Errors**: Process files in smaller batches

Never let fallback failures break the entire agent execution.