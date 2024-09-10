# Makefile for automating project setup

# Default target: setup the project
setup:
	
	pip install -r requirements.txt
	# Use a tab here
	python3 scripts/setup.py

# Clean target (if you want to add clean tasks)
clean:
	
	rm -rf __pycache__

# Run the application
run:
	
	streamlit run main.py