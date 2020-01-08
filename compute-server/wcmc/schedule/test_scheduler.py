import pytest

from wcmc.schedule.memory.scheduler import MemoryScheduler
from wcmc.schedule.scheduler import JobExecutor, Job, JobState, SampleStateService, SampleState
from wcmc.schedule.stasis.scheduler import AWSScheduler

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

job_status_run = Job(
    method="test_run",
    samples=["test", "test2", "test3", "test4failed", "test5failed"],
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
        elif job.method == "test_run":
            service: SampleStateService = self.scheduler.state_service

            for x in job.samples:
                if 'failed' in x:
                    service.set_state(job.generate_id(), x, SampleState.FAILED)
                else:
                    service.set_state(job.generate_id(), x, SampleState.DONE)

        return None


schedulers = [MemoryScheduler(executor=TestExecutor()), AWSScheduler(executor=TestExecutor())]


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


@pytest.mark.parametrize("scheduler", schedulers)
def test_done_with_failed_samples(scheduler):
    scheduler.submit(job=job_status_run)
    assert scheduler.job_done(job_status_run.generate_id()) is True
