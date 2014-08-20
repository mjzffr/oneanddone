# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import requests

_baseurl = 'https://bugzilla.mozilla.org/rest/bug'

def _request_json(url, params):
    """ Returns the json-encoded response from Bugzilla@Mozilla, if any """
    headers = {'content-type':'application/json', 'accept':'application/json'}
    try:
        r = requests.get(url, headers=headers, params=params)
        data = r.json()
        if not r.ok or data.get('error'):
            data = {}
            # TODO mzf log the error somewhere?
        return data
    except requests.exceptions.RequestException:
        # TODO mzf log the exception somewhere?
        return {}

def request_bugs(query, fields=['id','summary'], offset=0, limit=99):
    """ Returns list of at most first `limit` bugs (starting at `offset`) from
        Bugzilla@Mozilla, if any. The bugs are ordered by bug id.
    """
    params = {'include_fields' : ','.join(fields), 'offset':offset, 'limit':limit}
    url = ''.join([_baseurl, '?', query])
    return _request_json(url, params).get('bugs') or []

def request_bugcount(query):
    response = _request_json(''.join([_baseurl, '?', query]), {'count_only':1})
    bug_count = response.get('bug_count')
    return int(bug_count) if bug_count else bug_count

def request_bug(bug_id, fields=['id','summary']):
    """ Returns bug with id `bug_id` from Buzgilla@Mozilla, if any """
    params = {'include_fields' : ','.join(fields)}
    url = ''.join([_baseurl, '/', str(bug_id)])
    bugs = _request_json(url, params).get('bugs')
    if bugs:
        return bugs[0]
    else:
        return None










