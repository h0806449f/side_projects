data "aws_availability_zones" "this" {
  state = "available"
}


# subnet 1
resource "aws_subnet" "sub_1" {
  vpc_id     = aws_vpc.this.id
  cidr_block = "10.0.1.0/24"

  availability_zone       = data.aws_availability_zones.this.names[1]
  map_public_ip_on_launch = true
  # availability_zone       = "ap-northeast-1a"

  tags = {
    Name = "sub-1"
  }
}


# Subnet 2
resource "aws_subnet" "sub_2" {
  vpc_id     = aws_vpc.this.id
  cidr_block = "10.0.2.0/24"

  availability_zone       = data.aws_availability_zones.this.names[2]
  map_public_ip_on_launch = true
  # availability_zone       = "ap-northeast-1c"

  tags = {
    Name = "sub-2"
  }
}
