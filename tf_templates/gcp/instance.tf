# Create instance 
resource "google_compute_instance" "instance-1" {
  name         = "${var.gcp_env_1}-instance"
  machine_type = var.gcp_machine_type_1
  zone         = var.gcp_zone_1

  tags = ["ssh"]

  boot_disk {
    initialize_params {
      image = var.gcp_image_1
    }
  }

  metadata = {
    ssh-keys = var.ssh_keys
  }

  network_interface {
    network    = google_compute_network.vpc.name
    subnetwork = google_compute_subnetwork.private_subnet_1.name
    access_config {
      nat_ip = google_compute_address.static.address
    }
  }
  allow_stopping_for_update = true
}


# # show bastion ip address
output "ip" {
  value       = google_compute_instance.instance-1.network_interface.0.access_config.0.nat_ip
  description = "public ip address"
}

