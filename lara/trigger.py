import json
import log as logging

LOG = logging.getLogger(__name__)


def repository_missing_event(**kwargs):
    followup_event = dict(
        followupEvent={
            "name": "repository_missing_event",
            "data": kwargs
        }
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



def issue_comment_body_not_finished_event(**kwargs):
    followup_event = dict(
        speech="You have an unfinished comments.",
        displayText="You have an unfinished comments.",
    )
    LOG.debug("Issue comment body not finished event is triggered.")

    return followup_event
