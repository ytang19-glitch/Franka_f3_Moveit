
## Docker vs Native Ubuntu Development

### Overview

This project was developed in two stages:

1. **Docker-based development** for rapid environment setup and software validation.
```bash
  https://github.com/ytang19-glitch/Learn_Docker
```
3. **Native Ubuntu 24.04 development** for controlling the physical Franka FR3 robot using ROS 2 Jazzy and MoveIt 2.

The migration from Docker to a native environment was necessary because real robot control requires direct hardware communication through the Franka Control Interface (FCI).

---

## Development Timeline

```text
1. Check ROS 2 Control Status
        │
        ▼
ros2 control list_controllers
(waiting for controller manager service)

        │
        ▼
2. Run Franka ROS 2 Docker Environment
        │
        ▼
Docker starts successfully
        │
        ▼
3. libfranka Connection Timeout
        │
        ▼
Diagnosis:
- Workstation connected to wrong Ethernet port
- Connected to Arm LAN port instead of Control Box LAN port
- Wrong IP address used
        │
        ▼
Fix:
- Connect workstation directly to Franka Control Box Ethernet port
- Use Control Box IP address
- Configure correct network settings
        │
        ▼
4. Successfully Connect to Franka FR3
        │
        ▼
5. Build ROS 2 Franka Workspace
        │
        ▼
Build packages:
- franka_description
- franka_hardware
- franka_bringup
- franka_fr3_moveit_config
- MoveIt 2 packages
        │
        ▼

6. Learn and Configure MoveIt 2
        │
        ▼
7. Develop Cartesian Motion Demo
        │
        ▼
8. Test in Simulation
(Gazebo / RViz / MoveIt)

        │
        ▼
9. Native Ubuntu 24.04 Setup
        │
        ▼
10. Configure Ethernet + FCI
        │
        ▼
11. Launch MoveIt 2 on Real FR3
        │
        ▼
12. Execute Cartesian Motion
(Real Robot)
```

---

## Why Start with Docker?

Docker provides an isolated and reproducible development environment.

It was used during the early stage of the project to:

- Install ROS 2 Jazzy quickly
- Build the Franka ROS2 packages
- Learn the MoveIt 2 framework
- Develop and test the software architecture
- Avoid dependency conflicts

Docker significantly reduced the initial setup time and made experimentation safer.

---

## Why Migrate to Native Ubuntu?

Although Docker is excellent for software development, controlling a physical industrial robot requires direct access to hardware resources.

The project was migrated to **Ubuntu 24.04** because it provides:

- Native Ethernet communication
- Direct access to the Franka Control Interface (FCI)
- Lower communication latency
- Easier network configuration
- Better integration with ROS 2 controllers
- Simpler debugging using Linux networking tools

The native environment is therefore recommended for real robot deployment.

---

## Comparison

| Feature | Docker | Native Ubuntu |
|----------|---------|----------------|
| Easy installation | Y | N |
| Dependency isolation | Y | N |
| Software development | Y | Y |
| Simulation | Y | Y |
| MoveIt planning | Y | Y |
| RViz visualization | Y | Y |
| Direct FR3 communication |  Limited | Y |
| Ethernet configuration | More complex | Native |
| Hardware debugging | Limited | Excellent |
| Industrial deployment | Rare | Recommended |

---

## Software Architecture

The software architecture remains identical in both environments.

### The architecture of using docker 

```bash
        Docker Verification Workflow
               │
               ▼
        Docker Container
               │
               ▼
        ROS 2 Humble Environment
               │
               ▼
        franka-docker image
               │
               ▼
        franky_bridge / libfranka
               │
               ▼
        FCI Communication
               │
               ▼
        Franka FR3 Robot
```

### Ubuntu native Software Architecture

```text
User
    │
    ▼
cartesian_move.launch.py
    │
    ▼
cartesian_move.py
    │
    ▼
MoveIt Python API
    │
    ▼
MoveIt Planning Pipeline
    │
    ▼
ROS 2 Controllers
    │
    ▼
Franka ROS2 Driver (libfranka)
    │
    ▼
Franka FR3
```

The only difference is the execution environment.

Docker isolates the operating system, while the native installation communicates directly with the robot hardware.

---

## Lessons Learned

Docker is an excellent platform for:

- Learning ROS 2
- Software development
- Motion planning
- Simulation
- Package development

Native Ubuntu is better suited for:

- Hardware integration
- Ethernet configuration
- Real-time robot communication
- Motion execution
- Research experiments
- Industrial deployment

---

## Conclusion

Both environments play an important role in robotics software development.

Docker accelerates software development by providing a clean and reproducible environment, while native Ubuntu enables reliable communication with the Franka FR3 hardware.

This project demonstrates the complete engineering workflow:

```text
Docker Development
        │
        ▼
ROS 2 & MoveIt Learning
        │
        ▼
Custom MoveIt Package Development
        │
        ▼
Migration to Native Ubuntu
        │
        ▼
Real Franka FR3 Cartesian Motion
```

The final implementation runs natively on **Ubuntu 24.04**, using **ROS 2 Jazzy**, **MoveIt 2**, and the official **Franka ROS2** software stack to execute Cartesian motion on the Franka FR3 robot.
