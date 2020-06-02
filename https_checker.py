#!/usr/bin/python3
import requests
import re
from urllib.parse import urlparse, urlunparse


# decorator methods
def force_HTTPS(func):
    '''get url and make sure it is using HTTPS'''
    def decorator(*args, **kwargs):
        url = kwargs['url']
        uri = urlparse(url)
        if 'https' != uri.scheme:
            uri = uri._replace(scheme='https')
        url = urlunparse(uri)
        kwargs['url'] = url
        f = func(*args, **kwargs)
        return f
    return decorator


def force_HTTP(func):
    '''get url and make sure it is using HTTP'''
    def decorator(*args, **kwargs):
        url = kwargs['url']
        uri = urlparse(url)
        if 'http' != uri.scheme:
            uri = uri._replace(scheme='http')
        url = urlunparse(uri)
        kwargs['url'] = url
        f = func(*args, **kwargs)
        return f
    return decorator


class WebpageTest:
    '''Webpage Test Class'''
    DEFAULT_HEADERS = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0'
    }
    TIMEOUT = 5

    def __init__(self):
        '''Initialize session'''
        print('<open session>\n')
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)


    def __del__(self):
        '''Delete session'''
        print('\n<exit session>')
        self.session.close()


    def check_robots(self, url=None) -> bool:
        '''Check if robots.txt is available'''
        uri = urlparse(url)

        # check if robots.txt is in url and build correct url
        if '/robots.txt' != uri.path:
            uri = uri._replace(path='/robots.txt')

        url = urlunparse(uri)
        status = None
        try:
            reply = self.session.get(url, timeout=self.TIMEOUT)
            score = 'PASS' if reply.status_code == 200 else 'FAIL'

        except requests.exceptions.ConnectionError:
            status = 'ConnectTimeoutError!'
            score = 'FAIL'


        print(f'[{score}] Check robots.txt', status if status else '')
        return True if score == 'PASS' else False

    @force_HTTPS
    def check_https(self, url=None) -> bool:
        '''Check if HTTPS is available'''
        status = None
        try:
            reply = self.session.get(url, verify=True, timeout=self.TIMEOUT)
            score = 'PASS' if reply.status_code == 200 else 'FAIL'

        except requests.exceptions.SSLError:
            status = 'SSLError!'
            score = 'FAIL'

        except requests.exceptions.ConnectionError:
            status = 'ConnectTimeoutError!'
            score = 'FAIL'

        print(f'[{score}] Check HTTPS', status if status else '')
        return True if score == 'PASS' else False

    @force_HTTP
    def check_https_redirection(self, url=None) -> bool:
        '''Check HTTP redirection to HTTPS'''
        # check for url argument
        url = self.url if url is None else url

        # check for https in url and build correct url
        if url.startswith('https'):
           url = url.replace('https://', 'http://')

        status = None
        try:
            reply = self.session.get(url, timeout=self.TIMEOUT)

            last_redirect = reply.history[-1]

            if urlparse(reply.url).scheme == 'https' and reply.status_code == 200 \
            and last_redirect.status_code == 301 and urlparse(last_redirect.url).scheme == 'https':
                score = 'PASS'            
            else:
                score = 'FAIL'

        except requests.exceptions.ConnectionError:
            status = 'ConnectTimeoutError!'
            score = 'FAIL'
        print(f'[{score}] Check HTTPS Redirection', status if status else '')
        return True if score == 'PASS' else False

    @force_HTTP
    def check_hsts(self, url=None) -> bool:
        '''Check HTTP Strict Transport Security (HSTS)'''
        '''HSTS is a method for web applications to ensure they only use TLS to support secure transport. It protects users against passive eavesdropper and active man-in-the-middle (MITM) attacks. It also enforces strict security like preventing mixed content and click-through certificate overrides, and it protects against web server mistakes like loading JavaScript over an insecure connection. HSTS serves as a secure umbrella against all of these attacks.'''
        status = None
        try:
            reply = self.session.get(url, timeout=self.TIMEOUT)
            last_redirect = reply.history[-1]

            if reply.url.startswith('https') and reply.status_code == 200 \
            and last_redirect.status_code == 301 and last_redirect.url.startswith('https'):
                score = 'PASS'            
            else:
                score = 'FAIL'

            # HSTS References
            # https://www.checkbot.io/guide/security/hsts/
            # https://blog.qualys.com/securitylabs/2016/03/28/the-importance-of-a-proper-http-strict-transport-security-implementation-on-your-web-server
            if 'strict-transport-security' in reply.headers:
                print(f'[PASS] HSTS header present')
                # check if HSTS includes subdomains
                if 'includeSubDomains' in reply.headers['strict-transport-security']:
                    print(f'[PASS] HSTS includes subdomains')
                else:
                    print(f'[FAIL] HSTS does NOT include subdomains')
                    score = 'FAIL'
                # check for max-age
                if 'max-age' in reply.headers['strict-transport-security']:
                    print(f'[PASS] HSTS includes max-age')
                    max_age = int(re.search(r'max-age=(\d+)', reply.headers['strict-transport-security']).group(1))
                    # should be greater than 120 days, or 1 year (31536000) ideally
                    if max_age > 10368000:
                        print(f'[PASS] HSTS max-age={max_age} meets minimum value')
                    else:
                        print(f'[FAIL] HSTS max-age={max_age} below minimum value')
                        score = 'FAIL'
                else:
                    print(f'[FAIL] HSTS does NOT include max-age')
                    score = 'FAIL'
            else:
                print(f'[FAIL] No HSTS header')
                score = 'FAIL'

        except requests.exceptions.ConnectionError:
            score = 'FAIL'
            status = 'ConnectTimeoutError!'

        print(f"[{score}] Check HSTS implementation", status if status else '')
        return True if score == 'PASS' else False
