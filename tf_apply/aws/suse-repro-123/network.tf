# create VPC
resource "aws_vpc" "main" {
  cidr_block = var.private_subnet_cidr_1
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.app_name_1}-${var.app_environment_1}-vpc"
  }
}

# create subnet
resource "aws_subnet" "subnet1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidr_1
  availability_zone = var.aws_zone_1 
}

# create internet gateway
resource "aws_internet_gateway" "gw" {
  vpc_id     = aws_vpc.main.id
 
  tags = {
    Name = "${var.app_name_1}-${var.app_environment_1}-igw"
  } 
}

# create route table
resource "aws_route_table" "rt" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "${var.app_name_1}-${var.app_environment_1}-rt"
  }
}

# create route
resource "aws_route" "internet_access" {
  route_table_id         = aws_route_table.rt.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.gw.id
} 

# associate route with subnet
resource "aws_route_table_association" "vpn_association" {
  subnet_id      = aws_subnet.subnet1.id
  route_table_id = aws_route_table.rt.id
} 



# Create the Security Group
resource "aws_security_group" "SG" {
  vpc_id       = aws_vpc.main.id
  name         = "${var.app_name_1}-${var.app_environment_1}-sg"
  description  = "${var.app_name_1}-${var.app_environment_1} Security Group"

  # allow ingress of port 22
  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
  } 
  
  # allow egress of all ports
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "${var.app_name_1}-${var.app_environment_1}-sg"
  }
}



# create network interface
resource "aws_network_interface" "enic" {
  subnet_id       = aws_subnet.subnet1.id
  security_groups = [aws_security_group.SG.id]

  attachment {
    instance     = aws_instance.instance-1.id
    device_index = 1
  }
}

resource "aws_eip" "ip" {
  #network_interface = aws_network_interface.enic.id
  instance = aws_instance.instance-1.id
  vpc      = true
}
