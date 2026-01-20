# ☁️ Type Cloud

> **跨设备实时云剪贴板 & 远程输入控制系统**
>
> 手机打字，电脑上屏。支持 Wayland/X11，智能终端识别，Web 远程控制。

Type Cloud 是一个现代化的文本中继系统，允许你在手机上输入文本，并实时粘贴到电脑的当前活动窗口中。它不仅是剪贴板同步，更是一个远程键盘，支持退格、回车和光标控制。

---

## ✨ 核心特性

*   **📱 手机秒变键盘**: 在手机浏览器输入，电脑实时响应。
*   **🧠 智能终端检测**: 自动识别当前窗口是否为终端（如 Konsole），智能切换 `Ctrl+V` (GUI) 或 `Ctrl+Shift+V` (Terminal) 粘贴模式。
*   **🎮 远程控制**: 网页端提供方向键、退格、回车和“一键清空”功能。
*   **🔒 安全认证**: 基于 JWT 的密码保护，防止未授权访问。
*   **🐧 Linux 友好**: 完美支持 Wayland (KDE/Gnome) 和 X11 环境。
*   **🐳 Docker 部署**: 服务端一键容器化部署。

---

## 🛠️ 项目结构

*   **`server/`**: 服务端核心 (Python Flask + SocketIO)。提供 Web 界面和消息广播。
*   **`client/`**: PC 客户端 (Python)。接收消息并调用系统工具 (`ydotool`) 模拟按键。

---

## 🚀 快速开始

### 1. 服务端部署 (服务器/NAS)

推荐使用 Docker Compose 部署。

1.  上传 `server/` 文件夹到服务器。
2.  进入目录并启动：
    ```bash
    cd server
    docker-compose up -d
    ```
    *默认端口: 3000，默认密码: 123456*

### 2. 客户端使用 (Linux PC)

客户端运行在你需要接收输入的电脑上。

**前置依赖**:
*   `python 3.8+`
*   `wl-copy` (Wayland) 或 `xclip` (X11) - 用于写入剪贴板。
*   `ydotool` - 用于模拟按键粘贴。**必须后台运行守护进程** (`sudo ydotoold &`)。
*   `xdotool` (X11) 或 `kdotool` (KDE Wayland) - 用于智能窗口检测。

**启动**:
```bash
cd client
# 运行一键启动脚本 (自动配置环境)
./run.sh
```

**配置**:
编辑 `client/run.sh` 或设置环境变量：
```bash
export SERVER_URL="http://你的服务器IP:3000"
./client/run.sh
```

---

## ⚙️ 配置说明

### 客户端环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `SERVER_URL` | `http://localhost:3000` | Type Cloud 服务端地址 |
| `PASTE_METHOD` | `auto` | 粘贴模式策略 |

**PASTE_METHOD 选项**:
*   `auto`: **(推荐)** 自动检测当前窗口。如果是终端 (Konsole, Terminal, Kitty 等)，发送 `Ctrl+Shift+V`；否则发送 `Ctrl+V`。
*   `ctrl+v`: 强制使用 GUI 粘贴快捷键。
*   `ctrl+shift+v`: 强制使用终端粘贴快捷键。

---

## 🕹️ Web 控制台功能

访问 `http://服务器IP:3000` 并登录后：

*   **文本框**: 输入文字，按回车或点击发送，文字将立即出现在电脑上。
*   **⬅️ / ➡️**: 移动电脑光标。
*   **退格**: 删除光标前的一个字符。
*   **回车**: 发送回车键。
*   **清空PC**: 智能清空当前输入框（GUI 发送 Ctrl+A+Backspace，终端发送 Ctrl+E+Ctrl+U）。

---

## 🔧 开发指南

**本地开发环境**:

```bash
# 1. 启动服务端 (开发模式)
cd server
./start.sh

# 2. 启动客户端
cd client
# 确保 ydotoold 已运行
python index.py
```

**运行测试**:
```bash
cd server
source venv/bin/activate
python verify_parity.py
```

---

## 📜 License

MIT License.

**Note:** This is a pure Vibe Coding project, built for personal convenience. PRs are not accepted.
