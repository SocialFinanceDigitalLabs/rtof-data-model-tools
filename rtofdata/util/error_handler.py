import logging


class ErrorEvent(dict):
    pass


class ListErrorHandler(list):

    def __init__(self):
        super().__init__()

    def __call__(self, event):
        self.append(event)

    def __repr__(self):
        return f"ListErrorHandler: {len(self)} events"

def print_error_handler(event):
    print(event)

def log_error_handler(event, logger=None, level=logging.INFO):
    if not logger:
        logger = logging.getLogger()
    logger.log(level=level, msg=str(event))