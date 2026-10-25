# Executar manualmente
pip install requirements.txt
ou
pip install flask

python app.py

# Executar no Docker
docker build -t meu-app .
docker run -p 5000:5000 meu-app

# Comandos
docker ps
docker rm id_container
docker images
docker rmi meu-app

