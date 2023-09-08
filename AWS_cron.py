from datetime import datetime
from pprint import pprint

from croniter import croniter
import json
from datetime import datetime


def days_to_numbs(day_range, exp_start):
    # Define a dictionary to map day abbreviations to numeric values
    days = ['SAT', 'SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI']

    # Split the input day range by the hyphen
    start_day, end_day = day_range.split('-')
    cron_expressions = []
    start = days.index(start_day, 0, 6)
    end = days.index(end_day, 0, 6)
    if end < start:
        end = days.index(end_day, 7, 13)
    for i in range(start, end+1):
        dow = days[i]
        cron_expressions.append(exp_start + ' ' + dow)
    return cron_expressions


def aws_cron_to_cron_format(aws_cron_expression):
    parts = aws_cron_expression.split()
    if len(parts[4]) > 3:
        cron_start = " ".join(parts[:4])
        cron_expressions = days_to_numbs(parts[4], cron_start.replace("?", "*"))
        return cron_expressions
    else:
        cron_expressions = []
        cron_expression = " ".join(parts[:5])
        cron_expressions.append(cron_expression.replace("?", "*"))
    return cron_expressions

def parse_aws_cron(aws_cron_expression, specific_date, specific_date1=None):
    cron_expressions = aws_cron_to_cron_format(aws_cron_expression)
    next_n_dates = []
    for cron_expression in cron_expressions:
        cron_schedule = croniter(cron_expression, specific_date, specific_date1)
        if specific_date1 is not None:
            for _ in range(10):
                next_occurrence = cron_schedule.get_next(datetime)
                if next_occurrence < specific_date1:
                    next_n_dates.append(next_occurrence)
                else:
                    break
        else:
            for _ in range(10):
                next_occurrence = cron_schedule.get_next(datetime)
                next_n_dates.append(next_occurrence)
    if len(next_n_dates) > 10:
        next_n_dates = sorted(next_n_dates)[:10]


    return next_n_dates



def lambda_handler(body):
    response = {"status": "", "result": {}}
    aws_cron_expressions = body["cronExpressions"]

    if "startDate" in body:
        specific_date = body["startDate"]
        specific_date1 = body["endDate"]

        datetime.strptime(specific_date, "%Y-%m-%dT%H:%M:%S.%f")
        datetime.strptime(specific_date1, "%Y-%m-%dT%H:%M:%S.%f")

        for aws_cron_expression in aws_cron_expressions:
            try:
                formatted_date = datetime.strptime(specific_date, "%Y-%m-%dT%H:%M:%S.%f")
                formatted_date1 = datetime.strptime(specific_date1, "%Y-%m-%dT%H:%M:%S.%f")
                dates_list = parse_aws_cron(aws_cron_expression, formatted_date, formatted_date1)
                formatted_dates_list = [dates.strftime("%Y-%m-%dT%H:%M:%S") for dates in dates_list]
                response["result"][aws_cron_expression] = formatted_dates_list
                response["status"] = "Success"
            except:
                print("Error")
                pass
        return response

    else:
        if "startDate" not in body and "onDate" not in body:
            today = datetime.now()
            specific_date = today.strftime("%Y-%m-%dT%H:%M:%S.%f")
        elif body["onDate"] == "":
            today = datetime.now()
            specific_date = today.strftime("%Y-%m-%dT%H:%M:%S.%f")
        else:
            specific_date = body["onDate"]
        for aws_cron_expression in aws_cron_expressions:
            try:
                date_string = specific_date
                formatted_date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f")
                dates_list = parse_aws_cron(aws_cron_expression, formatted_date)
                formatted_dates_list = [dates.strftime("%Y-%m-%dT%H:%M:%S") for dates in dates_list]
                response["result"][aws_cron_expression] = formatted_dates_list
                response["status"] = "Success"
            except:
                print("Error")
                pass
        return response

pprint(lambda_handler({
  "cronExpressions": [
    "25 5 ? * SAT-THU *"
  ]
}))
