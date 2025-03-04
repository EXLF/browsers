# Chrome多实例快捷方式管理器

一个用于管理多个Chrome浏览器实例的桌面应用程序，使用PyQt6开发。

## 功能特点

- 创建和管理多个独立的Chrome浏览器实例
- 每个实例拥有独立的用户数据目录，互不干扰
- 现代化UI界面，支持高DPI显示
- 自动保存配置，下次启动时自动加载
- 支持自定义Chrome路径和数据根目录
- 完美支持中文字体显示（使用微软雅黑UI字体）

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

### 设置

点击左侧菜单的"设置"选项，可以配置：

- Chrome可执行文件路径
- 数据根目录（所有Chrome实例的数据将存储在此目录下的子文件夹中）

## 技术实现

- 使用PyQt6构建现代化UI界面
- 采用模块化设计，代码结构清晰
- 全局应用微软雅黑UI字体，提供更好的中文显示效果
- 使用JSON文件保存配置信息

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
│       └── message.py       # 消息提示
```

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交Issue或Pull Request。 