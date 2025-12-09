.PHONY: help install setup clean run dev console test lint format livekit-start livekit-stop livekit-status livekit-logs livekit-restart

.DEFAULT_GOAL := help

# Colors
BLUE := \033[36m
GREEN := \033[32m
RED := \033[31m
YELLOW := \033[33m
RESET := \033[0m

help: ## Show this help message
	@echo "$(BLUE)LiveKit Voice Agent - Management Commands$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""

install: ## Install all dependencies
	@echo "$(BLUE)Installing dependencies...$(RESET)"
	@python3 -m venv venv
	@. venv/bin/activate && pip install --upgrade pip
	@. venv/bin/activate && pip install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(RESET)"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Activate venv: source venv/bin/activate"
	@echo "  2. Setup voice: make setup-voice"
	@echo "  3. Run agent: make dev"

install-neutts: ## Install NeuTTS Air from source
	@echo "$(BLUE)Installing NeuTTS Air...$(RESET)"
	@if [ ! -d "/tmp/neutts-air" ]; then \
		git clone https://github.com/neuphonic/neutts-air.git /tmp/neutts-air; \
	fi
	@cd /tmp/neutts-air && . $(CURDIR)/venv/bin/activate && \
		pip install --upgrade pip && \
		pip install -r requirements.txt
	@if [ -f "/tmp/neutts-air/pyproject.toml" ]; then \
		cd /tmp/neutts-air && . $(CURDIR)/venv/bin/activate && pip install .; \
	elif [ -f "/tmp/neutts-air/setup.py" ]; then \
		cd /tmp/neutts-air && . $(CURDIR)/venv/bin/activate && pip install -e .; \
	else \
		echo "$(YELLOW)No setup files found, installing via requirements.txt only$(RESET)"; \
		echo "export PYTHONPATH=\"/tmp/neutts-air:\$$PYTHONPATH\"" >> $(CURDIR)/venv/bin/activate; \
	fi
	@echo "$(GREEN)✓ NeuTTS Air installed$(RESET)"

setup: ## Initialize project (create directories)
	@echo "$(BLUE)Initializing project structure...$(RESET)"
	@mkdir -p voice_clones logs backups examples
	@touch voice_clones/.gitkeep
	@echo "$(GREEN)✓ Project initialized$(RESET)"

setup-voice: ## Setup voice cloning (interactive)
	@echo "$(BLUE)Voice Clone Setup$(RESET)"
	@echo ""
	@read -p "Path to reference audio (.wav): " audio_path; \
	read -p "Path to reference text (.txt): " text_path; \
	python setup_voice_clone.py "$$audio_path" "$$text_path"

clean: ## Clean up generated files
	@echo "$(BLUE)Cleaning up...$(RESET)"
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@rm -rf logs/*.log
	@echo "$(GREEN)✓ Cleaned up$(RESET)"

clean-all: clean ## Clean everything including venv and models
	@echo "$(YELLOW)Warning: This will remove venv and cached models!$(RESET)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf venv; \
		rm -rf ~/.cache/huggingface; \
		echo "$(GREEN)✓ Full cleanup complete$(RESET)"; \
	else \
		echo "Cancelled"; \
	fi

run: ## Run agent in production mode
	@echo "$(BLUE)Starting agent (production mode)...$(RESET)"
	@. venv/bin/activate && python agent.py start

dev: ## Run agent in development mode
	@echo "$(BLUE)Starting agent (development mode)...$(RESET)"
	@. venv/bin/activate && python agent.py dev

console: ## Run agent in console mode (terminal only)
	@echo "$(BLUE)Starting agent (console mode)...$(RESET)"
	@. venv/bin/activate && python agent.py console

test: ## Run tests
	@echo "$(BLUE)Running tests...$(RESET)"
	@. venv/bin/activate && pytest tests/ -v

test-components: ## Test individual components
	@echo "$(BLUE)Testing STT...$(RESET)"
	@. venv/bin/activate && python -c "from stt import WhisperMLXSTT; print('✓ STT OK')"
	@echo "$(BLUE)Testing LLM...$(RESET)"
	@. venv/bin/activate && python -c "from llm import MLXLLM; print('✓ LLM OK')"
	@echo "$(BLUE)Testing TTS...$(RESET)"
	@. venv/bin/activate && python -c "from tts import NeuTTSAirTTS; print('✓ TTS OK')"
	@echo "$(GREEN)✓ All components OK$(RESET)"

test-connection: ## Test LiveKit server connection
	@echo "$(BLUE)Testing LiveKit connection...$(RESET)"
	@. venv/bin/activate && python test_livekit_connection.py

lint: ## Run linter
	@echo "$(BLUE)Running linter...$(RESET)"
	@. venv/bin/activate && ruff check .

format: ## Format code
	@echo "$(BLUE)Formatting code...$(RESET)"
	@. venv/bin/activate && black .
	@echo "$(GREEN)✓ Code formatted$(RESET)"

check-env: ## Check environment variables
	@echo "$(BLUE)Checking environment...$(RESET)"
	@if [ ! -f .env ]; then \
		echo "$(RED)✗ .env file not found$(RESET)"; \
		exit 1; \
	fi
	@. .env && \
	if [ -z "$$LIVEKIT_URL" ]; then echo "$(RED)✗ LIVEKIT_URL not set$(RESET)"; exit 1; fi && \
	if [ -z "$$LIVEKIT_API_KEY" ]; then echo "$(RED)✗ LIVEKIT_API_KEY not set$(RESET)"; exit 1; fi && \
	if [ -z "$$LIVEKIT_API_SECRET" ]; then echo "$(RED)✗ LIVEKIT_API_SECRET not set$(RESET)"; exit 1; fi
	@echo "$(GREEN)✓ Environment OK$(RESET)"

logs: ## View logs
	@if [ -f logs/agent.log ]; then \
		tail -f logs/agent.log; \
	else \
		echo "$(YELLOW)No logs found$(RESET)"; \
	fi

info: ## Show system information
	@echo "$(BLUE)System Information$(RESET)"
	@echo ""
	@echo "Python version:"
	@python3 --version
	@echo ""
	@echo "Virtual environment:"
	@if [ -d venv ]; then echo "$(GREEN)✓ Present$(RESET)"; else echo "$(RED)✗ Not found$(RESET)"; fi
	@echo ""
	@echo "espeak:"
	@if command -v espeak >/dev/null 2>&1; then echo "$(GREEN)✓ Installed$(RESET)"; else echo "$(RED)✗ Not installed$(RESET)"; fi
	@echo ""
	@echo "LiveKit server:"
	@if curl -s http://localhost:7880 >/dev/null 2>&1; then echo "$(GREEN)✓ Running$(RESET)"; else echo "$(YELLOW)⚠ Not running$(RESET)"; fi

doctor: check-env info test-connection ## Run all checks

backup: ## Backup configuration
	@echo "$(BLUE)Backing up configuration...$(RESET)"
	@mkdir -p backups
	@cp .env backups/.env.$(shell date +%Y%m%d_%H%M%S)
	@cp requirements.txt backups/requirements.txt.$(shell date +%Y%m%d_%H%M%S)
	@echo "$(GREEN)✓ Configuration backed up$(RESET)"

update: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(RESET)"
	@. venv/bin/activate && pip install --upgrade pip
	@. venv/bin/activate && pip install --upgrade -r requirements.txt
	@echo "$(GREEN)✓ Dependencies updated$(RESET)"

shell: ## Open Python shell with imports
	@. venv/bin/activate && python -i -c "from stt import *; from llm import *; from tts import *; print('Ready!')"

# LiveKit Server Management
livekit-start: ## Start LiveKit server using Docker Compose
	@echo "$(BLUE)Starting LiveKit server...$(RESET)"
	@docker-compose up -d
	@echo "$(GREEN)✓ LiveKit server starting$(RESET)"
	@echo ""
	@echo "Server will be available at:"
	@echo "  WebSocket: ws://localhost:7880"
	@echo "  HTTP API:  http://localhost:7881"
	@echo ""
	@echo "Check status: make livekit-status"
	@echo "View logs:    make livekit-logs"

livekit-stop: ## Stop LiveKit server
	@echo "$(BLUE)Stopping LiveKit server...$(RESET)"
	@docker-compose down
	@echo "$(GREEN)✓ LiveKit server stopped$(RESET)"

livekit-restart: ## Restart LiveKit server
	@echo "$(BLUE)Restarting LiveKit server...$(RESET)"
	@docker-compose restart
	@echo "$(GREEN)✓ LiveKit server restarted$(RESET)"

livekit-status: ## Check LiveKit server status
	@echo "$(BLUE)LiveKit Server Status$(RESET)"
	@echo ""
	@docker-compose ps
	@echo ""
	@if curl -s http://localhost:7880 >/dev/null 2>&1; then \
		echo "$(GREEN)✓ Server is running and healthy$(RESET)"; \
	else \
		echo "$(RED)✗ Server is not responding$(RESET)"; \
	fi

livekit-logs: ## View LiveKit server logs
	@docker-compose logs -f livekit

livekit-clean: ## Stop and remove LiveKit containers and volumes
	@echo "$(YELLOW)Warning: This will stop and remove all LiveKit containers$(RESET)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo "$(GREEN)✓ LiveKit containers removed$(RESET)"; \
	else \
		echo "Cancelled"; \
	fi
