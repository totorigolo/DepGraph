
.DEFAULT_GOAL := all
all: show-rules
	@echo "Please use sub-rules to build HolBA."

show-rules:
	@echo "Available rules:\n\
     - init: install requirements via pip.\n\
     - show-rules: this help"

init:
	pip install -r requirements.txt


.PHONY: all show-rules init