import logging

from dashboard import dash_app, server



if __name__ == "__main__":
    logger = logging.getLogger('my-logger')
    logger.propagate = False
    dash_app.run_server(debug=True)