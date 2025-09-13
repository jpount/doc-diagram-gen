# Language Reference Documentation Directory

This directory contains PDF reference documentation for programming languages to enhance agent analysis capabilities.

## Structure

Place PDF reference documents here to enhance language-specific agents:

```
framework/references/
├── delphi-language-reference.pdf     # Delphi/Object Pascal reference
├── delphi-vcl-components.pdf         # VCL component reference  
├── delphi-database-programming.pdf   # Delphi database patterns
├── php-language-reference.pdf        # PHP language reference
├── php-security-guide.pdf            # PHP security best practices
├── laravel-framework-guide.pdf       # Laravel framework reference
├── symfony-architecture.pdf          # Symfony framework reference
└── [language]-[topic].pdf            # Additional references
```

## Usage

Language-specific agents (like `@delphi-architect` and `@php-architect`) will automatically:

1. **Detect Reference PDFs**: Scan this directory for relevant documentation
2. **Load PDF Content**: Read PDF content using Claude's native PDF capabilities  
3. **Extract Patterns**: Extract language-specific patterns, frameworks, and best practices
4. **Enhanced Analysis**: Use reference knowledge to identify obscure patterns and provide better recommendations

## Supported Languages

Currently supported language agents with PDF reference integration:
- **Delphi/Object Pascal**: `@delphi-architect`
- **PHP**: `@php-architect`

## Adding New Language References

To add references for a new language:

1. **Place PDFs**: Add language reference PDFs using naming convention `[language]-[topic].pdf`
2. **Update Agent**: Ensure the language agent includes PDF loading logic
3. **Test Integration**: Run agent to verify PDF content is loaded successfully

## Benefits

- **Obscure Language Support**: Enhanced analysis of less common languages like Delphi
- **Comprehensive Patterns**: Detect framework-specific patterns from official documentation  
- **Security Knowledge**: Reference security best practices for vulnerability detection
- **Legacy Support**: Better analysis of older language versions and deprecated features
- **Framework Expertise**: Deep knowledge of framework internals and best practices

## Example Usage

```python
# In agent code
delphi_refs = Glob("framework/references/delphi-*.pdf")
for pdf_file in delphi_refs:
    pdf_content = Read(pdf_file)  # Claude can read PDFs natively
    # Extract patterns and knowledge from PDF content
```

This approach allows agents to leverage comprehensive reference documentation for accurate analysis of specialized or obscure programming languages.