PYTHON ?= python3
SIZE ?= 256
OUTPUT ?= examples/simple_cv_project/output

.PHONY: demo generate test clean

demo:
$(PYTHON) -m examples.simple_cv_project.server --size $(SIZE) --output $(OUTPUT)

generate:
$(PYTHON) -m examples.simple_cv_project.server --generate-only --size $(SIZE) --output $(OUTPUT)

test:
$(PYTHON) -m unittest discover -s tests -t .

clean:
rm -rf $(OUTPUT)
