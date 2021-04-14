terraform {
  backend "s3" {
    bucket = "nus-iss-equeue-terraform"
    key    = "lambda/searchFilter/tfstate"
    region = "us-east-1"
  }
}
