.PHONY: reader-prepare reader-check

# One local pass over the existing Reader generators and validation contracts.
# These targets do not create a Reader, qualify source evidence, or authorize release.
reader-prepare:
	python3 scripts/generate_site.py
	python3 scripts/knowledge_contract.py
	$(MAKE) reader-check

reader-check:
	python3 scripts/generate_site.py --check
	python3 scripts/knowledge_contract.py --check
	python3 scripts/check_site.py --local
	python3 -m unittest discover -s tests -p 'test_*.py'
	git diff --check
