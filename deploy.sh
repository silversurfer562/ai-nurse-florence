#!/bin/bash
# AI Nurse Florence - Production Deployment Script
# This script sets up a production-ready deployment with live data connections

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
PROJECT_NAME="ai-nurse-florence"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
REQUIRED_COMMANDS=("docker" "docker-compose" "curl")

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    for cmd in "${REQUIRED_COMMANDS[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "$cmd is required but not installed"
            exit 1
        fi
    done

    if [[ ! -f "$ENV_FILE" ]]; then
        log_error ".env file not found. Please copy .env.example to .env and configure it"
        log_info "Run: cp .env.example .env"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Function to validate environment variables
validate_environment() {
    log_info "Validating environment configuration..."

    # Source the .env file
    set -a
    source "$ENV_FILE"
    set +a

    # Check critical variables
    local required_vars=(
        "OPENAI_API_KEY"
        "API_BEARER"
        "REDIS_URL"
        "DATABASE_URL"
    )

    local missing_vars=()

    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            missing_vars+=("$var")
        fi
    done

    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        log_info "Please check your .env file"
        exit 1
    fi

    # Check if OpenAI key looks valid
    if [[ ! "$OPENAI_API_KEY" =~ ^sk- ]]; then
        log_warning "OPENAI_API_KEY doesn't start with 'sk-' - this might be incorrect"
    fi

    log_success "Environment validation passed"
}

# Function to build and start services
deploy_services() {
    log_info "Building and starting services..."

    # Build the application
    log_info "Building Docker images..."
    docker-compose -f "$COMPOSE_FILE" build --pull

    # Start services
    log_info "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d

    log_success "Services started"
}

# Function to wait for services to be healthy
wait_for_services() {
    log_info "Waiting for services to be healthy..."

    local max_attempts=30
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        log_info "Health check attempt $attempt/$max_attempts"

        # Check Redis
        if docker-compose exec redis redis-cli ping &>/dev/null; then
            log_success "Redis is healthy"
            break
        else
            log_warning "Redis not ready yet..."
        fi

        sleep 10
        ((attempt++))
    done

    if [[ $attempt -gt $max_attempts ]]; then
        log_error "Services failed to become healthy within timeout"
        return 1
    fi

    # Wait a bit more for the API to start
    log_info "Waiting for API to start..."
    sleep 15
}

# Function to test the deployment
test_deployment() {
    log_info "Testing deployment..."

    # Test health endpoint
    local health_url="http://localhost:8000/api/v1/health"

    if curl -f -s "$health_url" > /dev/null; then
        log_success "Health endpoint is responding"
    else
        log_error "Health endpoint is not responding"
        log_info "Try: curl $health_url"
        return 1
    fi

    # Test a simple API endpoint
    local disease_url="http://localhost:8000/api/v1/disease/lookup?q=diabetes"
    local auth_header="Authorization: Bearer ${API_BEARER}"

    if curl -f -s -H "$auth_header" "$disease_url" > /dev/null; then
        log_success "Disease lookup API is working"
    else
        log_warning "Disease lookup API may not be working (this could be normal if external APIs are disabled)"
    fi
}

# Function to show deployment status
show_status() {
    log_info "Deployment Status:"
    echo

    # Show running containers
    docker-compose -f "$COMPOSE_FILE" ps

    echo
    log_info "Available endpoints:"
    echo "  🏥 API:        http://localhost:8000"
    echo "  📊 Grafana:    http://localhost:3000 (admin/admin)"
    echo "  📈 Prometheus: http://localhost:9090"
    echo "  🔍 Health:     http://localhost:8000/api/v1/health"
    echo "  📚 Docs:       http://localhost:8000/docs"

    echo
    log_info "Useful commands:"
    echo "  View logs:     docker-compose logs -f"
    echo "  Stop services: docker-compose down"
    echo "  Restart:       docker-compose restart"
    echo "  Update:        docker-compose pull && docker-compose up -d"
}

# Function to show live data status
show_live_data_status() {
    echo
    log_info "Live Data Configuration:"

    # Source the .env file to check settings
    set -a
    source "$ENV_FILE"
    set +a

    if [[ "${USE_LIVE:-0}" == "1" || "${USE_LIVE_APIS:-false}" == "true" ]]; then
        log_success "Live external APIs are ENABLED"
        echo "  ✅ PubMed/NCBI medical literature"
        echo "  ✅ MyDisease.info disease data"
        echo "  ✅ MedlinePlus health information"
        echo "  ✅ ClinicalTrials.gov trial data"
    else
        log_warning "Live external APIs are DISABLED (using mock data)"
        echo "  To enable live data, set USE_LIVE=1 in your .env file"
    fi

    if [[ -n "${OPENAI_API_KEY:-}" ]] && [[ "$OPENAI_API_KEY" != "your-openai-api-key-here" ]]; then
        log_success "OpenAI integration is configured"
    else
        log_warning "OpenAI integration is not configured"
    fi
}

# Main deployment function
main() {
    echo "=========================================="
    echo "🏥 AI Nurse Florence - Production Deploy"
    echo "=========================================="
    echo

    check_prerequisites
    validate_environment
    deploy_services
    wait_for_services

    if test_deployment; then
        log_success "Deployment completed successfully!"
        show_status
        show_live_data_status

        echo
        log_info "🎉 AI Nurse Florence is now running with production configuration!"
        log_info "Check the endpoints above to verify everything is working."
    else
        log_error "Deployment completed but some tests failed"
        log_info "Check the logs: docker-compose logs"
        exit 1
    fi
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        log_info "Stopping services..."
        docker-compose -f "$COMPOSE_FILE" down
        log_success "Services stopped"
        ;;
    "restart")
        log_info "Restarting services..."
        docker-compose -f "$COMPOSE_FILE" restart
        log_success "Services restarted"
        ;;
    "logs")
        docker-compose -f "$COMPOSE_FILE" logs -f
        ;;
    "status")
        show_status
        show_live_data_status
        ;;
    "test")
        source "$ENV_FILE"
        test_deployment
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|logs|status|test}"
        echo
        echo "Commands:"
        echo "  deploy   - Deploy the full stack (default)"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  logs     - Show service logs"
        echo "  status   - Show deployment status"
        echo "  test     - Test the deployment"
        exit 1
        ;;
esac