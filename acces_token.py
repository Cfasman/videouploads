import json
import urllib
import urllib.request


def get_auth_code():
    """ Get access token for connect to youtube api """
    oauth_url = 'https://accounts.google.com/o/oauth2/token'
    # create post data
    data = dict(
        refresh_token="1//0cu_hdqFFQrV6CgYIARAAGAwSNwF-L9IrzqLudmkSllzh7j-IkxSEMo5J7Dtoc5Y1u7V_xLSxJE9KNNgfYdsp2WlKlcjVM3RxsA4",
        client_id="2475035465-oca17l9mqqkh6hh4nj56e0h27b3ms5gf.apps.googleusercontent.com",
        client_secret="DD6SwyaQg13V9qr3N6szkRyp",
        grant_type='refresh_token',
    )

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    data = urllib.parse.urlencode(data).encode('utf-8')
    # make request and take response
    request = urllib.request.Request(oauth_url, data=data, headers=headers)
    response = urllib.request.urlopen(request)

    # get access_token from response
    response = json.loads(response.read().decode('utf-8'))
    return response['access_token']