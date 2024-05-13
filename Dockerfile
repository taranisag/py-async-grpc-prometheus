FROM python:3.12-slim

ARG BUILD_LOCAL

COPY requirements.txt test_requirements.txt setup.py README.md ./

RUN pip install -r requirements.txt
RUN if [ "$BUILD_LOCAL" = "true" ]; \
    then pip install -r test_requirements.txt; \    
    fi
RUN mkdir -p /app

WORKDIR /app

COPY . /app