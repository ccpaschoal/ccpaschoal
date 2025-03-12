import requests

# URL do arquivo SVG da cobrinha (exemplo do repositório Platane/snk)
url = "https://raw.githubusercontent.com/Platane/snk/output/github-contribution-grid-snake.svg"
r = requests.get(url)

if r.status_code == 200:
    with open("snake.svg", "wb") as f:
        f.write(r.content)
else:
    print("Erro ao baixar o arquivo:", r.status_code)
