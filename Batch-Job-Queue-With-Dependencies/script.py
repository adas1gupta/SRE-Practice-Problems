from dataclasses import dataclass, field
from uuid import UUID, uuid4
from graphlib import TopologicalSorter
from concurrent.futures import ThreadPoolExecutor

@dataclass
class BatchJob:
    command: str
    job_id: UUID = field(default_factory=uuid4)
    dependencies: list[UUID] = field(default_factory=list)
    resource_requirements: dict = field(default_factory=dict)
    priority: int = 0
    max_retries: int = 3
    max_duration: float | None = None

class Scheduler:
    def __init__(self):
        self.jobs: dict[UUID, BatchJob] = {}
        self.job_state: dict[UUID, str] = {}
        self.retry_counts: dict[UUID, int] = {}
        self.dag: TopologicalSorter | None = None
        self.executor: ThreadPoolExecutor | None = None
        self.execution_log: list[dict] = []
