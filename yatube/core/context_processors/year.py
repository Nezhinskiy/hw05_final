import datetime


def year(request):
    now = datetime.datetime.now()
    return {
        'year': now.year
    }
