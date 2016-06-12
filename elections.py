#!/usr/bin/python
# vim: set ts=4:
# vim: set shiftwidth=4:
# vim: set expandtab:

#-------------------------------------------------------------------------------
#---> Elections supported
#-------------------------------------------------------------------------------
# election id - base_url - election type - year tuples for each election
elections = [
        ('20150920', 'http://ekloges.ypes.gr/current', 'v', 2015),
        ('20150125', 'http://ekloges-prev.singularlogic.eu/v2015a', 'v', 2015),
        ('20150705', 'http://ekloges-prev.singularlogic.eu/r2015', 'e', 2015),
        ('20140525', 'http://ekloges-prev.singularlogic.eu/may2014', 'e', 2014),
        ('20120617', 'http://ekloges-prev.singularlogic.eu/v2012b', 'v', 2012),
        ('20120506', 'http://ekloges-prev.singularlogic.eu/v2012a', 'v', 2012)]

# chosen election
_ELECTION = 3

election_str = elections[_ELECTION][0]
base_url = elections[_ELECTION][1]
election_type = elections[_ELECTION][2]
year = elections[_ELECTION][3]

#-------------------------------------------------------------------------------
#---> Json files urls
#-------------------------------------------------------------------------------

if year > 2012:
    static_url = '{0}/stat/{1}'.format(base_url, election_type)
    dyn_url = '{0}/dyn/{1}'.format(base_url, election_type)

    # e.g. 'http://ekloges.ypes.gr/current/stat/v/statics.js'
    top_level_url = '{0}/{1}'.format(static_url, 'statics.js')
    # e.g. 'http://ekloges.ypes.gr/current/stat/ep_xx.js'
    district_url = lambda x: '{0}/ep_{1}.js'.format(static_url, x)
    # e.g 'http://ekloges.ypes.gr/current/dyn/v/den_xxxx.js'
    munit_url = lambda x: '{0}/den_{1}.js'.format(dyn_url, x)
    # e.g 'http://ekloges.ypes.gr/current/stat/v/special_xxxx.js'
    special_list_url = lambda x: '{0}/special_{1}.js'.format(static_url, x)
    # e.g 'http://ekloges.ypes.gr/current/dyn/v/x/tm_xyyyy.js'
    pstation_url = lambda x: '{0}/{1}/tm_{2}.js'.format(dyn_url, int(x / 10000), x)
    pstation_static_url = lambda x: '{0}/{1}/tm_{2}.js'.format(static_url, int(x / 10000), x)
else:
    static_url = '{0}/stat'.format(base_url)
    dyn_url = '{0}/dyn'.format(base_url)

    # e.g. 'http://ekloges.ypes.gr/current/stat/v/statics.js'
    top_level_url = '{0}/{1}'.format(static_url, 'statics.js')
    # e.g. 'http://ekloges.ypes.gr/current/stat/ep_xx.js'
    district_url = lambda x: '{0}/ep_{1}.js'.format(static_url, x)
    # e.g 'http://ekloges.ypes.gr/current/dyn/v/den_xxxx.js'
    munit_url = lambda x: '{0}/den_{1}.js'.format(dyn_url, x)
    # e.g 'http://ekloges.ypes.gr/current/stat/v/special_xxxx.js'
    special_list_url = lambda x: '{0}/special_{1}.js'.format(static_url, x)
    # e.g 'http://ekloges.ypes.gr/current/dyn/v/x/tm_xyyyy.js'
    pstation_url = lambda x: '{0}/tm_{1}.js'.format(dyn_url, x)
    pstation_static_url = lambda x: '{0}/tm_{1}.js'.format(static_url, x)


#-------------------------------------------------------------------------------
#---> Top level file structure
#-------------------------------------------------------------------------------

if election_type == 'v' and year >= 2015:
    lvl_labels = ['epik', 'snom', 'ep', 'dhm', 'den']
    lvl_structs = [['id', 'name', 'pstation_cnt', 'population'],
                   ['id', 'name', 'pstation_cnt'],
                   ['id', 'name', 'pstation_cnt', 'alt_id', 'mps', 'unknown'],
                   ['id', 'name', 'pstation_cnt', 'upper_id'],
                   ['id', 'name', 'pstation_cnt', 'upper_id']]
    parties_label = 'party'
    parties_struct = ['id', 'alt_id', 'name', 'colour', 'in_parliament']

elif election_type == 'v' and year >= 2012:
    lvl_labels = ['epik', 'ep', 'dhm', 'den']
    lvl_structs = [['id', 'name', 'pstation_cnt', 'population'],
                   ['id', 'name', 'pstation_cnt', 'alt_id', 'mps'],
                   ['id', 'name', 'pstation_cnt', 'upper_id'],
                   ['id', 'name', 'pstation_cnt', 'upper_id']]
    parties_label = 'party'
    parties_struct = ['id', 'alt_id', 'name', 'colour']

elif election_type == 'e':
    lvl_labels = ['epik', 'snom', 'ep', 'dhm', 'den']
    lvl_structs = [['id', 'name', 'pstation_cnt', 'population', 'mps', 'unknown'],
                   ['id', 'upper_id', 'name', 'pstation_cnt'],
                   ['id', 'name', 'pstation_cnt', 'alt_id', 'upper_id'],
                   ['id', 'name', 'pstation_cnt', 'upper_id'],
                   ['id', 'name', 'pstation_cnt', 'upper_id']]
    parties_label = 'party'
    parties_struct = ['id', 'alt_id', 'name', 'colour', 'in_parliament']


#-------------------------------------------------------------------------------
#---> Translations
#-------------------------------------------------------------------------------

translations = dict([
    ('NumTm', 'pstation_cnt'),
    ('Gramenoi', 'registered'),
    ('Egkyra', 'valid'),
    ('Akyra', 'invalid'),
    ('Leyka', 'blank')])

#-------------------------------------------------------------------------------
#---> Top level access helpers
#-------------------------------------------------------------------------------

def get(data_lst, lvl, field):
    structure = lvl_structs[lvl_labels.index(lvl)]
    try:
        idx = structure.index(field)
    except:
        if field == 'upper_id':
            return -1
        else:
            raise ValueError
    return data_lst[idx]

def get_parties_list(data):
    return data[parties_label]

def get_party_field(data_lst, field):
    idx = parties_struct.index(field)
    return data_lst[idx]

def has_special():
    if election_type == 'e':
        return False
    return True

def has_special_list():
    if election_str == '20120506':
        return False
    return True
