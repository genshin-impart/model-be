.PHONY: run
run: clean
	python ./backend/app.py

.PHONY: init
init: clean
	flask --app backend/app initdb --drop
	flask --app backend/app forge

.PHONY: clean
clean:
	@rm -rf flask_session
	@rm -rf backend/cache
	@rm -rf backend/core/new_data/*
	@rm -rf result.csv