# basic sg
resource "aws_security_group" "this" {
  name        = "henry_testing"
  description = "testing description"
  vpc_id      = aws_vpc.this.id
}

# ipv4 ingress
resource "aws_vpc_security_group_ingress_rule" "this" {
  security_group_id = aws_security_group.this.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # -1 = all ports
}

# ipv4 egress
resource "aws_vpc_security_group_egress_rule" "this" {
  security_group_id = aws_security_group.this.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # -1 = all ports
}
