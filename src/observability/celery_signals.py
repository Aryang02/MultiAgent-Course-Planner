import time

from celery.signals import task_failure, task_postrun, task_prerun, task_retry

from src.observability.logging import get_logger

logger = get_logger(__name__)
_task_start_times: dict[str, float] = {}


@task_prerun.connect
def on_task_prerun(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    _task_start_times[task_id] = time.perf_counter()
    logger.info(
        "celery_task_started",
        task_id=task_id,
        task_name=getattr(sender, "name", None) or str(task),
        retry=getattr(task.request, "retries", 0) if task else 0,
    )


@task_postrun.connect
def on_task_postrun(sender=None, task_id=None, task=None, state=None, **extra):
    started = _task_start_times.pop(task_id, None)
    duration_ms = round((time.perf_counter() - started) * 1000, 2) if started else None
    logger.info(
        "celery_task_finished",
        task_id=task_id,
        task_name=getattr(sender, "name", None) or str(task),
        state=state,
        duration_ms=duration_ms,
    )


@task_retry.connect
def on_task_retry(sender=None, request=None, reason=None, **extra):
    logger.warning(
        "celery_task_retry",
        task_id=getattr(request, "id", None),
        task_name=getattr(sender, "name", None),
        retry=getattr(request, "retries", 0),
        reason=str(reason),
    )


@task_failure.connect
def on_task_failure(
    sender=None,
    task_id=None,
    exception=None,
    traceback=None,
    einfo=None,
    **extra,
):
    logger.error(
        "celery_task_failed",
        task_id=task_id,
        task_name=getattr(sender, "name", None),
        error=str(exception),
        exc_info=True,
    )
