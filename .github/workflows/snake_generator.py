import requests

# Aqui você chamaria a API do repositório Platane/snk ou geraria a imagem localmente.
# Exemplo bem básico (não funcional) apenas para ilustrar:

url = "https://raw.githubusercontent.com/Platane/snk/output/github-contribution-grid-snake.svg"
r = requests.get(url)

with open("snake.svg", "wb") as f:
    f.write(r.content)
