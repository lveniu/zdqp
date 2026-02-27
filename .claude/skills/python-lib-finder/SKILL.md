# Python Library Finder

Quickly find the most practical Python libraries for your project needs.

## When to Use

Use this skill when:
- Building a new Python project and need library recommendations
- Looking for alternatives to existing libraries
- Choosing libraries for specific functionality (web, data, testing, etc.)
- Comparing options within a category

## Quick Reference

Use `Grep` tool to search this skill's reference files:
```
Grep pattern="fastapi|django|flask" path=python-lib-finder/references/
```

## Categories

| Category | Reference File | Use For |
|----------|---------------|---------|
| Web Frameworks | `web.md` | APIs, full-stack apps |
| Data & Science | `data-science.md` | Analysis, ML, visualization |
| Testing | `testing.md` | Testing frameworks, mocks |
| Database | `database.md` | ORM, drivers, tools |
| Async & Concurrency | `async.md` | Asyncio, parallel processing |
| API & HTTP | `api.md` | REST, GraphQL, HTTP clients |
| CLI & Terminal | `cli.md` | Command-line apps, TUIs |
| File & Format | `formats.md` | PDF, Excel, JSON, parsing |
| Web Scraping | `scraping.md` | Crawlers, browser automation |
| DevOps & Tools | `devops.md` | Build, deploy, monitoring |

## Usage Examples

**Find a web framework:**
- Read [web.md](references/web.md) for Django, FastAPI, Flask options
- For async APIs: check Litestar or FastAPI
- For traditional full-stack: Django

**Database layer:**
- Read [database.md](references/database.md) for SQLAlchemy, Beanie options
- For async: Beanie (MongoDB) or SQLAlchemy 2.0+

**Testing:**
- Read [testing.md](references/testing.md) for pytest, hypothesis, locust
- Mocking: responses, VCR.py, freezegun

## Selection Guidelines

**Prefer libraries that are:**
1. Actively maintained (recent commits, releases)
2. Well-documented with examples
3. Type-annotated (mypy compatible)
4. Async-friendly when applicable

**Framework choices by use case:**
- Small API: FastAPI, Flask
- Enterprise app: Django
- Async services: FastAPI, Litestar, Tornado
- Data processing: pandas, polars
- ML/LLM: transformers, langchain
- Scraping: scrapy, playwright
