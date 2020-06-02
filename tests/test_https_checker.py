def test_bad_ssl():
    from networking.https_checker import WebpageTest
    wt = WebpageTest()
    url = 'https://expired.badssl.com/'
    print('Checking ->', url)
    assert wt.check_robots(url=url) == False
    assert wt.check_https(url=url) == False
    assert wt.check_https_redirection(url=url) == False
    assert wt.check_hsts(url=url) == False

def test_good_https():
    from networking.https_checker import WebpageTest
    wt = WebpageTest()
    url = 'https://python.org/'
    print('Checking ->', url)
    assert wt.check_robots(url=url)
    assert wt.check_https(url=url)
    assert wt.check_https_redirection(url=url)
    assert wt.check_hsts(url=url)