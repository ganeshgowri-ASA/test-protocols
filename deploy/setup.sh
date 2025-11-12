#!/bin/bash

###############################################################################
# PV Testing Protocol Framework - Automated Setup Script
# Version: 1.0.0
# Description: Automated installation and configuration
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    log_error "Please do not run this script as root"
    exit 1
fi

log_info "Starting PV Testing Protocol Framework Setup..."

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    log_error "Cannot detect OS"
    exit 1
fi

log_info "Detected OS: $OS $VER"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8.0"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    log_error "Python 3.8+ required. Found: $PYTHON_VERSION"
    exit 1
fi

log_info "Python version: $PYTHON_VERSION ✓"

# Install system dependencies
install_dependencies() {
    log_info "Installing system dependencies..."

    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        sudo apt-get update
        sudo apt-get install -y \
            python3-pip \
            python3-venv \
            postgresql \
            postgresql-contrib \
            redis-server \
            libpq-dev \
            build-essential \
            git \
            curl
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        sudo yum update -y
        sudo yum install -y \
            python3-pip \
            python3-devel \
            postgresql \
            postgresql-server \
            redis \
            libpq-devel \
            gcc \
            git \
            curl
    else
        log_warn "OS not explicitly supported. Attempting generic installation..."
    fi

    log_info "System dependencies installed ✓"
}

# Create virtual environment
create_venv() {
    log_info "Creating Python virtual environment..."

    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_info "Virtual environment created ✓"
    else
        log_warn "Virtual environment already exists"
    fi

    source venv/bin/activate
}

# Install Python packages
install_python_packages() {
    log_info "Installing Python packages..."

    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt

    log_info "Python packages installed ✓"
}

# Setup PostgreSQL database
setup_database() {
    log_info "Setting up PostgreSQL database..."

    # Start PostgreSQL
    sudo systemctl start postgresql
    sudo systemctl enable postgresql

    # Create database and user
    sudo -u postgres psql <<EOF
CREATE DATABASE pv_testing;
CREATE USER pv_user WITH ENCRYPTED PASSWORD 'pv_password_change_me';
GRANT ALL PRIVILEGES ON DATABASE pv_testing TO pv_user;
\q
EOF

    log_info "Database setup complete ✓"
}

# Setup Redis
setup_redis() {
    log_info "Setting up Redis..."

    sudo systemctl start redis
    sudo systemctl enable redis

    log_info "Redis setup complete ✓"
}

# Create configuration files
create_config() {
    log_info "Creating configuration files..."

    # Create .env file
    if [ ! -f ".env" ]; then
        cat > .env <<EOF
# Database Configuration
DATABASE_URL=postgresql://pv_user:pv_password_change_me@localhost:5432/pv_testing

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=$(openssl rand -hex 32)

# Redis
REDIS_URL=redis://localhost:6379/0

# Storage
FILE_STORAGE_PATH=/data/pv_testing

# External Integrations (configure as needed)
LIMS_API_KEY=
QMS_API_URL=
PM_API_TOKEN=
EOF
        log_info "Created .env file ✓"
    else
        log_warn ".env file already exists"
    fi

    # Create data directories
    sudo mkdir -p /data/pv_testing/{reports,templates,uploads,exports}
    sudo chown -R $(whoami):$(whoami) /data/pv_testing

    log_info "Configuration files created ✓"
}

# Initialize database
init_database() {
    log_info "Initializing database schema..."

    source venv/bin/activate
    python manage.py db upgrade
    python manage.py load_fixtures

    log_info "Database initialized ✓"
}

# Create admin user
create_admin() {
    log_info "Creating admin user..."

    echo "Please enter admin credentials:"
    read -p "Email: " ADMIN_EMAIL
    read -sp "Password: " ADMIN_PASSWORD
    echo

    source venv/bin/activate
    python manage.py create_user \
        --username admin \
        --email "$ADMIN_EMAIL" \
        --password "$ADMIN_PASSWORD" \
        --role admin

    log_info "Admin user created ✓"
}

# Load protocol templates
load_protocols() {
    log_info "Loading protocol templates..."

    source venv/bin/activate
    python manage.py load_protocols --path templates/protocols/

    log_info "Protocols loaded ✓"
}

# Run tests
run_tests() {
    log_info "Running test suite..."

    source venv/bin/activate
    pytest tests/ -v

    log_info "Tests completed ✓"
}

# Main installation flow
main() {
    log_info "=========================================="
    log_info "PV Testing Protocol Framework Setup"
    log_info "=========================================="
    echo

    read -p "Install system dependencies? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_dependencies
    fi

    create_venv
    install_python_packages

    read -p "Setup PostgreSQL database? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_database
    fi

    read -p "Setup Redis? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_redis
    fi

    create_config
    init_database

    read -p "Create admin user? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_admin
    fi

    load_protocols

    read -p "Run tests? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_tests
    fi

    echo
    log_info "=========================================="
    log_info "Setup Complete!"
    log_info "=========================================="
    echo
    log_info "Next steps:"
    log_info "1. Review and update .env file with your configuration"
    log_info "2. Start the application: ./deploy/start_services.sh"
    log_info "3. Access dashboard at: http://localhost:8501"
    log_info "4. Access API docs at: http://localhost:8000/docs"
    echo
    log_info "For more information, see: docs/INSTALLATION.md"
}

# Run main function
main
