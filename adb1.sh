#!/bin/bash
echo "🚀 设置ADB反向端口转发..."

# 使用绝对路径
ADB_PATH="/home/lzzz/Downloads/platform-tools-latest-linux/platform-tools/adb"

echo "📱 重启ADB服务..."
sudo $ADB_PATH kill-server
sudo $ADB_PATH start-server
sleep 2

echo "🔗 连接设备..."
sudo $ADB_PATH connect 10.0.0.224:5566

echo "🔄 建立反向端口转发..."
sudo $ADB_PATH -s 10.0.0.224:5566 reverse tcp:8012 tcp:8012

echo "✅ 完成！当前状态："
sudo $ADB_PATH devices
echo "反向转发列表："
sudo $ADB_PATH -s 10.0.0.224:5566 reverse --list
