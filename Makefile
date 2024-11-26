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

