import datetime

TIMEZONE = datetime.timezone(datetime.timedelta(hours=3), name="МСК")


def get_current_dt() -> datetime.datetime:
    return datetime.datetime.now(tz=TIMEZONE)
