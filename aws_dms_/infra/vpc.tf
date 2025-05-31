# vpc
resource "aws_vpc" "this" {
  cidr_block = "10.0.0.0/16"

  enable_dns_support   = true
  enable_dns_hostnames = true
}

# igw
resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
}

# route table
resource "aws_route_table" "this" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }
}

# route table + subnet 1
resource "aws_route_table_association" "sub_1" {
  subnet_id      = aws_subnet.sub_1.id
  route_table_id = aws_route_table.this.id
}

# route table + subnet 2
resource "aws_route_table_association" "sub_2" {
  subnet_id      = aws_subnet.sub_2.id
  route_table_id = aws_route_table.this.id
}
