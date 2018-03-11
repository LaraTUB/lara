import app

if __name__ == "__main__":
    host = app.application.config.get('HOST', '0.0.0.0')
    port = app.application.config.get('PORT', 80)
    debug = app.application.config.get('DEBUG', False)
    app.application.run(host=host, debug=debug, port=port)
