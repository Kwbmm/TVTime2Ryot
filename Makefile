.PHONY: set_env install

set_env:
	python3 -m venv .venv

install: set_env
# Using . instead of source because https://stackoverflow.com/a/53936226
	. .venv/bin/activate && pip3 install -r requirements.txt
