# Bilibili 关注动态监控脚本

## 简介

本脚本用于监控哔哩哔哩（Bilibili）用户关注的 UP 主的动态，当有新视频发布时，会通过飞书机器人发送消息通知。脚本会自动处理登录、Cookie 管理和动态数据的比较，确保每次运行时能准确识别新视频。
> **本项目fork自 https://github.com/CserQin/bilibili-new-video-notifier 感谢CserQin的贡献！**

### 功能特点:

1.  **自动登录**：支持扫码登录，自动处理 Cookie 的保存和验证。
2.  **多类型监控**：支持监控视频、图文、转发等多种动态类型。
3.  **消息推送**：通过飞书机器人发送包含视频信息的卡片消息。
4.  **数据比较**：使用临时文件和本地文件比较，确保只推送新内容。
5. **Docker支持**：提供Docker容器化部署方案。
6. **灵活配置**：通过配置文件自定义监控类型和推送设置。
7. **MID过滤**：支持指定特定UP主进行监控，可配置关注列表。
8. **跨平台支持**：支持Windows、Linux、Mac等多平台运行。
9. **异常处理**：完善的错误处理和自动重试机制。
10. **一键部署**：提供自动化部署脚本，简化安装过程。

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
*   **Python版本**: Python 3.7 或更高版本
*   **操作系统**: Windows 10/11, Linux, macOS
*   **网络要求**: 能够访问B站API和飞书API
*   **依赖库**: 
  - `requests==2.31.0` - HTTP请求库
  - `qrcode==7.4.2` - 二维码生成库  
  - `schedule==1.2.0` - 定时任务库

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 配置文件

**创建方式：**
- **自动创建**：运行脚本自动生成
- **手动创建**：在项目根目录创建`config.json`（推荐）

**配置示例：**
```json
{
  "followed_dynamic_types": ["DYNAMIC_TYPE_AV", "DYNAMIC_TYPE_DRAW"],
  "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook地址",
  "check_interval_minutes": 3,
  "followed_mids": []
}
```

**配置说明：**

| 配置项 | 必填 | 说明              | 默认值 |
|--------|------|-----------------|--------|
| `feishu_webhook` | ✅ | 飞书机器人Webhook地址  | 无 |
| `followed_dynamic_types` | ❌ | 监控类型：见下方动态类型说明  | `["DYNAMIC_TYPE_AV", "DYNAMIC_TYPE_DRAW"]` |
| `check_interval_minutes` | ❌ | 检查间隔(分钟)        | `1` |
| `followed_mids` | ❌ | 指定UP主MID，留空监控所有 | `[]` |


**配置提示：**
- 修改配置后需重启脚本生效
- 配置文件需使用UTF-8编码

### 动态类型说明

- **DYNAMIC_TYPE_AV**: 视频动态 - 新视频发布时通知
- **DYNAMIC_TYPE_DRAW**: 图文动态 - 图文/文字更新时通知  
- **DYNAMIC_TYPE_FORWARD**: 转发动态 - 转发其他UP主时通知

**推荐组合：**
- 只关注视频：`["DYNAMIC_TYPE_AV"]`
- 视频+图文：`["DYNAMIC_TYPE_AV", "DYNAMIC_TYPE_DRAW"]` （默认）
- 全部监控：`["DYNAMIC_TYPE_AV", "DYNAMIC_TYPE_DRAW", "DYNAMIC_TYPE_FORWARD"]`

### MID过滤功能

指定UP主MID，只监控特定UP主：
```json
{"followed_mids": ["11111", "22222"]}
```

**获取MID方法：**
- 访问UP主主页：`https://space.bilibili.com/11111`
- URL中的数字就是MID（如`11111`）

**留空`[]`监控所有关注的UP主**

### 飞书Webhook获取

1. 飞书群聊 → 右上角"..." → "设置" → "群机器人"
2. "添加机器人" → "自定义机器人" → "添加"
3. 复制Webhook地址，填入配置文件

## 使用方法

### 首次使用流程

#### 1. 配置飞书Webhook
创建`config.json`，填入Webhook地址：
```json
{"feishu_webhook": "你的webhook地址"}
```

#### 2. 启动脚本

**Docker方式：**
```bash
# 一键部署（推荐）
bash docker-deploy.sh

# 或手动启动
docker-compose up -d
```

**本地方式：**
```bash
python bilibili_followed_dynamics.py
```

#### 3. 扫码登录

首次运行或Cookie失效时：
1. 脚本会生成登录二维码
2. 使用哔哩哔哩App扫描二维码
3. 登录成功后，Cookie会自动保存

#### 4. 监控运行

登录成功后，脚本会自动：
- 定期检查关注的UP主动态
- 识别新视频、图文、转发等内容
- 通过飞书机器人发送通知
- 记录运行日志便于排查问题

### 日常管理

#### 查看运行状态
**Docker方式：**
```bash
docker-compose logs -f    # 实时查看日志
docker-compose ps         # 查看服务状态
```

**本地方式：**
```bash
# 实时查看输出（按Ctrl+C停止）
python bilibili_followed_dynamics.py
```

#### 停止和重启
**Docker方式：**
```bash
docker-compose down       # 停止服务
docker-compose restart    # 重启服务
```

**本地方式：**
```bash
# 按Ctrl+C停止脚本运行
# 重新运行即可重启
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

脚本使用 `schedule` 库实现定时任务，支持自定义检查间隔。

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

**Q: 如何只监控特定的UP主？**
A: 在配置文件中设置`followed_mids`字段：
```json
"followed_mids": ["11111", "22222"]
```
留空或设置为`[]`表示监控所有关注的UP主。

**Q: 支持监控哪些类型的动态？**
A: 目前支持三种类型：
- `DYNAMIC_TYPE_AV`: 视频动态
- `DYNAMIC_TYPE_DRAW`: 图文/文字动态  
- `DYNAMIC_TYPE_FORWARD`: 转发动态

## 注意事项

*   **Webhook有效性**: 请确保飞书 Webhook 地址的有效性，否则消息推送将失败。
*   **文件权限**: 脚本运行时需要有足够的权限来读写配置文件和临时文件。
*   **二维码有效期**: 如果二维码过期或失效，请重新运行脚本。
*   **网络稳定性**: 建议使用稳定的网络环境，避免因网络问题导致监控中断。
 *   **Cookie管理**: 脚本会自动管理Cookie，无需手动干预，但建议定期检查和更新。

## 更新日志

### v1.1.0 (2024-02-XX)
- 🆕 新增MID过滤功能，支持指定特定UP主监控
- 🔄 新增转发动态监控支持（DYNAMIC_TYPE_FORWARD）
- 📋 完善配置文件说明和使用文档
- 🔧 优化Docker部署流程和脚本
- 🐛 修复已知问题和改进稳定性

### v1.0.0 (2024-01-XX)
- ✨ 初始版本发布
- 🐳 支持Docker容器化部署
- 📱 支持扫码登录和Cookie自动管理
- 🔔 支持飞书消息推送
- ⚙️ 支持灵活的配置选项
