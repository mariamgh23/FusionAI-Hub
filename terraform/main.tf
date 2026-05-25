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

resource "huaweicloud_networking_secgroup" "fusion_secgroup" {
  name = "fusion-secgroup"
}

resource "huaweicloud_networking_secgroup_rule" "allow_ssh" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = huaweicloud_networking_secgroup.fusion_secgroup.id
}

resource "huaweicloud_networking_secgroup_rule" "allow_http" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 80
  port_range_max    = 80
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = huaweicloud_networking_secgroup.fusion_secgroup.id
}

resource "huaweicloud_networking_secgroup_rule" "allow_app" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 8000
  port_range_max    = 8000
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = huaweicloud_networking_secgroup.fusion_secgroup.id
}

resource "huaweicloud_vpc_eip" "fusion_eip" {
  publicip {
    type = "5_bgp"
  }

  bandwidth {
    name        = "fusion-bandwidth"
    size        = 5
    share_type  = "PER"
    charge_mode = "traffic"
  }
}

resource "huaweicloud_compute_instance" "fusion_server" {
  name              = "fusion-server"
  flavor_name       = "s6.small.1"
  image_name        = "Ubuntu 22.04 server 64bit"
  security_group_ids = [
    huaweicloud_networking_secgroup.fusion_secgroup.id
  ]

  network {
    uuid = huaweicloud_vpc_subnet.fusion_subnet.id
  }
}

resource "huaweicloud_compute_eip_associate" "fusion_eip_assoc" {
  public_ip   = huaweicloud_vpc_eip.fusion_eip.address
  instance_id = huaweicloud_compute_instance.fusion_server.id
}
