from dataclasses import dataclass, field
from uuid import UUID, uuid4
from graphlib import TopologicalSorter
from concurrent.futures import ThreadPoolExecutor
from enum import Enum 

class JobState(Enum):
    PENDING = 1
    FAILED = 2
    BLOCKED = 3
    RUNNING = 4
    COMPLETED = 5


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
        self.job_state: dict[UUID, JobState] = {}
        self.retry_counts: dict[UUID, int] = {}
        self.dag: TopologicalSorter | None = None
        self.executor: ThreadPoolExecutor | None = None
        self.execution_log: list[dict] = []

    def submit_job(self, job: BatchJob) -> None:
        if job.job_id not in self.jobs:
            self.jobs[job.job_id] = job 
        else:
            raise ValueError(f"Job {job.job_id} already submitted")
        
        self.job_state[job.job_id] = JobState.PENDING
        self.retry_counts[job.job_id] = 0