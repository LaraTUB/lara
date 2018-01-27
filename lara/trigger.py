import json

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
