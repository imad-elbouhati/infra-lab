# Infrastructure automation lab using **Ansible** and **Docker**.

This repository contains Ansible playbooks and roles to build an infra lab including:
- WireGuard tunnels
- nftables firewall rules
- Docker & Docker Compose apps
- Nginx reverse proxy for routing
- GitLab Runners (Docker executor)
- TLS/SSL automation with Let’s Encrypt and CertBot (ACME)

---

## Features
- Automated provisioning with Ansible
- VPN and firewall configuration
- Containerized services using Docker Compose
- Reverse proxy with automatic TLS certificates
- GitLab Runner deployment and registration
- Inventory-driven configuration with Ansible Vault support for secrets
- SSH hardening (disable root login, enforce key-based auth, configurable settings)
---

## Requirements
- Ansible (>= 2.12)
- SSH access and sudo/root privileges on managed hosts
- DNS records pointing to proxy host for TLS validation
- GitLab instance or gitlab.com with a registration token

Optional:
- Ansible Vault for sensitive values (tokens, keys, certs)

---

## Usage
1. Define your hosts in `inventory/hosts.yaml`
2. Configure variables in `group_vars/` and `host_vars/`
3. Run the bootstrap and setup playbooks:
   ```bash
   ansible-playbook -i inventory/hosts.yaml setup.yaml
