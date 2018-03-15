import sys
import argparse
import app


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--dry_run", dest="dry_run",
                        action="store_true",
                        required=False,
                        help="")

    argv = parser.parse_args(sys.argv[1:])

    if not argv.dry_run:
        host = app.application.config.get('HOST', '0.0.0.0')
        port = app.application.config.get('PORT', 80)
        debug = app.application.config.get('DEBUG', False)
        app.application.run(host=host, debug=debug, port=port)
    else:
        issue = app.objects.get_git_object("issue")
        issue.score_pull_request("test for score pull request")
