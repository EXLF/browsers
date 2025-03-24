# Chrome多实例快捷方式管理器

一个用于管理多个Chrome浏览器实例的桌面应用程序，使用PyQt6开发。

## 功能特点

- 创建和管理多个独立的Chrome浏览器实例
- 每个实例拥有独立的用户数据目录，互不干扰
- 账号管理功能，记录每个实例对应的钱包地址和社交媒体账号
- 脚本插件功能，管理和下载各种浏览器脚本和插件工具
- 现代化UI界面，支持高DPI显示
- 自动保存配置，下次启动时自动加载
- 支持自定义Chrome路径和数据根目录
- 完美支持中文字体显示（使用微软雅黑UI字体）
- 多线程文件删除，保持UI响应性
- 高效的Chrome进程检查机制，优化删除操作性能

## 系统要求

- Windows 10/11 操作系统
- Python 3.8+
- PyQt6
- Google Chrome浏览器

## 安装方法

1. 克隆或下载本仓库
```bash
git clone https://github.com/yourusername/chrome-shortcut-manager.git
cd chrome-shortcut-manager
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行程序
```bash
python main.py
```

## 使用说明

### 首次使用

1. 启动程序后，点击"添加新实例"按钮
2. 输入实例名称和数据目录名
3. 确认创建后，新的Chrome实例将出现在主界面
4. 点击"启动"按钮即可打开对应的Chrome实例

### 账号管理

点击左侧菜单的"账号管理"选项，可以：

- 为每个Chrome实例记录关联的钱包地址
- 管理每个实例的社交媒体账号（Twitter、Discord、Telegram、Gmail）
- 添加备注信息
- 一键保存所有账号信息

### 脚本插件

点击左侧菜单的"脚本插件"选项，可以：

- 浏览热门脚本插件和工具类插件
- 查看插件详情和版本
- 提交自己的脚本插件

### 设置

点击左侧菜单的"设置"选项，可以配置：

- Chrome可执行文件路径
- 数据根目录（所有Chrome实例的数据将存储在此目录下的子文件夹中）
- 快捷方式保存路径

## 技术实现

- 使用PyQt6构建现代化UI界面
- 采用模块化设计，代码结构清晰
- 全局应用微软雅黑UI字体，提供更好的中文显示效果
- 使用SQLite数据库保存配置信息和Chrome实例数据
- 多线程实现文件系统操作，保持UI响应性
- 使用QTimer进行非阻塞批量删除操作
- Chrome进程检查缓存机制，减少重复进程检查

## 最近更新

### V1.2 更新内容

- 移除性能监控组件，减少系统资源占用
- 优化Chrome进程检查机制，添加进程缓存减少重复检查
- 修复批量删除操作中的变量命名问题
- 修复线程调度与UI更新的问题
- 提高删除操作的响应速度

### V1.1 更新内容

- 重构UI代码，采用模块化页面设计
- 将主窗口代码拆分为独立页面模块
- 优化文件删除操作，使用后台线程避免UI卡顿
- 改进批量删除功能，通过计时器确保UI响应性
- 修复SQLite数据库多线程访问问题
- 优化大量文件删除操作的性能
- 增强错误处理和用户体验

## 脚本插件安全机制

为确保脚本插件的安全性和完整性，系统采用了以下安全措施：

### 下载链接安全性
- 强制使用HTTPS协议
- 域名白名单验证，仅允许从可信来源下载
- 支持的下载平台：
  - GitHub
  - 蓝奏云 (lanzou.com/lanzoux.com/lanzout.com)
  - 阿里云盘
  - 百度网盘

### RSA签名验证
- 使用非对称加密验证脚本元数据完整性
- 防止脚本信息被恶意篡改
- 确保脚本来源可信

### 自动更新机制
- 启动时自动检查脚本更新
- 每5分钟自动检查一次更新
- 支持手动检查更新
- 显示详细的更新状态信息

## 开发者信息

如果您想参与开发或修改代码，项目结构如下：

```
chrome-shortcut-manager/
├── main.py                  # 程序入口
├── chrome_manager/          # 主模块
│   ├── __init__.py
│   ├── constants.py         # 全局常量定义
│   ├── config.py            # 配置管理
│   ├── main_window.py       # 主窗口
│   ├── shortcuts.py         # 快捷方式管理
│   ├── utils.py             # 工具函数
│   └── ui/                  # UI组件
│       ├── __init__.py
│       ├── cards.py         # 卡片组件
│       ├── components.py    # 基础组件
│       ├── dialogs.py       # 对话框
│       ├── message.py       # 消息提示
│       └── pages/           # 页面模块
│           ├── __init__.py
│           ├── home_page.py    # 主页模块
│           ├── account_page.py # 账号管理页面
│           ├── script_page.py  # 脚本插件页面
│           └── settings_page.py # 设置页面
```

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交Issue或Pull Request，或加入Discord社区：https://discord.gg/cTZCaYefPY 