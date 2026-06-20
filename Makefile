.PHONY: setup run test clean lint

# Setup virtual environment and install dependencies
setup:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	@echo "Setup complete. Run 'source venv/bin/activate' to activate."

# Run the Telegram bot
run:
	. venv/bin/activate && python main.py

# Run tests
test:
	. venv/bin/activate && python -m pytest tests/ -v

# Clean generated files
clean:
	rm -rf __pycache__ */__pycache__
	rm -rf reports/*.md
	rm -rf logs/*.jsonl
	rm -rf memory/*.db

# Lint with ruff
lint:
	. venv/bin/activate && ruff check .

# Format code
format:
	. venv/bin/activate && ruff format .
