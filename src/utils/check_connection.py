import urllib.request


def connect():
    try:
        urllib.request.urlopen('http://google.com')
        return True
    except:
        print('Seems you are offline :(')
        return False
