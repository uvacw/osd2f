import asyncio
import logging
import queue
import time
import typing

from tortoise import fields
from tortoise.models import Model

from ..logger import logger

clientLogQueue: queue.SimpleQueue = queue.SimpleQueue()


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


def start_logworker():
    async def logworker():
        stop = False
        while 1:
            try:
                log = clientLogQueue.get_nowait()
                if log != "STOP":
                    try:
                        if log is not None:
                            await background_insert_log(**log)
                    except Exception as e:
                        print("ERROR INSERTING LOG", e)
                else:
                    stop = True
                    logger.info("Stopping server logging worker")

            except queue.Empty:
                if not stop:
                    await asyncio.sleep(0.1)
                    continue
                else:
                    return

    asyncio.get_running_loop().create_task(logworker())


def stop_logworker():
    clientLogQueue.put("STOP", block=True)
    time.sleep(0.2)


async def background_insert_log(
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


async def insert_log(
    log_source: str,
    log_level: str,
    log_position: str,
    log_sid: typing.Optional[str] = None,
    entry: typing.Dict = None,
    user_agent_string: typing.Optional[str] = None,
):
    clientLogQueue.put(
        dict(
            log_source=log_source,
            log_level=log_level,
            log_position=log_position,
            log_sid=log_sid,
            entry=entry,
            user_agent_string=user_agent_string,
        )
    )


async def get_activity_logs():
    logs = await DBLog.all()
    data = [
        {
            "db_id": log.id,
            "insert_timestamp": log.insert_timestamp.isoformat(),
            "log_level": log.log_level,
            "source": log.log_source,
            "position": log.log_position,
            "submission_id": log.log_sid,
            "user-agent-string": log.user_agent_string,
            "entry": log.log_entry,
        }
        for log in logs
    ]
    return data


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
                if m == "stop-logging":
                    break
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
