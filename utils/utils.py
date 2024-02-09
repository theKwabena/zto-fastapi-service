import requests


def check_mailbox_size(url, auth):
    # Send a HEAD request to retrieve metadata, including content length
    response = requests.head(url, auth=auth, allow_redirects=False)
    if response.status_code == 200:
        # Check if the 'Content-Length' header is present in the response
        if 'Content-Length' in response.headers:
            return int(response.headers['Content-Length'])
    return None
