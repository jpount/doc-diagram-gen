# Hybrid Knowledge Process - How It Works

## 🎯 **Complete Flow Overview**

### **Phase 1: Setup (setup_simple.py)**
```
Step 1: Choose Mode (Quick/Guided)
Step 2: Configure Project 
Step 3: Select Documentation Types (12 types now available!)
Step 4: Hybrid Technology Detection ⭐ NEW
Step 5: Generate Configuration
```

### **Phase 2: Hybrid Technology Detection**

#### **🔍 Auto-Detection First**
```
🔍 Auto-detecting technologies in your codebase...

🎯 Auto-Detection Results:

Languages:
  • Java (High confidence)  
  • JavaScript (Medium confidence)

Frameworks:
  • Spring Boot (High confidence)
  • Angular (Low confidence)

Databases:
  • PostgreSQL (Medium confidence)
```

#### **✅ User Confirmation/Modification**
```
Confirm Technology Stack:
1. Use detected technologies ✅
2. Modify detected technologies
3. Manual selection (ignore detection)

Your choice [1-3]: 2

Modify Detected Technologies:
Current technologies:
  1. Java
  2. JavaScript  
  3. Spring Boot
  4. Angular
  5. PostgreSQL

Add technologies: 6,7     # Add React, MongoDB
Remove technologies: 4    # Remove Angular
```

#### **💾 Save Confirmed Stack**
- Saves to `analysis_config.json`
- Used by all agents during analysis
- Available for knowledge loading system

### **Phase 3: Agent Knowledge Loading**

When agents run, they use this process:

#### **🤖 In Each Agent**
```python
# Step 1: Load confirmed tech stack
from framework.scripts.knowledge_loader import load_knowledge_for_agent
knowledge_prompt = load_knowledge_for_agent("architect-agent")

# Step 2: Knowledge prompt provides:
# - Confirmed technology list
# - Relevant knowledge file contents  
# - Tech-specific patterns and commands
# - Fallback to generic if knowledge missing

# Step 3: Apply knowledge
# Use the loaded patterns for analysis
```

## 🧠 **Knowledge Loading Logic**

### **Priority Order:**
1. **User-Confirmed Tech Stack** (from analysis_config.json)
2. **Auto-Detection** (if no confirmed stack)  
3. **Generic Patterns** (if detection fails)

### **Knowledge File Mapping:**
```python
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
```

### **Fallback Behavior:**
```python
IF user_confirmed_tech_stack:
    → Load specific knowledge files
    → Use tech-specific patterns
    → High confidence analysis
    
ELIF auto_detection_successful:
    → Load detected knowledge
    → Use available patterns
    → Medium confidence analysis
    
ELSE:
    → Use generic patterns only
    → Basic analysis capabilities
    → Still functional but less specialized
```

## 🎯 **Benefits of Hybrid Approach**

### **✅ Best of Both Worlds**
- **Accurate Detection**: Real file scanning with confidence scoring
- **User Control**: Confirm, modify, or override completely
- **Flexibility**: Works with or without existing code
- **Intelligence**: Learns from user corrections

### **✅ Handles All Scenarios**

**Scenario 1: Perfect Detection**
- Auto-detects correctly → User confirms → Agents use specific knowledge

**Scenario 2: Partial Detection**  
- Detects some techs → User adds missing ones → Complete knowledge loading

**Scenario 3: Wrong Detection**
- Detects incorrectly → User overrides → Manual selection used

**Scenario 4: No Code Yet**
- Empty project → Manual selection → Knowledge ready for when code added

**Scenario 5: Detection Fails**
- Error in detection → Fallback to manual → Always functional

## 🔧 **Agent Usage Examples**

### **architect-agent with Java/Spring:**
```python
knowledge_prompt = load_knowledge_for_agent("architect-agent")
# Returns:
# - Java architecture patterns
# - Spring framework patterns
# - EJB/J2EE patterns (if detected)
# - Performance optimization techniques
# - Security vulnerability checks
```

### **analyst-agent with Python/Django:**
```python  
knowledge_prompt = load_knowledge_for_agent("analyst-agent")
# Returns:
# - Python security patterns (pickle, YAML issues)
# - Django ORM performance patterns
# - Python business logic extraction
# - FastAPI/Flask comparison patterns
```

### **Generic Fallback:**
```python
knowledge_prompt = load_knowledge_for_agent("analyst-agent")  # No tech detected
# Returns:
# - Generic architecture patterns
# - Basic security checks
# - General performance analysis
# - Still functional analysis
```

## 📋 **Complete Documentation Types Available**

Now includes all the missing types you mentioned:

```
1. Architecture Documentation (recommended)
2. Business Rules & Domain Logic
3. Security Assessment
4. Performance Analysis
5. API Documentation
6. Code Quality & Technical Debt (recommended)
7. Migration/Modernization Plan
8. UI/UX Analysis ✅ RESTORED
9. Developer/Troubleshooting Guide ✅ RESTORED
10. Executive Summary ✅ RESTORED
11. Deployment & Operations Guide ✅ NEW
12. Database Schema & Data Model ✅ NEW
```

## 🚀 **Ready to Test!**

The hybrid system now:
- ✅ **Auto-detects real technologies** (no more fake PostgreSQL/Kubernetes)
- ✅ **Asks user to confirm/modify** (full control)
- ✅ **Loads appropriate knowledge** (tech-specific analysis)
- ✅ **Fallback to generic** (always functional)
- ✅ **All documentation types** (UI, developer guides, executive summary)

**Try running `python3 setup_simple.py` - you'll get the full hybrid experience!** 🎯