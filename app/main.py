import sys
import argparse
import app

from app.db.api import user_get_by__github_login


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--dry_run", dest="dry_run",
                        action="store_true",
                        required=False,
                        help="""If `dry_run` is set, this script communicates
                        with *gihtub* backend directly. Mostly, it's for debuging
                        or developing new features without dialogflow's intervention.
                        Otherwise, this script starts a web services in foreground.""")

    parser.add_argument("-u", "--github_username", dest="github_username",
                        required=False,
                        help="""If `dry_run` is set, this optional argument must be
                        applied. User's github account.""")
    parser.add_argument("-p", "--github_password", dest="github_password",
                        required=False,
                        help="""If `dry_run` is set, this optional argument must be
                        applied. User's github account password.""")

    argv = parser.parse_args(sys.argv[1:])

    if not argv.dry_run:
        host = app.application.config.get('HOST', '0.0.0.0')
        port = app.application.config.get('PORT', 80)
        debug = app.application.config.get('DEBUG', False)
        app.application.run(host=host, debug=debug, port=port)
    elif argv.github_username and argv.github_password:
        app.application.config["GITHUB_USERNAME"] = argv.github_username
        app.application.config["GITHUB_PASSWORD"] = argv.github_password
        
        user = user_get_by__github_login('testuserlara')
        print(app.conversation.ask_for_todos.ask_for_todos(user))
