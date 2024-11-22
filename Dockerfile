FROM ubuntu
WORKDIR /app
RUN apt update -y && apt install -y python3 python3-dev python3-pip
COPY requirements/prod.txt .
RUN pip3 install  --break-system-packages -r prod.txt --no-cache
COPY . .
EXPOSE 8000
CMD uvicorn src.main:app --host 0.0.0.0 --port 8000
