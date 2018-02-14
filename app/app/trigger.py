from app import log as logging
from app.conversation import speech

LOG = logging.getLogger(__name__)


def repository_missing_event(**kwargs):
    followup_event = dict(
        followupEvent={
            "name": "repository_missing_event",
            "data": kwargs
        },
        speech=speech.repository_missing()
    )
    return followup_event


def issue_comment_not_finished_event(**kwargs):
    followup_event = dict(
        followupEvent={
            "name": "issue_comment_not_finished_event",
            "data": kwargs
        },
        contextOut=[{"name": "issue_comment", "lifespan": 1}]
    )

    return followup_event


def issue_comment_timeout_event(**kwargs):
    followup_event = dict(
        followupEvent={
            "name": "repository_missing_event",
            "data": kwargs
        }
    )
    LOG.debug("Issue comment body not finished event is triggered.")

    return followup_event
