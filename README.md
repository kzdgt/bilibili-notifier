# Bilibili 关注动态监控脚本

## 简介

本脚本用于监控哔哩哔哩（Bilibili）用户关注的 UP 主的动态，当有新视频发布时，会通过飞书机器人发送消息通知。脚本会自动处理登录、Cookie 管理和动态数据的比较，确保每次运行时能准确识别新视频。

### 功能特点:

1.  **自动登录**：支持扫码登录，自动处理 Cookie 的保存和验证。
2.  **多类型监控**：支持监控视频动态和文字/图文动态。
3.  **消息推送**：通过飞书机器人发送包含视频信息的卡片消息。
4.  **数据比较**：使用临时文件和本地文件比较，确保只推送新内容。
5. **Docker支持**：提供Docker容器化部署方案。
6. **灵活配置**：通过配置文件自定义监控类型和推送设置。

## 项目结构

```
bilibili-new-video-notifier/
├── bilibili_followed_dynamics.py  # 主程序文件
├── config.json                    # 配置文件（运行时自动生成）
├── requirements.txt               # Python依赖包列表
├── Dockerfile                     # Docker镜像构建文件
├── docker-compose.yml             # Docker Compose配置
├── docker-deploy.sh               # Docker部署脚本
├── .dockerignore                  # Docker构建忽略文件
├── .gitignore                     # Git忽略文件
├── README.md                      # 项目说明文档
└── LICENSE                        # 开源许可证
```

### 文件说明

- **bilibili_followed_dynamics.py**: 核心脚本，包含登录、监控、消息推送等功能
- **config.json**: 配置文件，包含飞书Webhook地址和监控设置
- **requirements.txt**: 项目依赖的Python包列表
- **Dockerfile**: 用于构建Docker镜像
- **docker-compose.yml**: Docker Compose服务配置，简化部署流程

## 快速开始 🚀

### 1分钟快速部署

**Docker方式（推荐）：**

**Linux/Mac:**
```bash
# 1. 克隆项目
git clone <项目地址>
cd bilibili-new-video-notifier

# 2. 运行部署脚本（自动构建镜像并启动服务）
bash docker-deploy.sh

# 3. 查看运行状态
docker-compose logs -f
```

**Windows (PowerShell):**
```powershell
# 1. 克隆项目
git clone <项目地址>
cd bilibili-new-video-notifier

# 2. 构建并启动服务
docker build -t bilibili-notifier .
docker-compose up -d

# 3. 查看运行状态
docker-compose logs -f
```

**本地方式：**
```bash
# 1. 克隆项目
git clone <项目地址>
cd bilibili-new-video-notifier

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行脚本（配置文件会自动生成）
python bilibili_followed_dynamics.py
```

## 详细安装与配置

### 方式一：Docker部署（推荐）

#### 1. 快速开始
```bash
# 1. 运行一键部署脚本（自动构建镜像并启动服务）
bash docker-deploy.sh

# 2. 查看服务状态
docker-compose ps

# 3. 查看日志
docker-compose logs -f
```

#### 2. 手动部署步骤
```bash
# 1. 构建Docker镜像
docker build -t bilibili-notifier .

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f
```

#### 3. 服务管理
```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps

# 进入容器调试
docker-compose exec bilibili-notifier /bin/bash
```


### 方式二：本地部署

#### 1. 环境要求
*   Python 3.x
*   所需 Python 库：`requests`, `qrcode`, `schedule`

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 配置文件
脚本会自动生成默认配置文件`config.json`，你也可以手动创建：
```bash
# 编辑 config.json，设置你的飞书Webhook地址
# 配置文件会在首次运行时自动生成
```

配置文件说明：
```json
{
  "followed_dynamic_types": ["DYNAMIC_TYPE_AV", "DYNAMIC_TYPE_DRAW"],
  "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook地址",
  "check_interval_minutes": 1
}
```

### 配置项详细说明

| 配置项 | 类型 | 必填 | 说明 | 可选值 |
|--------|------|------|------|--------|
| `followed_dynamic_types` | array | 是 | 监控的动态类型 | `DYNAMIC_TYPE_AV` (视频)<br>`DYNAMIC_TYPE_DRAW` (图文/文字) |
| `feishu_webhook` | string | 是 | 飞书机器人Webhook地址 | 从飞书群聊机器人设置中获取 |
| `check_interval_minutes` | integer | 否 | 检查间隔时间（分钟） | 建议值：1-5分钟 |

### 动态类型说明

- **DYNAMIC_TYPE_AV**: 视频动态，当关注的UP主发布新视频时触发通知
- **DYNAMIC_TYPE_DRAW**: 图文/文字动态，当关注的UP主发布图文或纯文字动态时触发通知

### 飞书Webhook获取方法

1. 在飞书群聊中点击右上角"..." → "设置" → "群机器人"
2. 点击"添加机器人"，选择"自定义机器人"
3. 设置机器人名称和头像，点击"添加"
4. 复制Webhook地址，填入配置文件中的`feishu_webhook`字段

## 使用方法

### 1. 运行脚本

**Docker方式：**
```bash
docker-compose up -d
```

**本地方式：**
```bash
python bilibili_followed_dynamics.py
```

### 2. 扫码登录

如果本地没有有效的 Cookie，脚本会生成一个二维码并通过飞书机器人发送消息提醒。使用哔哩哔哩 App 扫描二维码进行登录。

### 3. 监控动态

登录成功后，脚本会定期检查关注的 UP 主的动态，并在有新视频或文字动态发布时通过飞书机器人发送消息通知。

### 4. 查看日志

**Docker方式：**
```bash
docker-compose logs -f
```

**本地方式：**
```bash
# 实时查看输出
python bilibili_followed_dynamics.py
```

## 脚本说明

### 主要函数说明

#### 核心函数

| 函数名 | 功能描述 |
|--------|----------|
| `saveNprint_qr_image` | 生成并保存二维码图片，并在控制台打印二维码 |
| `send_feishu_card_error` | 发送飞书错误消息卡片 |
| `send_feishu_card` | 发送飞书视频更新消息卡片 |
| `job` | 定时任务函数，定期运行监控任务 |

#### session_cookie 类

处理登录、Cookie 管理和动态数据比较的核心类。

| 方法名 | 功能描述 |
|--------|----------|
| `dict_cookie_to_header` | 将字典形式的 Cookie 转换为请求头中的 Cookie 字符串 |
| `load_cookies` | 加载本地 Cookie 文件 |
| `cookie_valid` | 验证 Cookie 的有效性 |
| `save_cookies` | 保存当前会话的 Cookie 到本地文件 |
| `getQrCode` | 生成并显示登录二维码 |
| `ensure_login` | 确保用户已登录，如果 Cookie 无效则进行扫码登录 |
| `_wait_for_qr_login` | 等待用户扫码登录 |
| `compare_and_run` | 比较当前动态数据和本地数据，判断是否有更新 |
| `get_followed_dynamic` | 获取关注的 UP 主的动态，识别新视频并发送消息通知 |

### 定时任务

脚本使用 `schedule` 库实现定时任务，每次运行后会随机等待 1 - 3 分钟后再次运行。

### 使用建议

#### 🎯 最佳实践
1. **合理设置检查间隔**：建议设置为3-5分钟，避免过于频繁的请求
2. **监控日志输出**：定期检查日志，确保脚本正常运行
3. **网络环境稳定**：使用稳定的网络环境，避免因网络问题导致监控中断
4. **及时更新配置**：如Webhook地址变更，及时更新配置文件

#### ⚡ 性能优化
- 脚本采用智能缓存机制，避免重复数据获取
- 支持断点续传，异常恢复后自动继续监控
- 内存使用优化，长时间运行不会造成内存泄漏

#### 🔒 安全提示
- 妥善保管配置文件，避免泄露Webhook地址
- 定期检查和更新Cookie，确保登录状态有效
- 建议在可信环境中运行脚本

## 常见问题与故障排除

### 🔧 配置相关问题

**Q: 配置文件无法保存或读取？**
A: 确保脚本运行目录有读写权限，检查config.json文件是否存在且格式正确。

**Q: 飞书消息发送失败？**
A: 检查以下几点：
- Webhook地址是否正确且完整
- 飞书机器人是否被移除或禁用
- 网络连接是否正常

### 🔐 登录相关问题

**Q: 二维码无法显示或扫描失败？**
A: 尝试以下解决方案：
- 确保终端支持显示二维码
- 检查网络连接是否正常
- 删除cookie文件后重新登录
- 手动打开生成的二维码图片文件

**Q: 登录后Cookie很快失效？**
A: 这是正常现象，B站Cookie有效期较短。脚本会自动处理重新登录。

### 🐳 Docker相关问题

**Q: Docker容器无法启动？**
A: 检查以下项：
- Docker和Docker Compose是否正确安装
- 配置文件路径是否正确挂载
- 端口是否被占用

**Q: 容器日志显示权限错误？**
A: 确保宿主机上的配置文件有正确的读写权限。

### 📊 监控相关问题

**Q: 没有收到新视频通知？**
A: 可能原因：
- 检查配置文件中`followed_dynamic_types`是否包含`DYNAMIC_TYPE_AV`
- 确认确实有待监控的UP主发布了新视频
- 检查日志是否有错误信息

**Q: 监控间隔时间如何调整？**
A: 修改配置文件中的`check_interval_minutes`值，建议设置为1-5分钟。

## 注意事项

*   **Webhook有效性**: 请确保飞书 Webhook 地址的有效性，否则消息推送将失败。
*   **文件权限**: 脚本运行时需要有足够的权限来读写配置文件和临时文件。
*   **二维码有效期**: 如果二维码过期或失效，请重新运行脚本。
*   **网络稳定性**: 建议使用稳定的网络环境，避免因网络问题导致监控中断。
 *   **Cookie管理**: 脚本会自动管理Cookie，无需手动干预，但建议定期检查和更新。

## 更新日志

### v1.0.0 (2024-01-XX)
- ✨ 初始版本发布
- 🐳 支持Docker容器化部署
- 📱 支持扫码登录和Cookie自动管理
- 🔔 支持飞书消息推送
- ⚙️ 支持灵活的配置选项
