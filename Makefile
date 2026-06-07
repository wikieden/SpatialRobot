# SpatialRobot workspace — thin wrappers over `uv run`.
# Run from the workspace root. `make help` lists targets.

.DEFAULT_GOAL := help
.PHONY: help sync sync-clip test test-core test-brain test-perception \
        lint fmt types bump clean

CORE        := SpatialMem
BRAIN       := spatialmem-brain
PERCEPTION  := spatialmem-perception

help: ## List targets
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*## "}{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

sync: ## Create/refresh the shared .venv (all 3 members editable + dev tools)
	uv sync

sync-clip: ## uv sync + the GPU/CLIP extra (torch, open-clip, pillow)
	uv sync --extra clip

test: ## Run pytest across all 3 members
	uv run pytest $(CORE)/tests $(BRAIN)/tests $(PERCEPTION)/tests

test-core: ## Run only the memory-core tests
	uv run pytest $(CORE)/tests

test-brain: ## Run only the brain tests
	uv run pytest $(BRAIN)/tests

test-perception: ## Run only the perception tests
	uv run pytest $(PERCEPTION)/tests

lint: ## ruff check the whole workspace
	uv run ruff check .

fmt: ## ruff format the whole workspace
	uv run ruff format .

types: ## pyright on all 3 src trees
	uv run pyright $(CORE)/src/spatialmem
	uv run pyright $(BRAIN)/src/spatialmem_brain
	uv run pyright $(PERCEPTION)/src/spatialmem_perception

bump: ## Pull each submodule's tracked branch to latest (then commit the pointer)
	git submodule update --remote
	git submodule status

clean: ## Remove caches (keeps .venv)
	find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.pytest_cache' -prune -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.ruff_cache' -prune -exec rm -rf {} + 2>/dev/null || true
