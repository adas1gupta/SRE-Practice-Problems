from dataclasses import dataclass, field
from uuid import UUID, uuid4

@dataclass
class BatchJob:
    command: str
    job_id: UUID = field(default_factory=uuid4)
    dependencies: list[UUID] = field(default_factory=list)
    resource_requirements: dict = field(default_factory=dict)
    priority: int = 0
    max_retries: int = 3
    max_duration: float | None = None