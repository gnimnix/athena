import datetime

import xlsxwriter

from telegram import Update
from telegram.ext import CallbackContext

from athena.config import DATE_FORMAT
from athena.db import get_db


def report_handler(update: Update, context: CallbackContext) -> None:
    """Generates the report and sends to user

    Args:
        update (Update):
        context (CallbackContext):
    """
    
    query = update.callback_query
    query.answer()
    
    filename = "report.xlsx"
    wb = xlsxwriter.Workbook(filename)
    ws = wb.add_worksheet()
    
    row = 0
    col = 0
    data = {}
    
    with get_db() as db:
        data = dict(db['records'])
    
    min_date = datetime.datetime.now().date()
    max_date = datetime.date(1970, 1, 1)
    
    for user_records in data.values():
        for record in user_records:
            for d in record:
                tmp_date = datetime.datetime.strptime(d, "%d%m%y").date()
                min_date = min(min_date, tmp_date)
                max_date = max(max_date, tmp_date)
    
    i = min_date
    while i <= max_date:
        ws.write(row, col+1, i.strftime("%d %b "))
        i += datetime.timedelta(1)
        col += 1
        
    with get_db() as db:
        users = db['users']
    
    col = 0
    for iid, user_records in data.items():
        row += 1
        ws.write(row, col, users[iid]['name'] if iid in users else "Name not Found")
        for record in user_records:
            d = list(record.keys())[0]
            tmp_date = datetime.datetime.strptime(d, "%d%m%y").date()
            delta = tmp_date - min_date
            days = delta.days
            ws.write(row, days+1, 'Y')
        
    
    wb.close()
    
    query.message.reply_document(open(filename, 'rb'))
