.PHONY: help

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z][a-zA-Z0-9_-]*:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

pep8:  ## Run PEP 8 compliance check
	@echo "Running PEP 8 compliance check..."
	@python3 scripts/check_pep8.py

pep8-fix:  ## Run PEP 8 compliance check and show suggestions for fixes
	@echo "Running PEP 8 compliance check with detailed output..."
	@flake8 . --show-source --statistics

pep8-auto-fix:  ## Automatically fix common PEP 8 issues using autopep8
	@echo "Automatically fixing PEP 8 issues..."
	@autopep8 --in-place --recursive --aggressive --aggressive .

black:  ## Format code using Black (opinionated formatter)
	@echo "Formatting code with Black..."
	@black .

isort:  ## Sort imports using isort
	@echo "Sorting imports..."
	@isort .

format:  ## Run all formatting tools (Black + isort)
	@echo "Running complete code formatting..."
	@$(MAKE) black
	@$(MAKE) isort

pep8-report:  ## Generate a detailed PEP 8 compliance report
	@echo "Generating PEP 8 compliance report..."
	@echo "=== PEP 8 COMPLIANCE REPORT ===" > pep8_report.txt
	@echo "Generated on: $$(date)" >> pep8_report.txt
	@echo "" >> pep8_report.txt
	@echo "=== SUMMARY ===" >> pep8_report.txt
	@flake8 . --statistics >> pep8_report.txt 2>&1 || true
	@echo "" >> pep8_report.txt
	@echo "=== DETAILED VIOLATIONS ===" >> pep8_report.txt
	@flake8 . --show-source >> pep8_report.txt 2>&1 || true
	@echo "" >> pep8_report.txt
	@echo "=== FILES WITH VIOLATIONS ===" >> pep8_report.txt
	@flake8 . --format=%(path)s >> pep8_report.txt 2>&1 | sort | uniq >> pep8_report.txt 2>&1 || true
	@echo "Report saved to: pep8_report.txt"
	@echo "Total violations: $$(flake8 . --count 2>/dev/null || echo 0)"

clean:  ## Clean up Python cache files
	@echo "Cleaning up Python cache files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true 