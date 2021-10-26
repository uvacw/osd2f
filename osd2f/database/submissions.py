from tortoise import Tortoise, fields
from tortoise.models import Model

from ..definitions import OutputSubmission, Submission, SubmissionList
from ..logger import logger
from ..security.entry_encryption.secure_entry_singleton import SecureEntry


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


async def insert_submission(submission: Submission):
    logger.debug(submission)
    for entry in submission.entries:
        await DBSubmission.create(
            submission_id=submission.submission_id,
            filename=submission.filename,
            entry=SecureEntry.write_entry_field(entry),
            n_deleted=submission.n_deleted,
        )


async def get_submissions():
    submissions = await DBSubmission.all()
    submission_dict = [
        OutputSubmission(
            db_id=si.id,
            submission_id=si.submission_id,
            filename=si.filename,
            n_deleted_across_file=si.n_deleted,
            insert_timestamp=si.insert_timestamp.isoformat(),
            entry=SecureEntry.read_entry_field(dict(si.entry)),
        ).dict()
        for si in submissions
    ]
    return submission_dict


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
                    entry=SecureEntry.write_entry_field(entry),
                    n_deleted=sub.n_deleted,
                )

    await DBSubmission.bulk_create(objects=subgenerator())


async def count_submissions():
    return await DBSubmission.all().count()


async def get_pending_participants():
    conn = Tortoise.get_connection("default")
    rs = await conn.execute_query(
        """
    WITH completed AS (
        SELECT DISTINCT log_sid FROM osd2f_logs
        WHERE
            log_SID IS NOT NULL
            AND log_position="Received the donation!"
        GROUP BY log_sid
    )
    SELECT
        osd2f_logs.log_sid AS submission_id,
        MIN(insert_timestamp) AS first_seen,
        MAX(insert_timestamp) AS last_seen
    FROM osd2f_logs
    OUTER LEFT JOIN completed ON osd2f_logs.log_sid=completed.log_sid
    WHERE submission_id IS NOT NULL
    GROUP BY submission_id
    ORDER BY last_seen DESC
    """
    )
    data = [
        {
            "submission_id": r["submission_id"],
            "first_seen": r["first_seen"],
            "last_seen": r["last_seen"],
        }
        for r in rs[1]
    ]
    return data
