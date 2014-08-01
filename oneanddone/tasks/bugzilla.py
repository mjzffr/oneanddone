import requests

_baseurl = 'https://bugzilla.mozilla.org/rest/bug'

def _request_json(url, params):
    """ Returns the json-encoded response from Bugzilla@Mozilla, if any """
    headers = {'content-type':'application/json', 'accept':'application/json'}
    try:
        r = requests.get(url, headers=headers, params=params)
        data = r.json()
        if r.status_code != 200 or data.get('error'):
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

def request_bug(bug_id, fields=['id','summary']):
    """ Returns bug with id `bug_id` from Buzgilla@Mozilla, if any """
    params = {'include_fields' : ','.join(fields)}
    url = ''.join([_baseurl, '/', str(bug_id)])
    bugs = _request_json(url, params).get('bugs')
    if bugs:
        return bugs[0]
    else:
        return None










