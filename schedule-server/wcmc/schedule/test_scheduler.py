import pytest
from pytest import fail

from wcmc.schedule.memory.scheduler import MemoryScheduler
from wcmc.schedule.scheduler import Scheduler, JobExecutor, Job, JobState

job_status_complete = Job(
    method="test_complete",
    samples=["test", "test2", "test3"],
    to_notify=["test@test.de"]
)

job_status_schedule = Job(
    method="test_schedule",
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


schedulers = [MemoryScheduler(executor=TestExecutor())]


@pytest.mark.parametrize("scheduler", schedulers)
def test_submit(scheduler):
    scheduler.submit(job=job_status_complete)
    assert scheduler.job_state(job_status_complete.generate_id()) == JobState.DONE

    scheduler.submit(job=job_status_schedule)
    assert scheduler.job_state(job_status_schedule.generate_id()) == JobState.SCHEDULED


@pytest.mark.parametrize("scheduler", schedulers)
def test_set_job_state(scheduler):
    scheduler.submit(job=job_status_schedule)
    assert scheduler.job_state(job_status_schedule.generate_id()) == JobState.SCHEDULED
    scheduler.set_job_state(job_status_schedule.generate_id(), JobState.DONE)
    assert scheduler.job_state(job_status_schedule.generate_id()) == JobState.DONE


@pytest.mark.parametrize("scheduler", schedulers)
def test_cancel(scheduler):
    scheduler.submit(job=job_status_schedule)
    assert scheduler.job_state(job_status_schedule.generate_id()) == JobState.SCHEDULED
    scheduler.cancel(job_status_schedule)
    assert scheduler.job_done(job_status_schedule.generate_id()) is False


@pytest.mark.parametrize("scheduler", schedulers)
def test_done(scheduler):
    scheduler.submit(job=job_status_schedule)
    assert scheduler.job_state(job_status_schedule.generate_id()) == JobState.SCHEDULED
    scheduler.set_job_state(job_status_schedule.generate_id(), JobState.DONE)
    assert scheduler.job_done(job_status_schedule.generate_id()) is True
