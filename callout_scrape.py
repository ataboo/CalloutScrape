#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from DataObjects import JobHeader
from DataObjects import JobData
import urllib.request
from MysqlWriter import MysqlWriter

r = urllib.request.urlopen('https://members.boilermakers.ca/wsiscript/jobref.dll/workeropenjobs')
soup = BeautifulSoup(r, "html.parser")

table = soup.find('table', attrs={'class': 'jobreftable'})

rows = table.find_all('tr', attrs={'class': 'info_row'})
callHeaders = {}
callBodies = []
for row in rows:
    cols = row.find_all('td')
    stripped = [ele.text.strip() for ele in cols]

    if row.has_attr('class') and 'doZebra' in row['class']:
        rowRaw = [ele for ele in stripped if ele]
        headerRow = JobHeader(rowRaw)
        callHeaders[headerRow.id] = headerRow
    else:
        callBodies.append(JobData(cols))

for call in callBodies:
    if call.id and callHeaders[call.id]:
        call.attribute_dictionary.update(callHeaders[call.id].attributes)

mysql = MysqlWriter(callBodies)

