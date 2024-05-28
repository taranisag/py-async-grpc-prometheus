#!/usr/bin/env python
from setuptools import find_packages
from setuptools import setup

with open("README.md", "r") as fh:
  long_description = fh.read()

setup(name="py_async_grpc_prometheus",
      version="0.1.1",
      description="Python async gRPC Prometheus Interceptors",
      long_description=long_description,
      long_description_content_type="text/markdown",
      author="Taranis",
      author_email="avi.klaiman@taranis.com",
      install_requires=[
          "setuptools>=39.0.1",
          "grpcio>=1.10.0",
          "prometheus_client>=0.3.0"
      ],
      url="https://github.com/taranisag/py-async-grpc-prometheus",
      packages=find_packages(exclude=["tests.*", "tests"]),
     )
