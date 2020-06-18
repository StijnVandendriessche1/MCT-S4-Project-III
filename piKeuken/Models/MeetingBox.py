import logging


class MeetingBox:
    def __init__(self, name, buzzy = False, count_peoples = 0):
        try:
            self.name = name
            self.buzzy = buzzy
            self.count_peoples = count_peoples
            self.last_change = 0
        except Exception as e:
            logging.error(e)
            raise e
