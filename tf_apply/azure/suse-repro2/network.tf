# create resource group
resource "azurerm_resource_group" "scl_resource_group" {
  name     = "${var.app_name_1}-ResourceGroup"
  location = var.azure_region_1
  tags = {
    environment = "${var.app_name_1}"
  }
}

# create Virtual Network
resource "azurerm_virtual_network" "scl_network" {
  name                = "${var.app_name_1}-vnet"
  address_space       = ["${var.private_vpc_cidr_1}"]
  location            = var.azure_region_1
  resource_group_name = azurerm_resource_group.scl_resource_group.name
  tags = {
    environment = "${var.app_name_1}"
  }
}

# create subnet
resource "azurerm_subnet" "scl_subnet" {
  name                 = "${var.app_name_1}-subnet"
  resource_group_name  = azurerm_resource_group.scl_resource_group.name
  virtual_network_name = azurerm_virtual_network.scl_network.name
  address_prefix       = var.private_subnet_cidr_1
}

# create public IP address
resource "azurerm_public_ip" "scl_publicip" {
  name                = "${var.app_name_1}-publicip"
  location            = var.azure_region_1
  resource_group_name = azurerm_resource_group.scl_resource_group.name
  allocation_method   = "Static"

  tags = {
    environment = "${var.app_name_1}"
  }
}

# create network security group
resource "azurerm_network_security_group" "scl_nsg" {
  name                = "${var.app_name_1}-nsg"
  location            = var.azure_region_1
  resource_group_name = azurerm_resource_group.scl_resource_group.name

  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  tags = {
    environment = "${var.app_name_1}"
  }
}

# Create virtual NIC
resource "azurerm_network_interface" "scl_nic" {
  name                = "${var.app_name_1}-nic"
  location            = var.azure_region_1
  resource_group_name = azurerm_resource_group.scl_resource_group.name

  ip_configuration {
    name                          = "${var.app_name_1}-nicconfig"
    subnet_id                     = azurerm_subnet.scl_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.scl_publicip.id
  }
  tags = {
    environment = "${var.app_name_1}"
  }
}

# Connect nsg to nic
resource "azurerm_network_interface_security_group_association" "scl_nicsgassoc" {
  network_interface_id      = azurerm_network_interface.scl_nic.id
  network_security_group_id = azurerm_network_security_group.scl_nsg.id
}

# Create storage account for diagnostics
# storage account needs random name so this is generated here
resource "random_id" "randomId" {
  keepers = {
    # Generate a new ID only when a new resource group is defined
    resource_group = azurerm_resource_group.scl_resource_group.name
  }
  byte_length = 8
}

resource "azurerm_storage_account" "scl_sa" {
  name                     = "diag${random_id.randomId.hex}"
  location                 = var.azure_region_1
  resource_group_name      = azurerm_resource_group.scl_resource_group.name
  account_replication_type = "LRS"
  account_tier             = "Standard"

  tags = {
    environment = "${var.app_name_1}"
  }
}

output "ip" {
  value = azurerm_public_ip.scl_publicip.ip_address
}
