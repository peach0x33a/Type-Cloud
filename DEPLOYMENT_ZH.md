# Type Cloud 部署指南

Type Cloud 由两部分组成：服务端 (Server) 和 客户端 (Client)。

## 1. 服务端部署 (服务器)

### Docker 部署 (推荐)
1. 修改 `docker-compose.yml` 中的 `PASSWORD` 和 `JWT_SECRET`。
2. 运行 `docker-compose up -d`。
3. 确保服务器防火墙放行 3000 端口。

### 手动部署
1. `pip install -r server/requirements.txt`
2. `export PASSWORD="your_password"`
3. `python server/app.py`

## 2. 客户端部署 (PC)

### 依赖安装
- Linux (Wayland): `wl-clipboard`, `ydotool`, `kdotool` (KDE)
- Linux (X11): `xclip`, `ydotool`, `xdotool`

### 启动脚本
1. 确保 `ydotoold` 已运行: `sudo ydotoold &`
2. 运行客户端:
   ```bash
   SERVER_URL="http://your-server-ip:3000" ./client/run.sh
   ```

## 3. 配置选项
- `PASTE_METHOD`: 
  - `auto`: 自动识别终端并切换 Ctrl+Shift+V (默认)。
  - `ctrl+v`: 强制使用标准粘贴。
  - `ctrl+shift+v`: 强制使用终端粘贴。
