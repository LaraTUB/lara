import json
import log as logging
from conversation import speech as Speech

LOG = logging.getLogger(__name__)


def repository_missing_event(**kwargs):
    followup_event = dict(
        followupEvent={
            "name": "repository_missing_event",
            "data": kwargs
        },
        speech=Speech.repository_missing()
    )
    return followup_event


def issue_comment_not_finished_event(**kwargs):
    followup_event = dict(
        followupEvent={
            "name": "issue_comment_not_finished_event",
            "data": kwargs
        }
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
