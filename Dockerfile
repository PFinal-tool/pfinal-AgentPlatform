FROM python:3.7
WORKDIR /pfinalAgent
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

CMD ["gunicorn", "start:app", "-c", "./gunicorn.conf.py"]