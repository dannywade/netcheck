.PHONY: test rm_db

rm_db: test
	rm database.db
	echo "Test database deleted..."

test:
	PYTHONPATH=./netcheck pytest
