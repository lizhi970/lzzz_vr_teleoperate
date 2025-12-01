
####################此文档是通过vr手柄控制机器臂以及末端执行器运动的说明文档##########################
## 1. 基础环境

```bash
# 创建 conda 基础环境
(base) lzzz@user:~$ conda create -n tv python=3.10 pinocchio=3.1.0 numpy=1.26.0 -c conda-forge
(base) lzzz@user:~$ conda activate tv
```
```bash
# 安装 televuer 模块
(tv) lzzz@Host:~/lzzz_vr_teleoperate$ cd teleop/vuer
(tv) lzzz@Host:~/lzzz_vr_teleoperate/teleop/vuer$ pip install -e .

```bash
# 安装依赖
(tv) lzzz@Host:~/lzzz_vr_teleoperate$ pip install -r requirements.txt
```
### 生成证书文件
```bash
# 默认使用 pico/quest等xr设备
(tv) lzzz@Host:~/lzzz_vr_teleoperate/teleop/vuer$ openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem
```
### 开启防火墙
```bash
(tv) lzzz@Host:~/lzzz_vr_teleoperate/teleop/vuer$ sudo ufw allow 8012
```
### 开启无线端口网络转发
```bash
(tv) lzzz@Host:~/lzzz_vr_teleoperate$ sudo ./adb1.sh
```
> 提示：ADB 在VR设备和电脑之间建立双向数据传输隧道，让双方都能通过 localhost 直接访问对方的服务，相当于变成访问本地服务。ADB可实现无线和有线两种转发。
         有线转发：全程需用一根USB线连接在pc和VR设备之间，在VR设备浏览器上访问http://localhost:8012?ws=ws://localhost:8012
         python中的Vuer创建代码self.vuer = Vuer(queries=dict(grid=False), queue_len=3)。
         无线转发：注意：确保PC和VR设备要在同一网段下，如情况一：设备连接路由器的无线，而电脑通过网线连接到路由器；情况二：PC和VR设备连接同一个wifi
         建立好连接后，同样在VR设备浏览器上访问http://localhost:8012?ws=ws://localhost:8012
         python中的Vuer创建代码self.vuer = Vuer(queries=dict(grid=False), queue_len=3)。
         如果不使用ADB转发的话，直接无线访问，两者处于同一局域网下，那么在VR浏览器中访问https://your_pc_ip:8012?ws=wss://your_pc_ip:8012
         python中的Vuer创建代码为self.vuer = Vuer(host='0.0.0.0', cert=cert_file, key=key_file, queries=dict(grid=False), queue_len=3)
          
## 2. 实机部署
### 启动遥操
本程序通过VR设备（手柄）来控制实际机器人动作。我只测试了手柄控制, to do lzzz
则启动命令如下所示：

```bash
(tv) lzzz@Host:~$ cd ~/lzzz_vr_teleoperate/teleop/
```
```bash
python teleop_hand_and_arm.py --tele-mode=controller --arm-type=R3_23 --hand-type inspire1 --display-type pass-through

```
> 基础控制参数说明：
tele-mode VR 的输入模式：                                        `controller`（手柄）         
display-type VR 的显示模式：                                     `immersive`（沉浸式）or`pass-through`（穿透）   
arm-type 机器人类型：                                            `R3_23`                                  
hand-type 机械手类型：                                           `inspire1`   

完成后继续操作：
1. 人保持坐姿，戴上VR设备（pico4 ultra enterprise），连接WiFi热点
2. 在VR设备里操作，打开浏览器（PICO Browser），输入并访问网址：https://localhost:8012/?ws=wss://localhost:8012
3. 进入`Vuer`网页界面后，点击 **`pass-through`** 按钮，启动 VR 界面，终端会打印出链接建立的信息：
   ```bash
   websocket is connected. id:dbb8537d-a58c-4c57-b49d-cbb91bd25b90
   default socket worker is up, adding clientEvents 
   Uplink task running. id:dbb8537d-a58c-4c57-b49d-cbb91bd25b90
   ```
   > 由于通过adb建立反向端口转发，因此会瞬间建立
4. 为保证机器人的安全性，需将人的手臂摆放到与**机器人初始姿态**相近的姿势。
5. 左手柄中按下 **X** 键后，会正式开启遥操作程序，此时就可以远程控制机器人的手臂。
6. 在遥操过程中，使用左右手柄的按 **trigger** 键可控制**inspire1**机器手的抓握动作。
## 3. 退出
要退出程序，按下右手柄的**A**键。

## 代码敬请期待..........

