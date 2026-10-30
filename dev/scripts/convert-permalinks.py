#!/usr/bin/env python3
# Rewrite the EDS page URLs (the item_page field) of items exported from DIBS,
# for use when EDS accession numbers or permalinks change.
#
# This is meant to be run on the JSON file of items written by
# admin/export-data.  The accession prefix and page template have the same
# form as FOLIO_ACCESSION_PREFIX and EDS_PAGE_TEMPLATE in settings.ini; the
# template must contain {accession_number}.  Example:
#
#   convert-permalinks.py dibs-item.json \
#       --prefix cit.oai.folio.org.fs00001057 \
#       --template 'https://search.ebscohost.com/login.aspx?direct=true&AuthType=ip,guest&db=cat09073a&site=eds-live&scope=site&custid=s8984125&groupid=main&profile=eds&AN={accession_number}'
#
# The output is written to the input file name with ".converted" appended.

import argparse
import json
import sys

parser = argparse.ArgumentParser(description = 'Rewrite EDS links of DIBS items.')
parser.add_argument('input_file', help = 'JSON file of items from export-data')
parser.add_argument('--prefix', required = True,
                    help = 'accession number prefix (FOLIO_ACCESSION_PREFIX)')
parser.add_argument('--template', required = True,
                    help = 'EDS page URL template (EDS_PAGE_TEMPLATE)')
args = parser.parse_args()

if '{accession_number}' not in args.template:
    sys.exit('The template must contain {accession_number}.')

prefix = args.prefix if args.prefix.endswith('.') else args.prefix + '.'
output_file = args.input_file + '.converted'

with open(args.input_file, 'r') as f:
    # Each item in the list will be a dict.
    record_list = json.load(f)
    print(f'Converting {len(record_list)} records')
    for record in record_list:
        # This matches how pokapi makes accession numbers from instance ids.
        accession_number = prefix + record['item_id'].replace('-', '.')
        record['item_page'] = args.template.format(accession_number = accession_number)

with open(output_file, 'w') as f:
    f.write(json.dumps(record_list))

print('Output written to ' + output_file)
