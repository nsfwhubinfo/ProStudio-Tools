# ProStudio Dynamic Memory Caching - GCP Infrastructure
# ====================================================

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "prostudio-terraform-state"
    prefix = "prod/terraform"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP zone"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "prostudio"
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "container.googleapis.com",
    "containerregistry.googleapis.com",
    "redis.googleapis.com",
    "secretmanager.googleapis.com",
    "servicenetworking.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "memcache.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com"
  ])
  
  service                    = each.key
  disable_on_destroy         = false
  disable_dependent_services = false
}

# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "${var.app_name}-vpc-${var.environment}"
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
  
  depends_on = [google_project_service.required_apis["compute.googleapis.com"]]
}

# Subnets
resource "google_compute_subnetwork" "private" {
  name          = "${var.app_name}-private-${var.environment}"
  ip_cidr_range = "10.0.0.0/20"
  region        = var.region
  network       = google_compute_network.vpc.id
  
  secondary_ip_range {
    range_name    = "gke-pods"
    ip_cidr_range = "10.4.0.0/14"
  }
  
  secondary_ip_range {
    range_name    = "gke-services"
    ip_cidr_range = "10.8.0.0/20"
  }
  
  private_ip_google_access = true
}

# Cloud NAT for outbound connectivity
resource "google_compute_router" "router" {
  name    = "${var.app_name}-router-${var.environment}"
  region  = var.region
  network = google_compute_network.vpc.id
}

resource "google_compute_router_nat" "nat" {
  name                               = "${var.app_name}-nat-${var.environment}"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  
  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Service Networking for Memorystore
resource "google_compute_global_address" "service_range" {
  name          = "${var.app_name}-service-range-${var.environment}"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

resource "google_service_networking_connection" "service_networking" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.service_range.name]
}

# Memorystore Redis Instance (Equivalent to ElastiCache)
resource "google_redis_instance" "cache" {
  name               = "${var.app_name}-redis-${var.environment}"
  tier               = "STANDARD_HA"  # High availability
  memory_size_gb     = 13  # Similar to cache.r7g.large
  region             = var.region
  location_id        = var.zone
  alternative_location_id = "${var.region}-b"  # For HA
  
  authorized_network = google_compute_network.vpc.id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"
  
  redis_version      = "REDIS_7_0"
  display_name       = "ProStudio Redis Cache ${var.environment}"
  
  redis_configs = {
    "maxmemory-policy"  = "allkeys-lru"
    "timeout"           = "300"
    "tcp-keepalive"     = "60"
    "notify-keyspace-events" = "AKE"
  }
  
  auth_enabled = true
  
  transit_encryption_mode = "SERVER_AUTHENTICATION"
  
  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 3
        minutes = 0
      }
    }
  }
  
  labels = {
    environment = var.environment
    app         = var.app_name
    component   = "cache"
  }
  
  depends_on = [
    google_service_networking_connection.service_networking
  ]
}

# GKE Cluster (Alternative to ECS)
resource "google_container_cluster" "primary" {
  provider = google-beta
  
  name     = "${var.app_name}-gke-${var.environment}"
  location = var.region
  
  # Regional cluster for HA
  node_locations = [
    "${var.region}-a",
    "${var.region}-b",
    "${var.region}-c"
  ]
  
  remove_default_node_pool = true
  initial_node_count       = 1
  
  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.private.name
  
  ip_allocation_policy {
    cluster_secondary_range_name  = "gke-pods"
    services_secondary_range_name = "gke-services"
  }
  
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }
  
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
  
  cluster_autoscaling {
    enabled = true
    
    resource_limits {
      resource_type = "cpu"
      minimum       = 4
      maximum       = 100
    }
    
    resource_limits {
      resource_type = "memory"
      minimum       = 16
      maximum       = 400
    }
    
    auto_provisioning_defaults {
      service_account = google_service_account.gke_node.email
      oauth_scopes = [
        "https://www.googleapis.com/auth/cloud-platform"
      ]
    }
  }
  
  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
    
    managed_prometheus {
      enabled = true
    }
  }
  
  addons_config {
    horizontal_pod_autoscaling {
      disabled = false
    }
    
    http_load_balancing {
      disabled = false
    }
    
    network_policy_config {
      disabled = false
    }
  }
  
  release_channel {
    channel = "REGULAR"
  }
  
  cost_management_config {
    enabled = true
  }
}

# Node Pool
resource "google_container_node_pool" "primary" {
  name       = "${var.app_name}-node-pool-${var.environment}"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  
  initial_node_count = 1
  
  autoscaling {
    min_node_count = 2
    max_node_count = 20
  }
  
  management {
    auto_repair  = true
    auto_upgrade = true
  }
  
  node_config {
    preemptible  = false
    machine_type = "n2-standard-4"  # 4 vCPU, 16 GB memory
    
    disk_size_gb = 100
    disk_type    = "pd-balanced"
    
    service_account = google_service_account.gke_node.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
    
    workload_metadata_config {
      mode = "GKE_METADATA"
    }
    
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }
    
    labels = {
      environment = var.environment
      app         = var.app_name
    }
    
    tags = ["${var.app_name}-gke-node"]
  }
}

# Spot instance node pool for cost optimization
resource "google_container_node_pool" "spot" {
  name       = "${var.app_name}-spot-pool-${var.environment}"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  
  initial_node_count = 0
  
  autoscaling {
    min_node_count = 0
    max_node_count = 10
  }
  
  management {
    auto_repair  = true
    auto_upgrade = true
  }
  
  node_config {
    spot         = true
    machine_type = "n2-standard-4"
    
    disk_size_gb = 100
    disk_type    = "pd-balanced"
    
    service_account = google_service_account.gke_node.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
    
    workload_metadata_config {
      mode = "GKE_METADATA"
    }
    
    taint {
      key    = "spot-instance"
      value  = "true"
      effect = "NO_SCHEDULE"
    }
    
    labels = {
      environment = var.environment
      app         = var.app_name
      spot        = "true"
    }
    
    tags = ["${var.app_name}-gke-spot-node"]
  }
}

# Service Account for GKE nodes
resource "google_service_account" "gke_node" {
  account_id   = "${var.app_name}-gke-node-${var.environment}"
  display_name = "GKE Node Service Account"
}

# IAM roles for node service account
resource "google_project_iam_member" "gke_node_roles" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer",
    "roles/artifactregistry.reader"
  ])
  
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.gke_node.email}"
}

# Artifact Registry for container images
resource "google_artifact_registry_repository" "app" {
  location      = var.region
  repository_id = "${var.app_name}-${var.environment}"
  format        = "DOCKER"
  
  description = "Docker repository for ${var.app_name}"
  
  labels = {
    environment = var.environment
    app         = var.app_name
  }
}

# Cloud Storage bucket for cache persistence
resource "google_storage_bucket" "cache_persistence" {
  name          = "${var.app_name}-cache-${var.environment}-${var.project_id}"
  location      = var.region
  force_destroy = false
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
  
  labels = {
    environment = var.environment
    app         = var.app_name
  }
}

# Outputs
output "gke_cluster_name" {
  description = "GKE cluster name"
  value       = google_container_cluster.primary.name
}

output "gke_cluster_endpoint" {
  description = "GKE cluster endpoint"
  value       = google_container_cluster.primary.endpoint
  sensitive   = true
}

output "redis_host" {
  description = "Redis instance host"
  value       = google_redis_instance.cache.host
  sensitive   = true
}

output "redis_port" {
  description = "Redis instance port"
  value       = google_redis_instance.cache.port
}

output "redis_auth_string" {
  description = "Redis auth string"
  value       = google_redis_instance.cache.auth_string
  sensitive   = true
}

output "artifact_registry_url" {
  description = "Artifact Registry URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.app.repository_id}"
}

output "cache_bucket_name" {
  description = "GCS bucket for cache persistence"
  value       = google_storage_bucket.cache_persistence.name
}