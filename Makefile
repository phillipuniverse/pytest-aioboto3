.PHONY: test
test:
	poetry run pytest

.PHONY: rufflintfix
rufflintfix:
	poetry run ruff check . --fix --unsafe-fixes

.PHONY: rufflintcheck
rufflintcheck:
	@echo "Checking ruff..."
	poetry run ruff check .

.PHONY: rufflintwatch
rufflintwatch:
	poetry run ruff check . --fix --watch

.PHONY: ruffformatfix
ruffformatfix:
	poetry run ruff format . --preview

.PHONY: ruffformatcheck
ruffformatcheck:
	poetry run ruff format . --check --preview

.PHONY: poetrycheck
poetrycheck:
	poetry check --lock

.PHONY: pyformatcheck
pyformatcheck: poetrycheck rufflintcheck ruffformatcheck

.PHONY: lint
lint: pyformatcheck 

.PHONY: autofmt
autofmt: rufflintfix ruffformatfix 

.PHONY: patchrelease
patchrelease:
	poetry version patch
	git add pyproject.toml
	git commit -m "Release version $$(poetry version --short)"
	git tag $$(poetry version --short)

.PHONY: minorrelease
minorrelease:
	poetry version minor
	git add pyproject.toml
	git commit -m "Release version $$(poetry version --short)"
	git tag $$(poetry version --short)

.PHONY: preminor
preminor:
	poetry version preminor
	git add pyproject.toml
	git commit -m "Release version $$(poetry version --short)"
	git tag $$(poetry version --short)

.PHONY: prepatch
prepatch:
	poetry version prepatch
	git add pyproject.toml
	git commit -m "Release version $$(poetry version --short)"
	git tag $$(poetry version --short)

.PHONY: prerelease
prerelease:
	poetry version prerelease
	git add pyproject.toml
	git commit -m "Release version $$(poetry version --short)"
	git tag $$(poetry version --short)

