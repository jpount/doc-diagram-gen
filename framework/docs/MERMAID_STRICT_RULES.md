# Mermaid Diagram Strict Rules - Prevention First

## Core Principle
Prevent errors from being introduced rather than fixing them later.

## MANDATORY RULES FOR ALL DIAGRAMS

### 1. Universal Formatting Rules
```
✅ ALWAYS:
- Start file with diagram type declaration
- End file with exactly one newline
- Use spaces, never tabs
- Keep lines under 200 characters
- No trailing whitespace on any line

❌ NEVER:
- Use tabs anywhere
- Have more than 2 consecutive blank lines
- Mix spacing styles
```

### 2. Comment Rules
```
✅ CORRECT:
%% This comment starts at column 1
graph TD
    A --> B

❌ WRONG:
    %% This comment is indented (ERROR!)
graph TD
    A --> B
```

### 3. Node ID Rules
```
✅ CORRECT:
graph TD
    node1[Label]
    nodeA[Label]
    startNode[Label]

❌ WRONG:
graph TD
    1[Label]        %% Numeric-only IDs not allowed
    node-1[Label]   %% Hyphens in IDs cause issues
```

### 4. String and Label Rules
```
✅ CORRECT:
graph TD
    A[Simple Label]
    B["Label with (parentheses)"]
    C["Label with special chars: $&#"]

❌ WRONG:
graph TD
    A[Label with (parens)]  %% Unquoted parens
    B[Label: with colon]    %% Unquoted colon
```

### 5. Sequence Diagram Specific Rules
```
✅ CORRECT:
sequenceDiagram
    participant User
    participant System
    User->>System: Request
    Note over User: Single space after colon
    Note right of System: Processing

❌ WRONG:
sequenceDiagram
    participant "User as User/Browser"  %% Complex aliases
    User->>System:  Request             %% Multiple spaces after colon
    Note over User:  Multiple spaces     %% Multiple spaces
```

### 6. Class Diagram Specific Rules
```
✅ CORRECT:
classDiagram
    class User {
        +String name
        +login()
    }
    User <|-- Admin
    User --> Account : has

❌ WRONG:
classDiagram
    class User {
        <<@Entity>>      %% @ symbol not allowed
        +String name
    }
    User --> Account has  %% Missing colon before label
```

### 7. Flowchart/Graph Specific Rules
```
✅ CORRECT:
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process]
    B -->|No| D[End]
    
    subgraph "Complex Process"
        E[Step 1] --> F[Step 2]
    end

❌ WRONG:
graph TD
    A[Start] --> B{Decision}
    B --> |Yes| C[Process]  %% Space after arrow
    B-->|No|D[End]          %% No spaces (less readable but works)
    
    subgraph Complex Process  %% Unquoted multi-word
        E[Step 1] --> F[Step 2]
    %% Missing 'end' for subgraph
```

### 8. ER Diagram Specific Rules
```
✅ CORRECT:
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    PRODUCT ||--o{ LINE-ITEM : "included in"

❌ WRONG:
erDiagram
    CUSTOMER ||--o{ ORDER places      %% Missing colon
    ORDER |--| LINE-ITEM : contains   %% Invalid relationship syntax
```

### 9. State Diagram Rules
```
✅ CORRECT:
stateDiagram-v2
    [*] --> State1
    State1 --> State2 : Transition
    State2 --> [*]

❌ WRONG:
stateDiagram         %% Must use stateDiagram-v2
    [*] --> State1
    State1 --> State2
```

### 10. Special Character Rules
```
✅ SAFE CHARACTERS in labels (unquoted):
- Letters (a-z, A-Z)
- Numbers (0-9)
- Spaces
- Basic punctuation: . , ! ?

✅ REQUIRES QUOTES:
- Parentheses: ( )
- Brackets: [ ] { }
- Special: & $ # @ % ^ * = + | \ / < >
- Quotes themselves: " '
- Colons: :
- Semicolons: ;

✅ CORRECT ESCAPING:
graph TD
    A["Label with \"quotes\""]
    B["Label with (parens)"]
    C["Price: $100"]

❌ WRONG:
graph TD
    A[Label with "quotes"]
    B[Label with (parens)]
    C[Price: $100]
```

## ERROR PATTERNS AND FIXES

### Common Error: "Expecting 'COLON'"
**Cause**: Missing colon in relationship label
```
❌ WRONG: A --> B label
✅ FIX:   A --> B : label
```

### Common Error: "Expecting 'SQE', got 'PS'"
**Cause**: Unquoted special characters in labels
```
❌ WRONG: A[getMethod()]
✅ FIX:   A["getMethod()"]
```

### Common Error: "Parse error on line X"
**Cause**: Usually unbalanced brackets or missing end statements
```
❌ WRONG: 
subgraph Test
    A --> B
    %% Missing 'end'

✅ FIX:
subgraph Test
    A --> B
end
```

### Common Error: "Invalid syntax"
**Cause**: Indented comments or wrong diagram type
```
❌ WRONG:
    %% Indented comment
stateDiagram

✅ FIX:
%% Comment at column 1
stateDiagram-v2
```

## VALIDATION CHECKPOINTS

### 1. Pre-Write Checks
- Validate diagram type is correct
- Check for balanced brackets/braces
- Verify no indented comments
- Ensure proper node ID format
- Check for unquoted special characters

### 2. During Writing
- Apply safe transformations only
- Fix spacing issues
- Remove trailing whitespace
- Ensure file ends with newline

### 3. Post-Write Validation
- Run through Mermaid CLI
- Parse error messages
- Apply targeted fixes
- Re-validate

## IMPLEMENTATION PRIORITY

1. **PREVENT**: Follow rules when generating
2. **VALIDATE**: Check before writing
3. **FIX**: Apply safe, targeted fixes
4. **VERIFY**: Confirm in browser viewer