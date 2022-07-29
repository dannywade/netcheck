.PHONY: test rm_db

rm_db:
	rm database.db
	echo "Test database deleted..."

test: rm_db
	PYTHONPATH=./netcheck pytest --cov
