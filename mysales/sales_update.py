import time

from dateutil.relativedelta import relativedelta
from datetime import datetime
from .api_update import save_sales_to_database


def day_update_sales(api_key, user_id):
    start_time = time.time()
    end_date = datetime.now().date()
    start_date = end_date - relativedelta(days=2)
    response_status_code = save_sales_to_database(api_key, user_id, start_date)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"script update_sales take {execution_time} sec.")
    return response_status_code


def month_update_sales(api_key, user_id):
    start_time = time.time()
    end_date = datetime.now().date()
    start_date = end_date - relativedelta(days=30)
    response_status_code = save_sales_to_database(api_key, user_id, start_date)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"script update_sales take {execution_time} sec.")
    return response_status_code


def full_update_sales(api_key, user_id):
    start_time = time.time()
    end_date = datetime.now().date()
    start_date = end_date - relativedelta(months=5)
    response_status_code = save_sales_to_database(api_key, user_id, start_date)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"script update_sales take {execution_time} sec.")
    print(response_status_code)
    return response_status_code
