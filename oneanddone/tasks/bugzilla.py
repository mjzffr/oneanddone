import requests

_baseurl = 'https://bugzilla.mozilla.org/rest/bug'

# 3063 =item C<limit>
# 3064
# 3065 C<int> Limit the number of results returned to C<int> records. If the limit
# 3066 is more than zero and higher than the maximum limit set by the administrator,
# 3067 then the maximum limit will be used instead. If you set the limit equal to zero,
# 3068 then all matching results will be returned instead.
# 3069
# 3070 =item C<offset>
# 3071
# 3072 C<int> Used in conjunction with the C<limit> argument, C<offset> defines
# 3073 the starting position for the search. For example, given a search that
# 3074 would return 100 bugs, setting C<limit> to 10 and C<offset> to 10 would return
# 3075 bugs 11 through 20 from the set of 100.

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

def request_bugs(query, fields=['id','summary']):
    """ Returns list of bugs from Bugzilla@Mozilla, if any """
    params = {'include_fields' : ','.join(fields)}
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










