.PHONY: initialize-development

# Initialize the project development environment.
initialize-development:
	@pip install --upgrade -r requirements.txt
	@pip install -U -r test_requirements.txt
	@pre-commit install

.PHONY: test
test:
	@coverage run --source=py_async_grpc_prometheus -m pytest
	@coverage report -m

# Run pre-commit for all
pre-commit:
	@pre-commit run --all-files

run-test:
	@python -m unittest discover

# Fix the import path. Use pipe for sed to avoid the difference between Mac and GNU sed
compile-protos:
	@docker run --entrypoint protoc --rm -v $(PWD):$(PWD) -w $(PWD) namely/protoc-all \
      --plugin=protoc-gen-grpc=/usr/local/bin/grpc_python_plugin \
      --python_out=./  \
	  --mypy_out=./ \
      --grpc_out=./  \
	  --mypy_grpc_out=./ \
      -I ./ \
      tests/integration/protos/*.proto
	@docker run --entrypoint protoc --rm -v $(PWD):$(PWD) -w $(PWD) namely/protoc-all \
      --plugin=protoc-gen-grpc=/usr/local/bin/grpc_python_plugin \
      --python_out=./  \
	  --mypy_out=./ \
      --grpc_out=./  \
	  --mypy_grpc_out=./ \
      -I ./ \
      tests/integration/hello_world/*.proto

run-test-server:
	python -m tests.integration.hello_world.hello_world_server

run-test-client:
	python -m tests.integration.hello_world.hello_world_client

publish:
	# Markdown checker
	# pip install cmarkgfm
	rm -rf *.egg-info build dist
	python setup.py sdist bdist_wheel
	twine check dist/*
	twine upload dist/*
