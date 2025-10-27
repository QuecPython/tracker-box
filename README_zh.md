# Smart Tracker解决方案

欢迎来到 QuecPython Tracker 解决方案仓库！本仓库提供了一个全面的解决方案，用于使用 QuecPython Tracker 设备应用程序。



## 介绍

Smart Tracker 是QuecPython专为快速演示与智能资产管理打造的硬件设备。它基于 QuecPython **EG912U**模组开发，支持多种通信模块，具备强大的传感器扩展能力，是你探索 Acceleronix 资产管理 SaaS 平台的理想入口。



### 产品概述

- Tracker 智能定位器

- 终端设备功能涵盖绝大部分定位器应用场景

- 可视化运营平台+手机 APP，设备管理和数据查看更方便

  <img src="./media/tracker_process.png" style="zoom:100%;" />

  

### 产品特点

- 位置信息、危险警情智能感知、识别和上报

- QuecPython 二次开发，模块化、定制化、缩短开发周期

- 可视化运营平台、手机 APP 控制终端

  

### 应用行业

- 车载定位

- 物流货运

- 人员定位

- 电子学生证

- 宠物定位

- 特殊行业(农业灌溉, 稀有物种监控等)

  <img src="./media/tracker_application.png" style="zoom:100%;" />

## 功能



- 多重定位、安全围栏、危险报警、紧急求救、语音监听、录音、轨迹回放、远程控制等

- 智能定位

  - 系统利用 4G 通信/多重定位/分布式服务等技术，为智能定位器行业提供从端到服务的一站式解决方案

- 全平台支持

  - 设备运营平台和手机 APP 功能齐全，终端设备厂商无需自行搭建服务平台即可快速实现对设备和终端用户的管理

- 可靠稳定

  - 终端设备定位精度高、危险感知灵敏度高、功耗低、运行稳定，终端设备厂商可套壳即用，极大缩短硬件开发周期

    <img src="./media/tracker_funcion.png" style="zoom:100%;" />



## 快速开始

### 先决条件

在开始之前，请确保您具备以下先决条件：

- **硬件：**

  - Windows 电脑一台，建议 `Win10` 系统

  - 一套Tracker box产品

    > 购买渠道：联系移远工作人员购买

  - 一张可正常使用的 SIM 卡

- **软件：**

  - QuecPython 模块的 USB 驱动：[QuecPython_USB_Driver_Win10_U_G](https://developer.quectel.com/wp-content/uploads/2024/09/Quectel_Windows_USB_DriverU_V1.0.19.zip)
  - 调试工具 [QPYcom](https://images.quectel.com/python/2022/12/QPYcom_V3.6.0.zip)
  - [QuecPython 固件](https://developer.quectel.com/doc/quecpython/Application_guide/zh/media/solutions/tracker_box(EG912U)/fw/8915DM_cat1_open_EG912UGLAAR05A01M08_TEST0807.zip)
  - QuecPython 固件及相关软件资源
  - Python 文本编辑器（例如，[VSCode](https://code.visualstudio.com/)、[Pycharm](https://www.jetbrains.com/pycharm/download/)）

### 安装



1. **克隆仓库**：

   ```
   # 1.拉取主项目代码
   git clone https://github.com/aaronchenzhihe/tracker-box.git
   cd tracker-box
   git checkout tracker-box-EG912U
   ```

   

2. **烧录固件：** 按照[说明](https://python.quectel.com/doc/Application_guide/zh/dev-tools/QPYcom/qpycom-dw.html#下载固件)将固件烧录到开发板上。

### 运行应用程序

1. **连接硬件：** 按照下图进行硬件连接：

   <img src="./media/usb-c_sim.jpg" style="zoom:30%;" />

   1. 在图示位置插入可用的 Nano SIM 卡
   2. 使用 Type-C 数据线连接开发板和电脑

2. **将代码下载到设备：**

   - 启动 QPYcom 调试工具。
   - 将数据线连接到计算机。
   - 按照[说明](https://python.quectel.com/doc/Application_guide/zh/dev-tools/QPYcom/qpycom-dw.html#下载脚本)将 `code` 文件夹中的所有文件导入到模块的文件系统中，保留目录结构。

3. **运行应用程序：**

   - 选择 `File` 选项卡。

   - 选择 `_main.py` 脚本。

   - 右键单击并选择 `Run` 或使用`运行`快捷按钮执行脚本。

     

## 贡献

我们欢迎对本项目的改进做出贡献！请按照以下步骤进行贡献：

1. Fork 此仓库。

2. 创建一个新分支（`git checkout -b feature/your-feature`）。

3. 提交您的更改（`git commit -m 'Add your feature'`）。

4. 推送到分支（`git push origin feature/your-feature`）。

5. 打开一个 Pull Request。

   

## 许可证

本项目使用 Apache 许可证。详细信息请参阅 [LICENSE](https://github.com/QuecPython/solution-tracker/blob/master/LICENSE) 文件。



## 支持

如果您有任何问题或需要支持，请参阅 [QuecPython 文档](https://python.quectel.com/doc)或在本仓库中打开一个 issue。