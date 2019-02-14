from pathlib import Path

# list all files that will be parsed
p = Path("./data/nfe-url/").rglob("*.txt")
list_of_resources = []
for _ in p:
    with open(_, 'r') as urlf:
        url = urlf.readlines()[0].replace("\n", "")
        list_of_resources.append(url)

with open("./data/url_list.csv", "w") as f:
    for _ in list_of_resources:
        f.write(f"{_}\n")
