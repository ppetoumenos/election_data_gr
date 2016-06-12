#!/usr/bin/python
# vim: set ts=4:
# vim: set shiftwidth=4:
# vim: set expandtab:

import logging
import datetime
import unicodecsv as csv
import codecs
from crawler import Crawler
import elections as el

_SECONDS_PER_REQUEST = 3

#-------------------------------------------------------------------------------
#---> Logging init
#-------------------------------------------------------------------------------
fname = 'run_{:%Y%m%d_%H%M%S}.log'.format(datetime.datetime.now())
handler = logging.FileHandler(fname, 'w', 'utf-8')
handler.setFormatter(logging.Formatter('%(message)s')) # or whatever

logger = logging.getLogger()
logger.setLevel(logging.DEBUG) 
logger.addHandler(handler)
#logging.basicConfig(filename=fname, level=logging.DEBUG)

parties = dict()
#-------------------------------------------------------------------------------
#---> Helper Functions
#-------------------------------------------------------------------------------

def new_entry(nam, upper_id):
    """ Return a new dictionary for storing election results """
    d = dict([
        ('name', nam),
        ('pstation_cnt', 0),
        ('upper_id', upper_id),
        ('lower_cnt', 0),
        ('registered', 0),
        ('valid', 0),
        ('invalid', 0),
        ('blank', 0),
        ('results', dict())])
    for idx in parties:
        d['results'][idx] = 0
    return d

def to_dict(raw_lst, lvl):
    """ Extract the name, id, and hierarchical information from an entry of
    the top-level json file and build an election results entry """
    idx = int(el.get(raw_lst, lvl, 'id'))
    nam = el.get(raw_lst, lvl, 'name')
    upper_id = int(el.get(raw_lst, lvl, 'upper_id'))
    return idx, new_entry(nam, upper_id)

def parse_base(data, lvl):
    """ Parse the list of entries in the top-level json file for a specific
    hierarchical level and return a dictionary of election result entries """
    d = dict()
    for raw_lst in data[lvl]:
        idx, datum = to_dict(raw_lst, lvl)
        d[idx] = datum
    return d

def check(idx, d, res, field):
    """ Check the correctness of a json object returned by the crawler """
    if res is None:
        logger.warning(u'Did not get data for {0}, {1}'.format(idx, d['name']))
        return False
    if res[field] != idx:
        logger.warning(u'Wrong id for {0}, {1}. Got {2}'.format(idx, d['name'], res[field]))
        return False

    return True

def translate_result(result):
    """ Transform the raw election result returned by the crawler to our format """
    d = new_entry('', -1)

    for key, translation in el.translations.items():
        if key in result:
            d[translation] = result[key]

    if d['pstation_cnt'] == 0:
        d['pstation_cnt'] = 1

    for res in result['party']:
        idx = res['PARTY_ID']
        votes = res['VOTES']
        d['results'][idx] = votes

    return d

def add(d, result):
    """ Add the result fields to the ones of d """
    for key in ['pstation_cnt', 'registered', 'valid', 'invalid', 'blank']:
        d[key] += result[key]

    for idx in d['results']:
        d['results'][idx] += result['results'][idx]

def write_to_csv(csv_f, idx, data_lst):
    """ write the data to a csv file.
    csv_f is is the CSVWriter, idx is the id of the result to write,
    data_lst is a list containing the dictionaries for this and higher level """
    original_idx = idx
    templst = []
    for data in data_lst:
        templst.extend([idx, data[idx]['name']])
        if 'upper_id' not in data[idx]:
            break
        idx = data[idx]['upper_id']

    res = data_lst[0][original_idx]

    templst.extend([res['pstation_cnt'], res['lower_cnt'], res['registered']])
    templst.extend([res['valid'], res['invalid'], res['blank']])
    for party_id in parties:
        templst.append(res['results'][party_id])

    csv_f.writerow(templst)


#-------------------------------------------------------------------------------
#---> Extract high level information
#-------------------------------------------------------------------------------

crawler = Crawler(el.election_str, _SECONDS_PER_REQUEST)

# Get the file containing all the ids and names
pdata = crawler.get(el.top_level_url)

# Top level file contains information for the following levels:
# 'epik' -> nationwide, top administrative level
# 'snom' -> regions, second administrative level - NUTS 2
# 'ep' -> voting district, roughly similar to the pre-2011 prefectures - NUTS 3
# 'dhm' -> municipalities, third administrative level - LAU 1
# 'den' -> municipal units, roughly similar to the pre-2011 municipalities - LAU 2

# parse id and name for all parties
for party_raw in el.get_parties_list(pdata):
    party_id = int(el.get_party_field(party_raw, 'id'))
    name = el.get_party_field(party_raw, 'name')
    parties[party_id] = {'name':name}
logger.info(u'Parties info parsed successfully')

# Extract the nationwide data
nationwide_raw = pdata['epik'][0]
_, nationwide = to_dict(nationwide_raw, 'epik')
logger.info(u'Nationwide info parsed successfully')

# parse the other levels
districts = parse_base(pdata, 'ep')
logger.info(u'District info parsed successfully')

municipalities = parse_base(pdata, 'dhm')
logger.info(u'Municipalities info parsed successfully')

municipal_units = parse_base(pdata, 'den')
logger.info(u'Municipal units info parsed successfully')

#-------------------------------------------------------------------------------
#---> Crawl through all the municipal units data
#-------------------------------------------------------------------------------

for mu_id, mu_dict in municipal_units.items():
    url = el.munit_url(mu_id)
    results = crawler.get(url)
    if not check(mu_id, mu_dict, results, 'DEN_ID'):
        continue
    add(mu_dict, translate_result(results))
    mu_dict['lower_cnt'] = mu_dict['pstation_cnt']
    logger.info(u'Parsed unit {0}, {1}'.format(mu_id, mu_dict['name']))

#-------------------------------------------------------------------------------
#---> Add special polling stations and get their results
#-------------------------------------------------------------------------------
#2012a no special list
# for each district get static
# http://ekloges-prev.singularlogic.eu/v2012a/stat/ep_31.js
# extract CountTmK -> ordinary pstations
# extract CountTmGe0 -> all pstations located in the district
# get all tm [(CountTmK - CountTmM+1, CountTmGeo] static
# read their EP_ID, count them for this district, make sure DHM_ID is zero

# special polling stations don't belong to any municipality or unit
# add one extra "municipality" and "unit" in each district to aggregate the
# special polling station results
if el.has_special():
    # add empty entries first
    specials = dict()
    max_municipality = max([m_id for m_id in municipalities.keys()])
    max_munit = max([mu_id for mu_id in municipal_units.keys()])
    for district_id in districts:
        max_municipality += 1
        max_munit += 1
        name = 'special_' + str(district_id)

        m_dict = new_entry(name, district_id)
        municipalities[max_municipality] = m_dict
        mu_dict = new_entry(name, max_municipality)
        municipal_units[max_munit] = mu_dict
        specials[district_id] = mu_dict

    # find and aggregate special polling stations
    for district_id in districts:
        if el.has_special_list():
            mu_dict = specials[district_id]
            url = el.special_list_url(district_id)
            special_lst = crawler.get(url)
            for special in special_lst:
                url = el.pstation_url(special['TM_ID'])
                results = crawler.get(url)
                add(mu_dict, translate_result(results))
                mu_dict['lower_cnt'] += 1
        else:
            url = el.district_url(district_id)
            district_data = crawler.get(url)
            start_id = district_data['CountTmK'] - district_data['CountTmM'] + 1
            end_id = district_data['CountTmGeo'] + 1
            for pstation_id in range(start_id, end_id):
                real_pstation_id = 10000 * district_id + pstation_id
                url = el.pstation_static_url(real_pstation_id)
                results = crawler.get(url)
                if results['DHM_ID'] != 0:
                    continue
                real_district_id = results['EP_ID']
                mu_dict = specials[real_district_id]

                url = el.pstation_url(real_pstation_id)
                results = crawler.get(url)
                add(mu_dict, translate_result(results))
                mu_dict['lower_cnt'] += 1

        logger.info(u'Parsed special polling stations for district {0}, {1}'.format(district_id, districts[district_id]['name']))

#-------------------------------------------------------------------------------
#---> Aggregate the municipality, district, and nationwide data
#-------------------------------------------------------------------------------
for mu_id, mu_dict in municipal_units.items():
    m_dict = municipalities[mu_dict['upper_id']]
    add(m_dict, mu_dict)
    m_dict['lower_cnt'] += 1

for m_id, m_dict in municipalities.items():
    d_dict = districts[m_dict['upper_id']]
    add(d_dict, m_dict)
    d_dict['lower_cnt'] += 1

for d_id, d_dict in districts.items():
    add(nationwide, d_dict)
    nationwide['lower_cnt'] += 1

logger.info(u'Aggregated data for municipalities and districts')

#-------------------------------------------------------------------------------
#---> Export CSV
#-------------------------------------------------------------------------------
party_header = []
for party_id in parties:
    party_header.append(parties[party_id]['name'])

fname = el.election_str + '_municipal_units.csv'
header = ['id', 'municipality unit', 'municipality id', 'municipality',
        'district id', 'district', 'number of polling stations',
        'number of polling stations', 'registered voters', 'valid votes',
        'invalid votes', 'blank votes']
header.extend(party_header)

with open(fname, 'wb') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter='\t', encoding='utf-8')
    csvwriter.writerow(header)
    for mu_id in municipal_units:
        write_to_csv(csvwriter, mu_id, [municipal_units, municipalities, districts])

fname = el.election_str + '_municipalities.csv'
header = ['id', 'municipality', 'district id', 'district',
        'number of polling stations', 'number of municipal units',
        'registered voters', 'valid votes', 'invalid votes', 'blank votes']
header.extend(party_header)

with open(fname, 'wb') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter='\t', encoding='utf-8')
    csvwriter.writerow(header)
    for m_id in municipalities:
        write_to_csv(csvwriter, m_id, [municipalities, districts])

fname = el.election_str + '_districts.csv'
header = ['id', 'district', 'number of polling stations',
        'number of municipalities', 'registered voters', 'valid votes',
        'invalid votes', 'blank votes']
header.extend(party_header)

with open(fname, 'wb') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter='\t', encoding='utf-8')
    csvwriter.writerow(header)
    for d_id in districts:
        write_to_csv(csvwriter, d_id, [districts])


