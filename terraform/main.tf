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
resource "huaweicloud_compute_instance" "fusion_server" {
  name            = "fusion-server"
  image_name      = "Ubuntu 22.04 server 64bit"
  flavor_name     = "s6.small.1"
  security_groups = ["default"]

  network {
    uuid = huaweicloud_vpc_subnet.fusion_subnet.id
  }
}
