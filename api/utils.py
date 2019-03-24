from datetime import datetime


class Utils:
    def __init__(self):
        return

    @staticmethod
    def convert_dt(dt=datetime.now()):
        return dt.strftime("%Y%m%d")
