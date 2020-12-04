import datetime

DATE_TIME_FULL_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_TIME_SHORT_FORMAT = '%d-%m-%Y'
RESPONSE_CODE = 'response_code'
MSG = 'msg'
DATA = 'data'

def get_current_time():
    now = datetime.datetime.now()
    formatted_date = now.strftime(DATE_TIME_FULL_FORMAT)
    return formatted_date

def get_time_by_format(input_time):
    date_time_obj = datetime.datetime.strptime(input_time, DATE_TIME_SHORT_FORMAT)
    formatted_date = date_time_obj.strftime(DATE_TIME_FULL_FORMAT)
    return formatted_date

def get_common_response():
    response = {RESPONSE_CODE: 200, MSG: "OK"}
    return response