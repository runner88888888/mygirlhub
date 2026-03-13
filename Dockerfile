# MyGirlHub – image with git so rebuild_site.py can run 'git pull' before building.
# Use this in your Portainer stack so "rebuild" automatically pulls latest code.
FROM python:3.11-alpine
RUN apk add --no-cache git
WORKDIR /app
# Dependencies for rebuild + publisher (paramiko for SFTP)
RUN pip install --no-cache-dir paramiko
# App code is mounted at /app; no COPY needed.
CMD ["python", "-u", "publisher.py"]
