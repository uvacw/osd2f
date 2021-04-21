import asyncio
import logging.handlers
import queue
import typing

from tortoise import Tortoise, fields
from tortoise.models import Model

from .definitions import Submission, SubmissionList
from .logger import logger


class DBSubmission(Model):
    id = fields.IntField(pk=True)
    submission_id = fields.CharField(index=True, max_length=100)
    filename = fields.CharField(index=True, max_length=5000)
    n_deleted = fields.IntField()
    insert_timestamp = fields.DatetimeField(auto_now_add=True)
    update_timestamp = fields.DatetimeField(auto_now=True)
    entry = fields.JSONField()

    class Meta:
        table = "submissions"


class DBLog(Model):
    id = fields.IntField(pk=True)
    insert_timestamp = fields.DatetimeField(auto_now_add=True)
    log_level = fields.CharField(index=True, max_length=100, null=False)
    log_source = fields.CharField(index=True, max_length=100, null=False)
    log_position = fields.CharField(index=True, max_length=5000, null=False)
    log_sid = fields.CharField(index=True, max_length=100, null=True)
    user_agent_string = fields.CharField(max_length=5000, null=True)
    log_entry = fields.JSONField(null=True)

    class Meta:
        table = "osd2f_logs"


async def initialize_database(db_url: str):
    await Tortoise.init(db_url=db_url, modules={"models": ["osd2f.database"]})
    await Tortoise.generate_schemas(safe=True)


async def stop_database():
    await Tortoise.close_connections()


async def insert_log(
    log_source: str,
    log_level: str,
    log_position: str,
    log_sid: typing.Optional[str] = None,
    entry: typing.Dict = None,
    user_agent_string: typing.Optional[str] = None,
):

    await DBLog(
        log_source=log_source,
        log_level=log_level,
        log_position=log_position,
        log_sid=log_sid,
        log_entry=entry,
        user_agent_string=user_agent_string,
    ).save()

    return


async def insert_submission(submission: Submission):
    logger.debug(submission)
    for entry in submission.entries:
        await DBSubmission.create(
            submission_id=submission.submission_id,
            filename=submission.filename,
            entry=entry,
            n_deleted=submission.n_deleted,
        )


async def insert_submission_list(submissionlist: SubmissionList):
    if len(submissionlist.__root__) < 1:
        logger.info("Empty submissionlist")
        return

    logger.debug(
        f"Inserting {len(submissionlist.__root__)} files of data for submission "
        f"'{submissionlist.__root__[0].submission_id}'"
    )

    def subgenerator():
        for sub in submissionlist.__root__:
            for entry in sub.entries:
                yield DBSubmission(
                    submission_id=sub.submission_id,
                    filename=sub.filename,
                    entry=entry,
                    n_deleted=sub.n_deleted,
                )

    await DBSubmission.bulk_create(objects=subgenerator())


async def count_submissions():
    return await DBSubmission.all().count()


def add_database_logging() -> queue.SimpleQueue:
    """Forward logger statements to the database.

    Uses a QueueHandler and an asyncronous worker to
    insert logs from logger.debug/info/warning/critical
    to the application database.

    NOTE: messages over 5000 characters are shortened
    """

    async def async_log_worker(q: queue.SimpleQueue):
        while 1:
            try:
                m = q.get_nowait()
                if m.msg == "stop-logging":
                    break
                if len(m.msg) < 5000:
                    await insert_log("server", m.levelname, m.msg)
                else:
                    await insert_log("server", m.levelname, m.msg[:4997] + "...")
            except queue.Empty:
                await asyncio.sleep(0.1)

    logQueue: queue.SimpleQueue = queue.SimpleQueue()
    h = logging.handlers.QueueHandler(logQueue)
    h.setLevel(logger.level)
    print(h.level)
    logger.addHandler(h)
    asyncio.get_running_loop().create_task(async_log_worker(logQueue))

    return logQueue