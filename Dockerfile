FROM python:3.9

# 
WORKDIR /fastapi-cource

# 
COPY ./requirements.txt /fastapi-cource/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /fastapi-cource/requirements.txt

# 
COPY ./app /fastapi-cource/app

# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]