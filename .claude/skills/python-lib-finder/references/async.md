# Async & Concurrency

## Async Frameworks

| Library | Description | Use Case |
|---------|-------------|----------|
| **asyncio** | Standard library | I/O-bound concurrent tasks |
| **trio** | Friendly async library | Structured concurrency |
| **curio** | Coroutine-based | Educational concurrency |
| **gevent** | Greenlet-based | Legacy code compatibility |
| **twisted** | Event-driven engine | Network protocols |

## Async Enhancements

| Library | Description |
|---------|-------------|
| **uvloop** | Ultra fast asyncio event loop |
| **asyncpg** | Fast PostgreSQL driver |
| **aiosqlite** | Async SQLite |

## Parallel Processing

| Library | Type | Description |
|---------|------|-------------|
| **multiprocessing** | Standard | Process-based parallelism |
| **concurrent.futures** | Standard | High-level async executor |
| **dask** | Distributed | Flexible parallel computing |
| **Ray** | Distributed | Unified ML ecosystem |
| **PySpark** | Distributed | Apache Spark Python API |
| **luigi** | Batch | Build complex pipelines |
| **mpi4py** | MPI | Message passing interface |

## Task Queues

| Library | Backend | Async |
|---------|---------|-------|
| **celery** | RabbitMQ/Redis | Yes |
| **dramatiq** | Redis/RabbitMQ | Yes |
| **rq** | Redis | No |
| **huey** | Redis/SQLite | No |
| **mrq** | Redis + gevent | Yes |

## Job Schedulers

| Library | Description |
|---------|-------------|
| **APScheduler** | In-process task scheduler |
| **schedule** | Simple job scheduling |
| **Airflow** | Workflow orchestration |
| **Prefect** | Modern data pipeline orchestration |
| **doit** | Task runner and build tool |
