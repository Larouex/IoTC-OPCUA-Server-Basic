# IoTC-OPCUA-Server-Basic
OPC/UA Server for Base Testing Scenarios for Azure IoT Central

## Overview
This repository is part of a training and project series for Azure IoT Central.

## Features
This is a simple OPC/UA Server written in Python using the <b>opcua-asyncio</b> that is based on the popular <b>FreeOpcUa</b> project/library.

[LINK: opcua-asyncio](https://github.com/FreeOpcUa/opcua-asyncio)

The server expresses two Nodes...

  * Ambient
  * Process

The <b>Ambient</b> node emits the following parameters...

  * Temperature
  * Humidity
  
The <b>Process</b> node emits the following parameters...

  * Temperature
  * Pressure
  * Mixing Ratio

## Setting up Your Development Toolchain
The code in this repository depends on Visual Studio Code and Python.

### Your Local Machine
The development "toolchain" refers to all of the various tools, SDK's and bits we need to install on your machine to facilitate a smooth experience developing our project. Our main development tool will be Visual Studio code. 

| - | Install These Tools |
|---|---|
| ![Python](./Assets/python-icon-100.png) | [LINK: Python 3 Installation Page](https://www.python.org/downloads/) - Pyhon is the programming language we will use to build applications for the Raspberry Pi. |
| ![Visual Studio Code](./Assets/vs-code-icon-100.png) | [LINK: Visual Studio Code Installation Page](https://code.visualstudio.com/download) - Visual Studio Code is a lightweight but powerful source code editor which runs on your desktop and is available for Windows, macOS and Linux. This is the IDE we will use to write code and deploy to the our BLE Devices and the Raspberry Pi Gateway.  |
| ![Docker](./Assets/docker-icon-100.png) | [LINK: Docker Desktop Install](https://www.docker.com/products/docker-desktop) - Docker Desktop is an application for MacOS and Windows machines for the building and sharing of containerized applications. |

### Upgrading pip
Pip is the package manager we will use to download packages

On Linux or macOS (Open Terminal):
```
    pip install -U pip
```
On Windows (from a CMD window or Powershell):
```
    python -m pip install -U pip
```

### Install all the Tools for Visual Studio Code
These are a set of tools we will use to develop our apps on the Raspberry Pi. You can open the Extensions sidebar with "Shift+Ctrl+X) or click the icon in the side navigator bar.

![alt text](./Assets/vs-code-python-sml.png "VS Code Python")

![alt text](./Assets/vs-code-docker-sml.png "VS Code Docker")

