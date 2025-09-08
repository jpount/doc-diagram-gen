#!/usr/bin/env python3
"""
Knowledge Loading System for Agents
Automatically detects technologies and loads appropriate knowledge files
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Optional
import re

class TechnologyDetector:
    """Detects technologies in codebase and loads appropriate knowledge"""
    
    def __init__(self, project_root: Path = Path(".")):
        self.project_root = Path(project_root)
        self.knowledge_dir = self.project_root / "framework" / "knowledge"
        self.codebase_dir = self.project_root / "codebase"
        
    def detect_technologies(self, project_name: str) -> Dict[str, any]:
        """Detect technologies in the project codebase"""
        project_path = self.codebase_dir / project_name
        
        if not project_path.exists():
            return {"error": "Project path does not exist", "technologies": []}
        
        detected = {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "tools": [],
            "confidence": {}
        }
        
        # Detection rules with confidence scoring
        detection_rules = {
            # Languages
            "Java": {
                "patterns": ["*.java", "pom.xml", "build.gradle"],
                "type": "language",
                "confidence_boost": ["src/main/java", "src/test/java"]
            },
            "JavaScript": {
                "patterns": ["*.js", "*.mjs", "package.json"],
                "type": "language",
                "confidence_boost": ["node_modules", "src/**/*.js"]
            },
            "TypeScript": {
                "patterns": ["*.ts", "*.tsx", "tsconfig.json"],
                "type": "language",
                "confidence_boost": ["@types/", "typescript"]
            },
            "Python": {
                "patterns": ["*.py", "requirements.txt", "setup.py", "pyproject.toml"],
                "type": "language",
                "confidence_boost": ["venv/", "virtualenv/", "__pycache__/"]
            },
            "C#/.NET": {
                "patterns": ["*.cs", "*.csproj", "*.sln"],
                "type": "language",
                "confidence_boost": ["bin/", "obj/", "packages/"]
            },
            
            # Frameworks
            "Spring": {
                "patterns": ["application.properties", "application.yml"],
                "type": "framework",
                "requires": ["Java"],
                "confidence_boost": ["@SpringBootApplication", "@Controller"]
            },
            "J2EE/Jakarta EE": {
                "patterns": ["web.xml", "ejb-jar.xml", "*.ear", "*.war"],
                "type": "framework", 
                "requires": ["Java"],
                "confidence_boost": ["WEB-INF/", "META-INF/application.xml"]
            },
            "Angular": {
                "patterns": ["angular.json", "*.component.ts"],
                "type": "framework",
                "requires": ["TypeScript"],
                "confidence_boost": ["@angular/core", "ng serve"]
            },
            "React": {
                "patterns": ["*.jsx", "*.tsx"],
                "type": "framework",
                "requires": ["JavaScript"],
                "confidence_boost": ["react-dom", "create-react-app"]
            },
            "Django": {
                "patterns": ["manage.py", "settings.py"],
                "type": "framework",
                "requires": ["Python"],
                "confidence_boost": ["django/", "INSTALLED_APPS"]
            },
            "Flask": {
                "patterns": ["app.py"],
                "type": "framework", 
                "requires": ["Python"],
                "confidence_boost": ["from flask import", "@app.route"]
            },
            "Express": {
                "patterns": ["package.json"],
                "type": "framework",
                "requires": ["JavaScript"],
                "confidence_boost": ["express", "app.listen"]
            },
            
            # Databases
            "PostgreSQL": {
                "patterns": ["*.sql"],
                "type": "database",
                "confidence_boost": ["psql", "postgresql://", "pg_"]
            },
            "MySQL": {
                "patterns": ["*.sql"],
                "type": "database",
                "confidence_boost": ["mysql://", "mysqldump"]
            },
            "MongoDB": {
                "patterns": ["*.bson"],
                "type": "database",
                "confidence_boost": ["mongodb://", "mongoose"]
            }
        }
        
        # Scan for technologies
        for tech_name, rules in detection_rules.items():
            confidence = 0
            found = False
            
            # Check basic patterns
            for pattern in rules["patterns"]:
                if pattern.startswith("*."):
                    if list(project_path.rglob(pattern)):
                        found = True
                        confidence += 10
                        break
                else:
                    if (project_path / pattern).exists() or list(project_path.rglob(pattern)):
                        found = True
                        confidence += 10
                        break
            
            # Check confidence boosters
            if found and "confidence_boost" in rules:
                for boost_pattern in rules["confidence_boost"]:
                    if boost_pattern.startswith("@") or "import" in boost_pattern:
                        # Content-based detection (would need file scanning)
                        confidence += 5  # Lower confidence for content patterns
                    else:
                        if list(project_path.rglob(boost_pattern)):
                            confidence += 15
            
            # Check dependencies
            if found and "requires" in rules:
                for req in rules["requires"]:
                    if req not in [t for tech_list in detected.values() for t in tech_list if isinstance(tech_list, list)]:
                        confidence -= 5  # Reduce if dependency not found
            
            # Add to detected list if found
            if found:
                tech_type = rules["type"]
                detected[tech_type + "s"].append(tech_name)
                detected["confidence"][tech_name] = confidence
        
        return detected
    
    def load_relevant_knowledge(self, detected_tech: Dict) -> Dict[str, str]:
        """Load knowledge files based on detected technologies"""
        knowledge_content = {}
        
        # Map technologies to knowledge files
        tech_to_files = {
            "Java": ["languages/java.md"],
            "J2EE/Jakarta EE": ["languages/j2ee.md"],
            "JavaScript": ["languages/javascript.md"],
            "TypeScript": ["languages/javascript.md"],  # Same file
            "Python": ["languages/python.md"],
            "C#/.NET": ["languages/dotnet.md"],
            "Angular": ["frameworks/angular.md"],
            "Spring": ["languages/java.md"],  # Spring patterns in Java file
        }
        
        # Load knowledge files for detected technologies
        all_detected = []
        for tech_list in detected_tech.values():
            if isinstance(tech_list, list):
                all_detected.extend(tech_list)
        
        for tech in all_detected:
            if tech in tech_to_files:
                for knowledge_file in tech_to_files[tech]:
                    file_path = self.knowledge_dir / knowledge_file
                    if file_path.exists():
                        with open(file_path, 'r') as f:
                            knowledge_content[knowledge_file] = f.read()
        
        # Always load generic patterns
        patterns_dir = self.knowledge_dir / "patterns"
        if patterns_dir.exists():
            for pattern_file in patterns_dir.glob("*.md"):
                with open(pattern_file, 'r') as f:
                    knowledge_content[f"patterns/{pattern_file.name}"] = f.read()
        
        return knowledge_content
    
    def get_agent_knowledge_prompt(self, agent_name: str, detected_tech: Dict) -> str:
        """Generate knowledge prompt for an agent based on detected technologies"""
        knowledge = self.load_relevant_knowledge(detected_tech)
        
        if not knowledge:
            return "No specific technology knowledge available. Use generic analysis patterns."
        
        prompt = f"""
## Technology-Specific Knowledge for {agent_name}

Based on the detected technology stack, you have access to the following specialized knowledge:

### Detected Technologies:
"""
        
        for tech_type, techs in detected_tech.items():
            if isinstance(techs, list) and techs:
                prompt += f"- **{tech_type.title()}**: {', '.join(techs)}\n"
        
        prompt += "\n### Available Knowledge Files:\n"
        for file_name, content in knowledge.items():
            prompt += f"- `{file_name}` - Loaded and available\n"
        
        prompt += f"""
### How to Use This Knowledge:

1. **Load Relevant Patterns**: Reference the knowledge files for technology-specific analysis patterns
2. **Apply Best Practices**: Use the technology-specific best practices from the knowledge files  
3. **Check for Anti-patterns**: Look for the technology-specific anti-patterns listed in the knowledge
4. **Use Specific Commands**: Leverage the bash commands and analysis techniques for the detected technologies

### Knowledge Content Available:
"""
        
        # Include a summary of each knowledge file
        for file_name, content in knowledge.items():
            lines = content.split('\n')
            # Extract first few meaningful lines as summary
            summary_lines = []
            for line in lines[1:20]:  # Skip title
                if line.strip() and not line.startswith('#'):
                    summary_lines.append(line.strip())
                if len(summary_lines) >= 3:
                    break
            
            prompt += f"\n#### {file_name}:\n"
            prompt += '\n'.join(f"- {line}" for line in summary_lines[:3])
            prompt += "\n"
        
        return prompt

# Example usage for agents
def load_knowledge_for_agent(agent_name: str, project_name: str = None) -> str:
    """Helper function for agents to load technology-specific knowledge"""
    detector = TechnologyDetector()
    
    # First try to load confirmed tech stack from setup
    confirmed_tech = load_confirmed_tech_stack()
    if confirmed_tech:
        print(f"✅ Using confirmed technology stack: {', '.join(confirmed_tech)}")
        # Convert flat list back to categorized format for knowledge loading
        detected_tech = categorize_technologies(confirmed_tech)
    else:
        # Fallback to auto-detection
        print(f"🔍 Auto-detecting technologies in codebase...")
        if not project_name:
            # Try to get project name from config
            try:
                import json
                with open("analysis_config.json", "r") as f:
                    config = json.load(f)
                project_name = config["project_name"]
            except:
                project_name = "default-project"
        
        detected_tech = detector.detect_technologies(project_name)
    
    return detector.get_agent_knowledge_prompt(agent_name, detected_tech)

def load_confirmed_tech_stack() -> Optional[List[str]]:
    """Load the technology stack confirmed by user during setup"""
    try:
        import json
        with open("analysis_config.json", "r") as f:
            config = json.load(f)
        return config.get("detected_tech", [])
    except:
        return None

def categorize_technologies(tech_list: List[str]) -> Dict[str, List[str]]:
    """Convert flat tech list back to categorized format"""
    categories = {
        "languages": [],
        "frameworks": [],
        "databases": [],
        "tools": [],
        "confidence": {}
    }
    
    # Technology categorization
    language_techs = ["Java", "JavaScript", "TypeScript", "Python", "C#/.NET", "C#", ".NET"]
    framework_techs = ["Spring", "Spring Boot", "J2EE", "J2EE/Jakarta EE", "Angular", "React", "Vue", "Django", "Flask", "FastAPI", "ASP.NET", ".NET Core"]
    database_techs = ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Oracle"]
    tool_techs = ["Docker", "Kubernetes", "AWS", "Azure"]
    
    for tech in tech_list:
        if tech in language_techs:
            categories["languages"].append(tech)
        elif tech in framework_techs:
            categories["frameworks"].append(tech)
        elif tech in database_techs:
            categories["databases"].append(tech)
        elif tech in tool_techs:
            categories["tools"].append(tech)
        # Set high confidence for user-confirmed technologies
        categories["confidence"][tech] = 25  # High confidence
    
    return categories

if __name__ == "__main__":
    # Test the knowledge loading system
    detector = TechnologyDetector()
    
    # Test detection (would normally use actual project)
    test_project = "test-project"
    detected = detector.detect_technologies(test_project)
    print("Detected technologies:")
    print(json.dumps(detected, indent=2))
    
    # Test knowledge loading
    knowledge = detector.load_relevant_knowledge(detected)
    print(f"\nLoaded {len(knowledge)} knowledge files")
    
    # Test agent prompt generation
    prompt = detector.get_agent_knowledge_prompt("architect-agent", detected)
    print(f"\nGenerated prompt length: {len(prompt)} characters")