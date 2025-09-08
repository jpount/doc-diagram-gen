# Python Knowledge Base

## Detection Patterns
- Python files: `.py`, `.pyw`, `.pyx`, `.pyi`, `.pyc`
- Config files: `setup.py`, `setup.cfg`, `pyproject.toml`, `requirements.txt`, `Pipfile`, `poetry.lock`
- Environment files: `.env`, `.python-version`, `venv/`, `virtualenv/`
- Testing files: `pytest.ini`, `tox.ini`, `.coveragerc`
- Type checking: `mypy.ini`, `.mypy_cache/`, `py.typed`

## Python Versions & Environments
- **Python 2.7** (EOL, legacy)
- **Python 3.6-3.12** (modern versions)
- **CPython**: Reference implementation
- **PyPy**: JIT-compiled Python
- **Anaconda**: Scientific Python distribution
- **Virtual Environments**: venv, virtualenv, conda

## Common Frameworks & Libraries

### Web Frameworks
- **Django**: Full-featured web framework
- **Flask**: Microframework for web
- **FastAPI**: Modern async API framework
- **Pyramid**: Flexible web framework
- **Tornado**: Async web framework
- **Bottle**: Simple micro-framework
- **Sanic**: Async web framework

### Data Science & ML
- **NumPy**: Numerical computing
- **Pandas**: Data manipulation
- **Scikit-learn**: Machine learning
- **TensorFlow/Keras**: Deep learning
- **PyTorch**: Deep learning
- **Matplotlib/Seaborn**: Visualization
- **Jupyter**: Interactive notebooks

### Async Frameworks
- **asyncio**: Built-in async support
- **aiohttp**: Async HTTP client/server
- **Celery**: Distributed task queue
- **RQ (Redis Queue)**: Simple job queue
- **Dramatiq**: Task processing

### ORMs & Database
- **SQLAlchemy**: SQL toolkit and ORM
- **Django ORM**: Django's built-in ORM
- **Peewee**: Simple ORM
- **Tortoise ORM**: Async ORM
- **MongoEngine**: MongoDB ORM
- **Redis-py**: Redis client

## Analysis Focus Areas

### Code Quality Checks
- **Large Modules**: > 1000 lines
- **Complex Functions**: Cyclomatic complexity > 10
- **Long Functions**: > 50 lines
- **Deep Nesting**: > 4 levels
- **Line Length**: > 79 characters (PEP 8)
- **Missing Docstrings**: Functions/classes without docs
- **Import Organization**: PEP 8 compliance

### Python-Specific Issues
- **Python 2 vs 3**: Compatibility issues
- **Type Hints**: Missing or incorrect annotations
- **Global State**: Overuse of global variables
- **Mutable Defaults**: Functions with mutable default arguments
- **Exception Handling**: Bare except clauses
- **Resource Management**: Missing context managers
- **Import Cycles**: Circular dependencies

### Security Vulnerabilities
- **SQL Injection**: Raw SQL queries
- **Command Injection**: subprocess with shell=True
- **Path Traversal**: Unsanitized file paths
- **Pickle Deserialization**: Unsafe unpickling
- **YAML Loading**: yaml.load() without safe loader
- **Hardcoded Secrets**: API keys, passwords
- **Weak Cryptography**: MD5, SHA1 usage
- **Input Validation**: Missing sanitization

### Performance Issues
- **N+1 Queries**: ORM inefficiencies
- **Synchronous I/O**: Blocking operations
- **Memory Leaks**: Circular references
- **Inefficient Loops**: List comprehension opportunities
- **String Concatenation**: In loops without join()
- **Missing Caching**: Repeated computations
- **Large Data Loading**: Loading entire files to memory
- **GIL Bottlenecks**: CPU-bound threading

### Anti-patterns to Detect
- **God Classes**: Oversized classes
- **Spaghetti Code**: Poor structure
- **Copy-Paste Programming**: Code duplication
- **Magic Numbers**: Hardcoded values
- **Dead Code**: Unreachable code
- **Primitive Obsession**: Overuse of primitives
- **Feature Envy**: Methods using other class's data

### Best Practices
- Follow PEP 8 style guide
- Use type hints (Python 3.5+)
- Implement proper logging
- Use virtual environments
- Write comprehensive tests
- Use context managers for resources
- Implement error handling properly
- Use f-strings for formatting (3.6+)
- Leverage list/dict comprehensions appropriately
- Document with docstrings

## Python-Specific Patterns

### Design Patterns
- **Singleton**: Module-level instances
- **Factory**: Class methods as factories
- **Decorator**: Function/class decorators
- **Iterator**: __iter__ and __next__
- **Context Manager**: with statement support
- **Observer**: Event-driven patterns

### Pythonic Idioms
- **EAFP**: Easier to Ask Forgiveness than Permission
- **Duck Typing**: Interface through behavior
- **List Comprehensions**: Concise list creation
- **Generator Expressions**: Memory-efficient iteration
- **Unpacking**: Multiple assignment
- **Enumerate**: Index with iteration
- **Zip**: Parallel iteration
- **Properties**: Getter/setter decorators

## Package Management

### Dependency Management
- **pip**: Package installer
- **pipenv**: Pip + virtualenv
- **poetry**: Modern dependency management
- **conda**: Package and environment manager
- **requirements.txt**: Traditional dependencies
- **setup.py/setup.cfg**: Package configuration
- **pyproject.toml**: Modern project configuration

### Package Quality Checks
- **Security Audit**: safety, pip-audit
- **Outdated Packages**: pip list --outdated
- **Unused Dependencies**: pipdeptree
- **License Compliance**: pip-licenses
- **Version Pinning**: Exact vs range versions

## Testing Patterns

### Testing Frameworks
- **pytest**: Modern testing framework
- **unittest**: Built-in testing
- **nose2**: Extended unittest
- **doctest**: Doctring tests
- **tox**: Test automation
- **coverage.py**: Code coverage

### Testing Best Practices
- Unit test coverage > 80%
- Integration tests for APIs
- Mocking external dependencies
- Fixtures for test data
- Parametrized tests
- Test isolation
- CI/CD integration

## Type Checking

### Static Type Analysis
- **mypy**: Static type checker
- **pyright**: Microsoft's type checker
- **pyre**: Facebook's type checker
- **pytype**: Google's type checker

### Type Hints Patterns
```python
from typing import List, Dict, Optional, Union, Callable, TypeVar, Generic
```

## Django-Specific

### Django Patterns
- **Models**: Database schema
- **Views**: Request handlers
- **Templates**: HTML rendering
- **Forms**: Input validation
- **Middleware**: Request/response processing
- **Signals**: Event handling
- **Admin**: Auto-generated interface

### Django Issues
- **N+1 Queries**: Missing select_related/prefetch_related
- **Migration Conflicts**: Parallel development
- **Settings Management**: Environment-specific configs
- **Static Files**: Improper handling
- **CSRF/XSS**: Security misconfigurations
- **Database Transactions**: Improper scope

## Flask-Specific

### Flask Patterns
- **Blueprints**: Application organization
- **Application Factory**: App creation pattern
- **Extensions**: Flask-SQLAlchemy, Flask-Login
- **Context Locals**: g, request, session
- **Error Handlers**: Custom error pages

### Flask Issues
- **Circular Imports**: Poor structure
- **Global State**: App instance issues
- **Configuration**: Environment management
- **Database Connections**: Connection pooling
- **Session Security**: Secret key management

## FastAPI-Specific

### FastAPI Patterns
- **Dependency Injection**: Depends() system
- **Pydantic Models**: Request/response validation
- **Async Handlers**: Async/await support
- **OpenAPI**: Automatic documentation
- **Background Tasks**: Async task execution

### FastAPI Issues
- **Sync in Async**: Blocking operations
- **N+1 Queries**: ORM issues with async
- **Dependency Overhead**: Complex dependency trees
- **Response Model**: Missing validation
- **CORS Configuration**: Security issues

## Migration Strategies

### Python 2 to 3
1. **Use 2to3 tool**: Automatic conversion
2. **Fix imports**: __future__ imports
3. **Update print statements**: print() function
4. **Handle strings**: bytes vs str
5. **Update libraries**: Python 3 compatible versions

### Legacy to Modern
- **Old-style classes → New-style classes**
- **% formatting → f-strings**
- **os.path → pathlib**
- **Threading → asyncio**
- **XML → JSON APIs**

### Monolith to Microservices
1. Identify service boundaries
2. Extract shared libraries
3. Implement API gateway
4. Add message queue (RabbitMQ/Kafka)
5. Implement service discovery

## Specific Checks for Agents

### For architect-agent
- Package structure analysis
- Dependency graph
- API design patterns
- Database schema
- Service boundaries

### For developer-agent
- PEP 8 compliance
- Type hint coverage
- Test coverage
- Complexity metrics
- Security scan results

### For analyst-agent
- Business logic extraction
- Data flow analysis
- API endpoint mapping
- Background job patterns
- Event handling

### For diagram-agent
- Module dependencies
- Class hierarchies
- Database ERD
- API flow diagrams
- Async task flows

## Data Science Patterns

### Common Issues
- **Memory Management**: Large dataset handling
- **Vectorization**: Missing NumPy optimizations
- **Data Leakage**: Train/test contamination
- **Feature Engineering**: Poor feature selection
- **Model Persistence**: Pickle security issues
- **Notebook Organization**: Messy Jupyter notebooks

### Best Practices
- Use vectorized operations
- Implement proper cross-validation
- Version control models
- Document data pipelines
- Use appropriate data types
- Implement reproducible workflows