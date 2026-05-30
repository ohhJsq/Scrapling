# Hermes Web UI & Agent - Docker 部署指南

## 快速开始

### 前置要求

- Docker (v20.10.0+
- Docker Compose (v2.0.0+)

### 部署步骤

1. **准备配置文件**

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，根据需要修改配置
nano .env
```

2. **启动服务**

```bash
# 使用预构建镜像（推荐）
docker compose up -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f
```

3. **访问 Web UI**

打开浏览器访问：`http://localhost:6060`

### 获取认证令牌

首次启动时，认证令牌会自动生成并打印在日志中：

```bash
# 查看 Web UI 日志获取令牌
docker compose logs hermes-webui | grep "Auth token"
```

令牌也会保存在 `./hermes_data/hermes-web-ui/.token`

### 常用命令

```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose down

# 重启服务
docker compose restart

# 查看日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f hermes-webui
docker compose logs -f hermes-agent

# 更新镜像并重启
docker compose pull
docker compose up -d

# 清理所有数据（警告：会删除所有配置和数据）
docker compose down -v
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `HERMES_AGENT_IMAGE` | Hermes Agent 镜像 | `nousresearch/hermes-agent:latest` |
| `WEBUI_IMAGE` | Web UI 镜像 | `ekkoye8888/hermes-web-ui:latest` |
| `PORT` | Web UI 访问端口 | `6060` |
| `HERMES_DATA_DIR` | 数据存储目录 | `./hermes_data` |
| `AUTH_DISABLED` | 是否禁用认证 | `false` |
| `AUTH_TOKEN` | 自定义认证令牌 | (自动生成) |
| `TZ` | 时区 | `Asia/Shanghai` |

### 数据持久化

所有数据都会持久化在 `./hermes_data` 目录下：

```
hermes_data/
├── config.yaml          # Hermes 配置
├── auth.json          # API 凭证
├── hermes-web-ui/
│   └── .token         # Web UI 认证令牌
├── skills/             # 技能文件
├── memories/           # 记忆文件
└── ...
```

## 安全建议

1. **不要在公共网络上禁用认证
2. 使用强认证令牌
3. 定期备份 `hermes_data` 目录
4. 限制 CORS_ORIGINS 为您的域名
5. 使用反向代理 (Nginx/Apache) 添加 HTTPS

## 故障排除

### 服务无法启动

```bash
# 检查容器状态
docker compose ps

# 查看详细日志
docker compose logs hermes-webui
docker compose logs hermes-agent

# 检查端口是否被占用
netstat -tulpn | grep 6060
```

### 认证问题

```bash
# 重置认证令牌
rm -f ./hermes_data/hermes-web-ui/.token
docker compose restart hermes-webui

# 查看新生成的令牌
docker compose logs hermes-webui | grep "Auth token"
```

### 数据备份与恢复

```bash
# 备份数据
tar -czf hermes_backup_$(date +%Y%m%d).tar.gz ./hermes_data

# 恢复数据
docker compose down
rm -rf ./hermes_data
tar -xzf hermes_backup_20240101.tar.gz
docker compose up -d
```

## 从源码构建（可选）

如果需要从源码构建 Web UI 镜像：

```bash
# 克隆仓库
git clone https://github.com/ohhJsq/hermes-web-ui.git
cd hermes-web-ui

# 构建并启动
docker compose up -d --build
```

## 更多信息

- [Hermes Agent 官方文档](https://hermes-agent.nousresearch.com/docs/)
- [Hermes Web UI GitHub](https://github.com/ohhJsq/hermes-web-ui)
- [Hermes Agent GitHub](https://github.com/ohhJsq/hermes-agent)
