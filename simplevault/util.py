def urlretrieve(url, fpath, headers=None):
    # adopted from http://stackoverflow.com/a/2028750/890242
    import urllib2
    request = urllib2.Request(url)
    if headers:
        request.add_header(*headers) 
    urlfile = urllib2.urlopen(request)
    chunk = 4096
    f = open(fpath, "w")
    while True:
        data = urlfile.read(chunk)
        if not data:
            break
        f.write(data)
    urlfile.close()
