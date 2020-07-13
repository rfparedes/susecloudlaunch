# create VPC
resource "google_compute_network" "vpc" {
  name                    = "${var.gcp_env_1}-vpc"
  auto_create_subnetworks = "false"
}

# create private subnet
resource "google_compute_subnetwork" "private_subnet_1" {
  name          = "${var.gcp_env_1}-private-subnet-1"
  ip_cidr_range = var.private_subnet_cidr_1
  network       = google_compute_network.vpc.name
  region        = var.gcp_region_1
}

# create a router
resource "google_compute_router" "router" {
  name    = "${var.gcp_env_1}-router"
  network = google_compute_network.vpc.name
}

# allow tcp from IAP
resource "google_compute_firewall" "allow-tcp-from-iap" {
  name    = "${var.gcp_env_1}-fw-allow-tcp-from-iap"
  network = google_compute_network.vpc.name
  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }
  source_ranges = [
    "35.235.240.0/20"
  ]
}

# external ip address
resource "google_compute_address" "static" {
  name = "ipv4-address"
}

# allow ssh to instance
resource "google_compute_firewall" "allow-ssh-to-instance" {
  name    = "${var.gcp_env_1}-fw-allow-ssh"
  network = google_compute_network.vpc.name
  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }
  source_ranges = [
    "0.0.0.0/0"
  ]

  target_tags = ["ssh"]
}

