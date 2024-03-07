import os
import yaml
import json
import decimal
import datetime
import logging

import boto3


import gsheet_writer


logging.basicConfig(level=logging.DEBUG)

with open("config_files/settings.yaml") as settings_f:
    settings = yaml.load(settings_f, Loader=yaml.Loader)


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Deals")

gwriter = gsheet_writer.GSheetWriter(
    os.path.expanduser(settings["GSHEET_SERVICE_FILE"]), settings["GSHEET_LOG_FILE"]
)

wks = gsheet_writer._get_worksheet_by_name(gwriter.sh, settings["GSHEET_TAB_NAME_LOGS"])
all_records = wks.get_all_records()
collected_records = []
for raw_record in all_records[1:]:
    if not raw_record["Trade ID"]:
        logging.info("Found an empty row")
        continue
    if not raw_record["Created At"]:
        raw_record["Created At"] = datetime.datetime(
            year=2020, month=1, day=1
        ).timestamp()

    record = json.loads(json.dumps(raw_record), parse_float=decimal.Decimal)
    collected_records.append(record)
import pdb

pdb.set_trace()
with table.batch_writer() as batch:
    for record in collected_records:
        batch.put_item(Item=record)
