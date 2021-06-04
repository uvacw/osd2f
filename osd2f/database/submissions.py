from tortoise import fields
from tortoise.models import Model

from ..definitions import Submission, SubmissionList
from ..logger import logger


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
            entry=entry,
            n_deleted=submission.n_deleted,
        )


async def get_submissions():
    submissions = await DBSubmission.all()
    submission_dict = [
        {
            "db_id": si.id,
            "submission_id": si.submission_id,
            "filename": si.filename,
            "n_deleted_across_file": si.n_deleted,
            "insert_timestamp": si.insert_timestamp.isoformat(),
            "entry": si.entry,
        }
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
                    entry=entry,
                    n_deleted=sub.n_deleted,
                )

    await DBSubmission.bulk_create(objects=subgenerator())


async def count_submissions():
    return await DBSubmission.all().count()
