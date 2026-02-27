# Testing Frameworks & Tools

## Testing Frameworks

| Library | Description | Type |
|---------|-------------|------|
| **pytest** | Mature, full-featured test tool | General purpose |
| **unittest** | Python standard library | Built-in |
| **nose2** | Successor to nose | unittest-compatible |
| **hypothesis** | Property-based testing | QuickCheck style |
| **Robot Framework** | Generic test automation | Keyword-driven |
| **ScanAPI** | REST API testing | OpenAPI/Swagger |

## Test Runners

| Library | Description |
|---------|-------------|
| **tox** | Multi-version testing |
| **green** | Clean, colorful runner |
| **mamba** | BDD testing tool |

## Mock & Fake

### HTTP Mocking

| Library | Description |
|---------|-------------|
| **responses** | Mock requests library |
| **httpretty** | HTTP request mock |
| **httmock** | Requests mocking |
| **VCR.py** | Record/replay HTTP |
| **mocket** | Socket mock with async/SSL |

### Time Mocking

| Library | Description |
|---------|-------------|
| **freezegun** | Mock datetime module |

### General Mocking

| Library | Description |
|---------|-------------|
| **mock** | Built-in mocking library |
| **doublex** | Test doubles framework |

## Test Data Generation

| Library | Description |
|---------|-------------|
| **faker** | Generate fake data |
| **mimesis** | Fake data for various locales |
| **factory_boy** | Test fixtures replacement |
| **polyfactory** | Mock data with pydantic support |

## Code Coverage

| Library | Description |
|---------|-------------|
| **coverage** | Code coverage measurement |

## GUI/Web Testing

| Library | Description |
|---------|-------------|
| **Selenium** | Browser automation |
| **playwright**** | Modern browser automation (see web-scraping skill) |
| **splinter** | Web app testing |
| **locust** | Load testing |
| **PyAutoGUI** | GUI automation |
| **Schemathesis** | Property-based API testing |

## Static Analysis

### Linters

| Library | Description |
|---------|-------------|
| **ruff** | Extremely fast linter/formatter |
| **pylint** | Customizable source analyzer |
| **flake8** | Wrapper for pycodestyle/pyflakes |

### Formatters

| Library | Description |
|---------|-------------|
| **black** | Uncompromising formatter |
| **yapf** | Google's formatter |
| **isort** | Import sorting |

### Type Checkers

| Library | Description |
|---------|-------------|
| **mypy** | Static type checking |
| **pyre-check** | Performant type checker |
| **ty** | Fast type checker |

### Other Analysis

| Library | Description |
|---------|-------------|
| **vulture** | Find dead code |
| **prospector** | Code analysis tool |
| **code2flow** | Generate flowcharts |
