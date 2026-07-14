
# Network Setup

This document describes the Ethernet network configuration required to connect a native Ubuntu 24.04 PC with the Franka FR3 robot.

The network connection is required for:

- Franka Control Interface (FCI)
- libfranka communication
- `franka_hardware`
- ROS 2 controller communication
- MoveIt trajectory execution

---

## Network Architecture

The communication structure:


Ubuntu PC
|
| Ethernet Cable
|
Franka Control Box
|
|
Franka FR3 Robot


Recommended setup:

             Internet

                |
              WiFi

                |
          Ubuntu PC
                |
          Ethernet
      192.168.0.2
                |
                |
      Franka Control Box
      192.168.0.1
                |
                |
           Franka FR3

WiFi is used for:
- Internet access
- ROS package installation

Ethernet is used for:
- Robot communication
- FCI connection

---

# 1. Hardware Requirements

Required:

- Ubuntu 24.04 PC
- Ethernet cable
- Franka FR3 robot
- Franka Control Box

Connect:


PC Ethernet Port
|
|
Franka Control Box Ethernet Port


---

# 2. Check Ethernet Interface

Find the Ethernet interface:

```bash
ip a

Example:

2: enp0s31f6:

In this example:

Ethernet interface = enp0s31f6

Check Ethernet connection:

ethtool enp0s31f6

Expected:

Link detected: yes
3. Configure Static IP Address

The PC and robot must be in the same subnet.

Default Franka network:

Device	IP Address
Franka Control Box	192.168.0.1
Ubuntu PC	192.168.0.2
Subnet Mask	255.255.255.0
4. Configure Ubuntu Ethernet
GUI Method

Open:

Settings
 └── Network
      └── Wired Connection
           └── IPv4

Select:

Manual

Set:

Address:
192.168.0.2

Netmask:
255.255.255.0

Gateway:
Leave empty

Save and reconnect.

Terminal Method

Find network connection:

nmcli connection show

Example:

Wired connection 1

Configure:

sudo nmcli connection modify \
"Wired connection 1" \
ipv4.method manual \
ipv4.addresses 192.168.0.2/24

Restart:

sudo nmcli connection down \
"Wired connection 1"

sudo nmcli connection up \
"Wired connection 1"
5. Verify Network Configuration

Check IP:

ip addr

Expected:

enp0s31f6

inet 192.168.0.2/24
6. Test Franka Connection

Ping the Franka controller:

ping 192.168.0.1

Expected:

64 bytes from 192.168.0.1

Successful ping confirms:

Ethernet connection works
IP configuration is correct
Robot controller is reachable
7. Check Routing

Check:

ip route

Expected:

192.168.0.0/24 dev enp0s31f6

Example:

default via 172.28.0.1 dev wlp2s0

192.168.0.0/24 dev enp0s31f6

Meaning:

WiFi
 |
 Internet


Ethernet
 |
 Franka Robot
8. Multiple Network Interfaces

A common configuration:

WiFi:
172.28.x.x


Ethernet:
192.168.0.x

This is normal.

The robot communication must use:

Ethernet interface
        |
        |
192.168.0.x subnet

Check:

ip route
9. ROS 2 Network Configuration

ROS 2 uses DDS communication.

Check ROS domain:

echo $ROS_DOMAIN_ID

Default:

0

Set:

export ROS_DOMAIN_ID=0

Permanent:

echo "export ROS_DOMAIN_ID=0" >> ~/.bashrc
10. Franka FCI Requirements

Before launching ROS 2:

Verify:

Robot is powered on
Emergency stop released
Franka Desk shows robot ready
FCI enabled

Communication pipeline:

ROS 2
 |
franka_hardware
 |
libfranka
 |
FCI
 |
Franka FR3
11. Common Network Problems
Problem: Ping Failed

Error:

Destination Host Unreachable

Check:

Ethernet cable
ethtool enp0s31f6

Expected:

Link detected: yes
IP address
ip a

PC:

192.168.0.x

Robot:

192.168.0.1
Problem: libfranka Timeout

Error:

libfranka: Connection timeout

Possible causes:

Wrong robot IP
Incorrect Ethernet configuration
FCI disabled
Network conflict

Check:

ping 192.168.0.1
Problem: ROS 2 Controller Cannot Connect

Symptoms:

Could not contact service:
/controller_manager/list_controllers

Check:

ros2 node list

Expected:

/fr3/controller_manager
12. Recommended Startup Sequence

Follow this order:

1. Connect Ethernet cable
          |
          ↓
2. Configure PC static IP
          |
          ↓
3. Ping Franka controller
          |
          ↓
4. Enable FCI
          |
          ↓
5. Launch Franka ROS 2 driver
          |
          ↓
6. Start MoveIt
          |
          ↓
7. Execute Cartesian Motion
Network Verification Checklist

Before running the FR3 Cartesian Motion Demo:

 Ethernet cable connected
 Ethernet interface detected
 Link status is UP
 PC IP configured as 192.168.0.x
 Robot IP 192.168.0.1 reachable
 FCI enabled
 libfranka connection established
 Franka ROS 2 driver running
 Controllers active
