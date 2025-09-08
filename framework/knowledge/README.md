# Knowledge Base for Documentation Framework

This directory contains technology-specific knowledge that agents dynamically load based on the detected tech stack.

## Structure

```
knowledge/
├── languages/       # Programming language-specific patterns and analysis
├── frameworks/      # Framework-specific knowledge
├── patterns/        # Architectural and design patterns
└── domains/        # Domain-specific business logic patterns
```

## How It Works

1. **Tech Stack Detection**: The framework detects technologies in your codebase
2. **Knowledge Loading**: Relevant knowledge files are loaded for the agents
3. **Contextual Analysis**: Agents use this knowledge to provide tech-specific insights

## Agent Mapping

- **architect-agent**: Uses patterns/ and frameworks/ for architecture analysis
- **developer-agent**: Uses languages/ and frameworks/ for code quality
- **analyst-agent**: Uses domains/ and patterns/ for business logic
- **diagram-agent**: Uses all categories for accurate visualizations
- **doc-writer-agent**: Synthesizes knowledge from all categories

## Adding New Technologies

To add support for a new technology:
1. Create a new .md file in the appropriate directory
2. Follow the template structure of existing files
3. Include patterns, anti-patterns, and best practices
4. Add detection rules in the tech-detection logic