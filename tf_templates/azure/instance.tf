# Create instance
resource "azurerm_linux_virtual_machine" "instance-1" {
  name                  = var.app_name_1
  location              = var.azure_region_1
  resource_group_name   = azurerm_resource_group.scl_resource_group.name
  network_interface_ids = [azurerm_network_interface.scl_nic.id]
  size                  = var.azure_instance_type_1

  os_disk {
    name                 = "${var.app_name_1}-osdisk"
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "SUSE"
    offer     = var.azure_image_offer
    sku       = var.azure_image_sku
    version   = var.azure_image_version
  }

  computer_name                   = var.app_name_1
  admin_username                  = "azure-user"
  disable_password_authentication = true

  admin_ssh_key {
    username   = "azure-user"
    public_key = var.azure_key_pair_1
  }

  boot_diagnostics {
    storage_account_uri = azurerm_storage_account.scl_sa.primary_blob_endpoint
  }

  tags = {
    environment = "${var.app_name_1}"
  }
}


