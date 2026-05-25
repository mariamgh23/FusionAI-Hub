resource "huaweicloud_vpc" "fusion_vpc" {
  name = "fusion-vpc"
  cidr = "192.168.0.0/16"
}

resource "huaweicloud_vpc_subnet" "fusion_subnet" {
  name       = "fusion-subnet"
  cidr       = "192.168.1.0/24"
  gateway_ip = "192.168.1.1"
  vpc_id     = huaweicloud_vpc.fusion_vpc.id
}
