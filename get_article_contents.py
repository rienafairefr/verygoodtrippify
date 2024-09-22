from os import makedirs,path

from content.content import get_article, get_episode_title

makedirs('data', exist_ok=True)

with open('urls', 'r') as urls_file:
    for url in urls_file.readlines():
        url = url.rstrip()
        data = get_article(url)
        episode_title = get_episode_title(url)
        with open(path.join('data',episode_title+'.txt'),'w') as f:
            f.write(str(data))
            pass
