from trackstospotify import treat_url


with open('urls', 'r') as urls_file:
    for url in urls_file.readlines():
        treat_url(url.rstrip())