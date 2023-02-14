import datetime


def set_filename(title):
    """
    Useful for setting unique filename when testing
    Arguments = Nothing
    Returns 2017-01-09 09:35:15
    """
    curr_datetime = datetime.datetime.now()
    filename = title + curr_datetime.strftime("-%Y-%m-%d") + '.jpg'  # %H-%M-%S
    return filename
