.PHONY: run
run: clean
	python ./backend/app.py

.PHONY: clean
clean:
	@rm -rf flask_session
	@rm -rf backend/cache
	@rm -rf backend/core/new_data/*