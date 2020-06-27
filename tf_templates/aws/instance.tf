# Create instance
resource "aws_instance" "instance-1" {
  instance_type          = var.aws_instance_type_1
  availability_zone      = var.aws_zone_1
  ami                    = var.aws_ami_1
  subnet_id              = aws_subnet.subnet1.id
  vpc_security_group_ids = [aws_security_group.SG.id]
  key_name               = aws_key_pair.deployer.id
  tags = {
    Name = "${var.app_name_1}-${var.app_environment_1}"
  }
}

# Create key pair
resource "aws_key_pair" "deployer" {
  key_name   = "${var.app_name_1}-${var.app_environment_1}-key"
  public_key = var.aws_key_pair_1
}

output "ip" {
  value = aws_eip.ip.public_ip
}
