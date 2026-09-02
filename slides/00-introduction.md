---
marp: true
theme: robotari
paginate: true
footer: "Robotari · ROS 2 Course (Jazzy)"
title: "ROS 2 Course – Introduction"
---

<!-- _class: title -->
<!-- _paginate: false -->
<!-- _footer: "" -->

# ROS 2 Course
<small>ROS 2 Jazzy Jalisco · Ubuntu 24.04 · Gazebo Harmonic</small>

Paweł Irzyk · Robotari
{{ CITY }} · {{ DATE }}

<!--
Speaker notes go here. Replace {{ CITY }} / {{ DATE }} per delivery
(or set them from the build script with sed).
-->

---

# Agenda

<div class="cols">
<div>

**Day 1 – Foundations**
- What ROS is, and where it came from
- ROS 2 concepts: nodes, topics, messages, parameters
- Working from the command line

**Day 2 – Building**
- Workspace, colcon, packages
- rclpy: nodes, publishers, subscribers, parameters
- Launch files

</div>
<div>

**Day 3 – Tooling**
- Gazebo simulation
- RViz2, TF2, rqt, rosbag
- Robot description (URDF / xacro)

**Day 4 – Advanced communication**
- Services and actions
- Communication strategies
- Course project

</div>
</div>

<!--
TODO: confirm the 4-day split. This is a proposal derived from the module
order in the original deck; adjust once the hands-on labs are timed.
-->

---

# Paweł Irzyk
<small>Robotics Software Engineer · Tech Lead · Founder of Robotari</small>

<div class="cols">
<div>

- Robotics software engineer and tech lead
- ROS 2 training and robotics consulting at Robotari
- {{ EXPERIENCE_LINE }}

</div>
<div>

![w:110](assets/logo-github.png) &nbsp; ![w:170](assets/qr-github.png)
github.com/pawelir

![w:110](assets/logo-linkedin.png) &nbsp; ![w:170](assets/qr-linkedin.png)
linkedin.com/in/pawelirzyk

</div>
</div>

<!--
TODO: replace the bullets with your current bio. The QR codes were regenerated
from the URLs in the original deck – check they still point where you want.
-->

---

<!-- _class: divider -->

# Introduction
<small>What ROS is, how its history was shaped, and how it is used today</small>

---

# Robot Operating System

<div class="cols wide-left">
<div>

Open-source middleware framework for robot software development

- Designed for modularity
- Flexible and extensible
- Supports a wide range of robots
- Community-driven

</div>
<div>

![w:340 center](assets/ros-logo.png)

</div>
</div>

![w:620 center](assets/ros-equation.png)

---

# ROS in practice

![h:520 center](assets/ros-ecosystem.png)

---

# ROS history

<div class="cols wide-left">
<div>

- **2006** – Personal project at Stanford: stop "reinventing the wheel" in robotics
- **2008–2014** – Developed at Willow Garage (PR1, PR2)
- **2009** – First distribution: ROS Mango Tango
- **2013** – Stewardship moves to Open Source Robotics Foundation
- **2017** – First ROS 2 distribution: Ardent Apalone
- **2022** – Core team moves to Intrinsic (Alphabet)
- **2024** – Open Source Robotics Alliance (OSRA) takes over governance

</div>
<div>

![w:120 center](assets/stanford.png)
![w:200 center](assets/pr1-robot.jpg)
![w:120 center](assets/willow-garage.png)

</div>
</div>

---

# ROS growth

![h:470 center](assets/ros-growth.png)

<p class="caption">Number of public ROS repositories and packages over time</p>

---

# ROS 1 vs ROS 2

<div class="cols wide-left">
<div>

What ROS 2 changed:

- **Middleware** – DDS (or Zenoh); no master, scales across machines
- **Quality of Service** – reliability, durability, deadlines per topic
- **Real-time** – deterministic executors, RT-friendly client libraries
- **Security** – authentication, access control, encryption (SROS 2)
- **Launch** – redesigned; Python, XML or YAML
- **Platforms** – Ubuntu Tier 1; Windows and RHEL supported

</div>
<div>

![w:280 center](assets/ros2-logo.png)

</div>
</div>

<div class="note">

ROS 1 reached end-of-life with Noetic in May 2025. New projects start on ROS 2.

</div>

---

# ROS 2 distributions

| Distribution | Released | EOL | Ubuntu |
|---|---|---|---|
| Humble Hawksbill (LTS) | May 2022 | May 2027 | 22.04 |
| **Jazzy Jalisco (LTS)** | **May 2024** | **May 2029** | **24.04** |
| Kilted Kaiju | May 2025 | Dec 2026 | 24.04 |
| Lyrical Luth (LTS) | May 2026 | May 2031 | 26.04 |
| Rolling Ridley | continuous | – | latest |

- A new distribution every May; even years are LTS (5 years of support)
- This course uses **Jazzy**: mature ecosystem, matches most deployed fleets on Ubuntu 24.04
- Everything shown here also works on Kilted and Lyrical unless noted

---

# Modern applications

Examples of ROS-based robotics products

<div class="cols">
<div>

- **Mobile robots** – [Husarion Panther](https://www.youtube.com/watch?v=aABlD3RVOc8)
- **Underwater robots** – [Hydromea EXRAY](https://www.youtube.com/watch?v=Sh3igUyK7Sc)
- **Industrial arms** – [Nomagic](https://www.youtube.com/watch?v=nIrc_bZnsVs) picking cells

</div>
<div>

![w:210](assets/husarion-panther.png) ![w:210](assets/hydromea-exray.png)
![h:190 center](assets/abb-irb120.jpg)

</div>
</div>
