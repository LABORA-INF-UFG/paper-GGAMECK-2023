FROM python:3.9

COPY . /home

WORKDIR /home

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /home

ENTRYPOINT ["python3", "./heuristic_model.py" ]

