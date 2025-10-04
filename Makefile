.PHONY: run format lint

run:
	python3 main.py

format:
	python3 -m pip install --quiet black
	black main.py

lint:
	python3 -m pip install --quiet ruff
	ruff check main.py