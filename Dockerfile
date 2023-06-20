# Use a imagem base do Python
FROM tiangolo/uwsgi-nginx-flask:python3.11


# Defina o diretório de trabalho dentro do contêiner
WORKDIR /

# Copie os arquivos do projeto para o diretório de trabalho do contêiner
COPY ./dados /dados/
COPY ./app.py /app.py


COPY requirements.txt /tmp/

# Instale as dependências do projeto
RUN pip install -U pip && pip install -r /tmp/requirements.txt

EXPOSE 5000

ENV NGINX_WORKER_PROCESSES auto

# Defina o comando para executar a aplicação
CMD ["uwsgi", "--ini", "wsgi.ini"]