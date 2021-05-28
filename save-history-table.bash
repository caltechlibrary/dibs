#!/bin/bash
DATE_LOG=$(date +%Y-%m-%d)
echo 'History ID, Type, What, Start Time, End Time' >"history-${DATE_LOG}.csv"
sqlite3 dibs.db 'SELECT historyid, type, what, start_time, end_time FROM history;' | tr '|' ',' >>"history-${DATE_LOG}.csv"
