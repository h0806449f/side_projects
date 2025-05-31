# Subnet group for RDS
resource "aws_db_subnet_group" "this" {
  name        = "henry-db-subnet-group"
  description = "Subnet group for RDS instances"
  subnet_ids = [
    aws_subnet.sub_1.id,
    aws_subnet.sub_2.id
  ]
}


# source db
resource "aws_db_instance" "source" {
  # basic config
  allocated_storage    = 10
  db_name              = "source_db"
  engine               = "mysql"
  engine_version       = "8.0"
  instance_class       = "db.t3.micro"
  parameter_group_name = "default.mysql8.0"
  skip_final_snapshot  = true
  publicly_accessible  = true


  # subnet
  db_subnet_group_name = aws_db_subnet_group.this.name
  multi_az             = true
  # sg
  vpc_security_group_ids = [aws_security_group.this.id]

  # master user
  username = "henry"
  password = "12345678"

  # dependency
  depends_on = [aws_db_subnet_group.this]
}


# target db
resource "aws_db_instance" "target" {
  # basic config
  allocated_storage    = 10
  db_name              = "target_db"
  engine               = "mysql"
  engine_version       = "8.0"
  instance_class       = "db.t3.micro"
  parameter_group_name = "default.mysql8.0"
  skip_final_snapshot  = true
  publicly_accessible  = true

  # subnet
  db_subnet_group_name = aws_db_subnet_group.this.name
  multi_az             = true
  # sg
  vpc_security_group_ids = [aws_security_group.this.id]

  # master user
  username = "henry"
  password = "12345678"

  # dependency
  depends_on = [aws_db_subnet_group.this]
}
