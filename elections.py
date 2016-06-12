#!/usr/bin/python
# vim: set ts=4:
# vim: set shiftwidth=4:
# vim: set expandtab:

#-------------------------------------------------------------------------------
#---> Elections supported
#-------------------------------------------------------------------------------
# election id - base_url - election type - year - has special polling stations tuples for each election
elections = [
        ('20150920', 'http://ekloges.ypes.gr/current', 'v', 2015, True),
        ('20150125', 'http://ekloges-prev.singularlogic.eu/v2015a', 'v', 2015, True),
        ('20150705', 'http://ekloges-prev.singularlogic.eu/r2015', 'e', 2015, True),
        ('20140525', 'http://ekloges-prev.singularlogic.eu/may2014', 'e', 2014, False),
        ('20120617', 'http://ekloges-prev.singularlogic.eu/v2012b', 'v', 2012, True),
        ('20120506', 'http://ekloges-prev.singularlogic.eu/v2012a', 'v', 2012, True)]

# chosen election
_ELECTION = 5

election_str = elections[_ELECTION][0]
base_url = elections[_ELECTION][1]
election_type = elections[_ELECTION][2]
year = elections[_ELECTION][3]
has_special = elections[_ELECTION][4]

#-------------------------------------------------------------------------------
#---> Json files urls
#-------------------------------------------------------------------------------

def get_url(lvl, idx, dynamic):
    content_type = 'dyn' if dynamic else 'stat'
    if year > 2012:
        first_part = '{0}/{1}/{2}'.format(base_url, content_type, election_type)
    else:
        first_part = '{0}/{1}'.format(base_url, content_type)

    if lvl == 'epik' or lvl == 'top':
        return '{0}/{1}'.format(first_part, 'statics.js')
    elif lvl == 'ep' or lvl == 'district':
        return '{0}/ep_{1}.js'.format(first_part, idx)
    elif lvl == 'den' or lvl == 'munical_unit':
        return '{0}/den_{1}.js'.format(first_part, idx)
    elif lvl == 'special':
        return '{0}/special_{1}.js'.format(first_part, idx)
    elif lvl == 'tm' or lvl == 'pstation':
        if year > 2012:
            return '{0}/{1}/tm_{2}.js'.format(first_part, int(idx / 10000), idx)
        else:
            return '{0}/tm_{1}.js'.format(first_part, idx)
    else:
        raise Exception


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

def has_special_list():
    if election_str == '20120506':
        return False
    return True
