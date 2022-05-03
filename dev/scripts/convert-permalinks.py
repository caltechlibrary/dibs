#!/usr/bin/env python3
# Created 2022-05-03 to rewrite the EDS page URLs after EDS changed the
# permalinks in late April.
#
# This is meant to be run on the dibs-item.json file.

import json
import sys

if len(sys.argv[1:]) != 1:
    sys.exit('Need 1 argument: original_file')

input_file = sys.argv[1]
output_file = input_file + '.converted'

# Note that the AN part here includes the AN prefix. This is so that the loop
# below can simply append the unique ID to this base_url string, to create the
# final page url.
base_url = ('https://search.ebscohost.com/login.aspx?direct=true'
            '&AuthType=ip,guest&db=cat09073a&site=eds-live&scope=site'
            '&custid=s8984125&groupid=main&profile=eds'
            '&AN=cit.oai.folio.org.fs00001057.')

with open(sys.argv[1], 'r') as f:
    # Each item in the list will be a dict.
    record_list = json.load(f)
    print(f'Converting {len(record_list)} records')
    for record in record_list:
        item_id = record['item_id']
        an_tail = item_id.replace('-', '.')
        record['item_page'] = base_url + an_tail

with open(output_file, 'w') as f:
    f.write(json.dumps(record_list))

print('Output written to ' + output_file)
