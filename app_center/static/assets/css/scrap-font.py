import requests, os
from bs4 import BeautifulSoup

BASEDIR = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))

lisdirvol = os.listdir(BASEDIR)

for vol in lisdirvol:
  if vol.split(".")[-1] in ['fonts']:
    CHPDIR = os.path.join(BASEDIR, vol)
    listdirchp = os.listdir(CHPDIR)
    total_file = len(listdirchp)
    link_list = []
    named_font = []
    for ft in listdirchp:
      path = os.path.join(CHPDIR, ft)
      with open(path, 'r') as out:
        css = out.read()
        first_split = css.split('https://')
        for fs in first_split:
          second_split = fs.split('.woff2')[0]
          if second_split.find('fonts.gstatic.com') != -1:
            link = f"https://{second_split}.woff2"
            if link not in link_list:
              link_list.append(link)
    ############## SCRAPING FONT ##########################
    for idx, ll in enumerate(link_list, start=1):
      response = requests.get(ll)
      font_path = os.path.join(CHPDIR, f"{vol}{idx}.woff2")
      print(f"tryna {idx} {ll} {response} ")
      if response.status_code == 200:
        content = response.content
        with open(font_path, 'wb+') as oufo:
          oufo.write(content)
      named_font.append(f"\"./fonts/{vol}{idx}.woff2\"")
    for ft2 in listdirchp:
      path2 = os.path.join(CHPDIR, ft)
      css2 = ''
      with open(path2, 'r') as out2:
        css2 = out2.read()
      for lk, nm in zip(link_list, named_font):
        css2 = css2.replace(lk, nm)
      with open(path2, 'w') as in2:
        in2.write(css2)