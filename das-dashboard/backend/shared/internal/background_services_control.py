import asyncio


class BackgroundServicesControl:
    """Holds in-memory asyncio tasks for long-running background jobs."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.running_jobs = {}
        return cls._instance

    def _job_key(self, job_name: str, server_ip: str) -> str:
        return f"{job_name}:{server_ip}"

    def add_job(self, job_name: str, server_ip: str, task: asyncio.Task) -> None:
        self.running_jobs[self._job_key(job_name, server_ip)] = task

    def remove_job(self, job_name: str, server_ip: str) -> asyncio.Task | None:
        return self.running_jobs.pop(self._job_key(job_name, server_ip), None)

    def get_job(self, job_name: str, server_ip: str) -> asyncio.Task | None:
        return self.running_jobs.get(self._job_key(job_name, server_ip))

    def is_running(self, job_name: str, server_ip: str) -> bool:
        task = self.get_job(job_name, server_ip)
        return task is not None and not task.done()
