.PHONY: test test-verbose clean

test:
	python3 -m pytest lib/test_*.py

test-verbose:
	python3 -m pytest lib/test_*.py -v

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
