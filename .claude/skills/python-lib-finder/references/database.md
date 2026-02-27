# Database & ORM

## ORM (Relational Databases)

| Library | Description | Async | Notes |
|---------|-------------|-------|-------|
| **SQLAlchemy** | Python SQL Toolkit | Yes (2.0+) | Most popular, powerful |
| **Django Models** | Django's built-in ORM | Yes | Full-featured, batteries-included |
| **SQLModel** | Pydantic + SQLAlchemy | Yes | Type-friendly, FastAPI pairing |
| **peewee** | Small, expressive ORM | No | Lightweight |
| **pony** | Generator-oriented interface | Yes | Unique syntax |
| **dataset** | Store dicts in database | No | Simple abstraction |

## ORM (NoSQL Databases)

| Library | Database | Async |
|---------|----------|-------|
| **Beanie** | MongoDB | Yes |
| **mongoengine** | MongoDB | No |
| **ODMantic** | MongoDB | Yes |
| **PynamoDB** | DynamoDB | Yes |

## Database Drivers (SQL)

### PostgreSQL

| Library | Description |
|---------|-------------|
| **psycopg** | Most popular adapter |

### MySQL

| Library | Description |
|---------|-------------|
| **pymysql** | Pure Python driver |
| **mysqlclient** | C-based MySQL connector |

### SQLite

| Library | Description |
|---------|-------------|
| **sqlite3** | Built-in (standard library) |
| **sqlite-utils** | CLI and manipulation utilities |

### Other

| Library | Database | Description |
|---------|----------|-------------|
| **pymssql** | SQL Server | Microsoft SQL Server |
| **clickhouse-driver** | ClickHouse | Native interface |

## Database Drivers (NoSQL)

| Library | Database | Async |
|---------|----------|-------|
| **redis-py** | Redis | Yes |
| **pymongo** | MongoDB | Yes |
| **kafka-python** | Kafka | No |
| **cassandra-driver** | Cassandra | Yes |

## Embedded Databases

| Library | Type | Description |
|---------|------|-------------|
| **DuckDB** | OLAP | In-process analytical SQL |
| **tinydb** | Document | Tiny document-oriented |
| **pickleDB** | Key-value | Simple lightweight |

## Caching

| Library | Backend | Description |
|---------|---------|-------------|
| **python-diskcache** | Disk/SQLite | Fast lookups |
| **redis-py** | Redis | Distributed caching |
| **django-cacheops** | Django | ORM caching |
| **beaker** | WSGI | Sessions + caching |
| **dogpile.cache** | Generic | Next-gen Beaker |
