from   datetime import datetime, timedelta
import os
import smtplib
import sys
from   time import time

try:
    thisdir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(thisdir, '..'))
except:
    sys.path.append('..')

from dibs.tind import TindRecord


MARC_XML = r'''<?xml version="1.0" encoding="UTF-8"?>
<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <controlfield tag="000">01059cam\a2200361Ia\4500</controlfield>
  <controlfield tag="001">735973</controlfield>
  <controlfield tag="005">20201028221548.0</controlfield>
  <controlfield tag="008">120118s2012\\\\nyua\\\\\b\\\\001\0\eng\d</controlfield>
  <datafield tag="010" ind1=" " ind2=" ">
    <subfield code="a">2011931725</subfield>
  </datafield>
  <datafield tag="015" ind1=" " ind2=" ">
    <subfield code="a">GBB1D1820</subfield>
    <subfield code="2">bnb</subfield>
  </datafield>
  <datafield tag="016" ind1="7" ind2=" ">
    <subfield code="a">015969759</subfield>
    <subfield code="2">Uk</subfield>
  </datafield>
  <datafield tag="019" ind1=" " ind2=" ">
    <subfield code="a">761380918</subfield>
  </datafield>
  <datafield tag="020" ind1=" " ind2=" ">
    <subfield code="a">1429215089</subfield>
  </datafield>
  <datafield tag="020" ind1=" " ind2=" ">
    <subfield code="a">1429224045 (hbk.)</subfield>
  </datafield>
  <datafield tag="020" ind1=" " ind2=" ">
    <subfield code="a">9781429215084</subfield>
  </datafield>
  <datafield tag="020" ind1=" " ind2=" ">
    <subfield code="a">9781429224048 (hbk.)</subfield>
  </datafield>
  <datafield tag="035" ind1=" " ind2=" ">
    <subfield code="a">(OCoLC)773193687</subfield>
    <subfield code="z">(OCoLC)761380918</subfield>
  </datafield>
  <datafield tag="040" ind1=" " ind2=" ">
    <subfield code="a">IPL</subfield>
    <subfield code="c">IPL</subfield>
    <subfield code="d">YDXCP</subfield>
    <subfield code="d">UKMGB</subfield>
    <subfield code="d">BWX</subfield>
    <subfield code="d">CIT</subfield>
  </datafield>
  <datafield tag="049" ind1=" " ind2=" ">
    <subfield code="a">CIT5</subfield>
  </datafield>
  <datafield tag="050" ind1=" " ind2="4">
    <subfield code="a">QA303</subfield>
    <subfield code="b">.M338 2012</subfield>
  </datafield>
  <datafield tag="100" ind1="1" ind2=" ">
    <subfield code="a">Marsden, Jerrold E</subfield>
  </datafield>
  <datafield tag="245" ind1="1" ind2="0">
    <subfield code="a">Vector calculus /</subfield>
    <subfield code="c">Jerrold E. Marsden, Anthony Tromba</subfield>
  </datafield>
  <datafield tag="250" ind1=" " ind2=" ">
    <subfield code="a">6th ed</subfield>
  </datafield>
  <datafield tag="260" ind1=" " ind2=" ">
    <subfield code="a">New York :</subfield>
    <subfield code="b">W.H. Freeman,</subfield>
    <subfield code="c">c2012</subfield>
  </datafield>
  <datafield tag="300" ind1=" " ind2=" ">
    <subfield code="a">xxv, 545 p. :</subfield>
    <subfield code="b">ill. (some col.) ;</subfield>
    <subfield code="c">26 cm</subfield>
  </datafield>
  <datafield tag="504" ind1=" " ind2=" ">
    <subfield code="a">Includes bibliographical references and index</subfield>
  </datafield>
  <datafield tag="650" ind1=" " ind2="0">
    <subfield code="a">Calculus</subfield>
  </datafield>
  <datafield tag="650" ind1=" " ind2="0">
    <subfield code="a">Vector analysis</subfield>
  </datafield>
  <datafield tag="690" ind1=" " ind2=" ">
    <subfield code="a">Caltech authors</subfield>
  </datafield>
  <datafield tag="700" ind1="1" ind2=" ">
    <subfield code="a">Tromba, Anthony</subfield>
  </datafield>
  <datafield tag="907" ind1=" " ind2=" ">
    <subfield code="a">.b14946786</subfield>
    <subfield code="b">150825</subfield>
    <subfield code="c">120214</subfield>
  </datafield>
  <datafield tag="909" ind1="C" ind2="O">
    <subfield code="o">oai:caltech.tind.io:735973</subfield>
    <subfield code="p">caltech:bibliographic</subfield>
  </datafield>
  <datafield tag="948" ind1=" " ind2=" ">
    <subfield code="a">PP</subfield>
  </datafield>
  <datafield tag="980" ind1=" " ind2=" ">
    <subfield code="a">BIB</subfield>
  </datafield>
  <datafield tag="998" ind1=" " ind2=" ">
    <subfield code="a">sfl</subfield>
    <subfield code="b">120313</subfield>
    <subfield code="c">a</subfield>
    <subfield code="d">m</subfield>
    <subfield code="e">-</subfield>
    <subfield code="f">eng</subfield>
    <subfield code="g">nyu</subfield>
    <subfield code="h">0</subfield>
    <subfield code="i">1</subfield>
  </datafield>
</record>
</collection>'''.encode()


def test_xml():
    r = TindRecord(marc_xml = MARC_XML)
    assert r.barcode == ''
    assert r.tind_id == '735973'
    assert r.title   == 'Vector calculus'
    assert r.author  == 'Jerrold E. Marsden, Anthony Tromba'
    assert r.year    == '2012'
    assert r.edition == '6th ed'
    assert r.call_no == 'QA303 .M338 2012'


def test_barcode1():
    r = TindRecord(barcode = 35047019626837)
    assert r.barcode == '35047019626837'
    assert r.tind_id == '990468'
    assert r.title   == 'Fundamentals of geophysics'
    assert r.author  == 'William Lowrie, Andreas Fichtner'
    assert r.year    == '2020'
    assert r.edition == 'Third edition'
    assert r.call_no == 'QC806.L67 2020'


def test_barcode2():
    r = TindRecord(barcode = 350470000611207)
    assert r.barcode == '350470000611207'
    assert r.tind_id == '466498'
    assert r.title   == 'Pack my bag: a self-portrait'
    assert r.author  == 'Henry Green'
    assert r.year    == '1940'
    assert r.edition == ''
    assert r.call_no == 'PR6013.R416 Z465'


def test_barcode3():
    r = TindRecord(barcode = 35047019626829)
    assert r.barcode == '35047019626829'
    assert r.tind_id == '990456'
    assert r.title   == 'GIS for science: applying mapping and spatial analytics'
    assert r.author  == 'Dawn J. Wright and Christian Harder, editors'
    assert r.year    == '2019'
    assert r.edition == ''
    assert r.call_no == 'Q175 .G5427'


def test_tind_id1():
    r = TindRecord(tind_id = 673541)
    assert r.barcode == ''
    assert r.tind_id == '673541'
    assert r.title   == 'Subtitles: on the foreignness of film'
    assert r.author  == 'Atom Egoyan and Ian Balfour'
    assert r.year    == '2004'
    assert r.edition == ''
    assert r.call_no == 'PN1995.4 .S83 2004'


def test_tind_id2():
    r = TindRecord(tind_id = 670639)
    assert r.barcode == ''
    assert r.tind_id == '670639'
    assert r.title   == 'French fest'
    assert r.author  == 'played by Mark Laubach'
    assert r.year    == '1997'
    assert r.edition == ''
    assert r.call_no == ''


def test_tind_id3():
    r = TindRecord(tind_id = 748838)
    assert r.barcode == ''
    assert r.tind_id == '748838'
    assert r.title   == 'Lasers and electro-optics'
    assert r.author  == 'Christopher C. Davis, University of Maryland'
    assert r.year    == '2014'
    assert r.edition == 'Second edition'
    assert r.call_no == 'TA1675 .D38 2014'


def test_tind_id4():
    r = TindRecord(tind_id = 676897)
    assert r.barcode == ''
    assert r.tind_id == '676897'
    assert r.title   == 'The diamond age'
    assert r.author  == 'Neal Stephenson'
    assert r.year    == '2003'
    assert r.edition == 'Bantam trade pbk. reissue'
    assert r.call_no == 'PS3569.T3868 D53 2003'
