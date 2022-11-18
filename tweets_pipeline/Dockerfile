FROM python
WORKDIR /code
ADD requirements.txt /code/ 
RUN pip install -U "pip>=19.3.1" && \
    pip install -r requirements.txt
ADD . /code/
