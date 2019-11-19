import pytest
from pytest import fail

from wcmc.schedule.scheduler import Scheduler, JobExecutor, Job, JobState

job = Job(
    method="test abc",
    samples=["test", "test2", "test3"],
    to_notify=["test@test.de"]
)


class TestExecutor(JobExecutor):
    """
    dummy test executor, doesn't really do anything
    except to return some different status codes to test the api
    """

    def execute(self, job: Job):
        assert job.generate_id() != ""
        assert len(job.samples) > 0

        if job.method == "test_complete":
            return JobState.DONE
        elif job.method == "test_schedule":
            return JobState.SCHEDULED

        return None


schedulers = [Scheduler(executor=TestExecutor())]


@pytest.mark.parametrize("scheduler", schedulers)
def test_submit(scheduler):
    scheduler.submit(job=job)
    assert scheduler.job_state(job.generate_id()) == JobState.SCHEDULED


@pytest.mark.parametrize("scheduler", schedulers)
def test_set_job_state(scheduler):
    fail()


@pytest.mark.parametrize("scheduler", schedulers)
def test_cancel(scheduler):
    fail()


@pytest.mark.parametrize("scheduler", schedulers)
def test_done(scheduler):
    fail()


@pytest.mark.parametrize("scheduler", schedulers)
def test_job_done(scheduler):
    fail()


@pytest.mark.parametrize("scheduler", schedulers)
def test_job_state(scheduler):
    fail()
