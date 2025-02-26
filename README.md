# Chrome多实例快捷方式管理器

一个基于PyQt6开发的Chrome浏览器多实例管理工具，支持创建和管理多个Chrome用户配置文件。

## 功能特点

- 现代化UI界面设计
- 支持创建多个Chrome实例快捷方式
- 自动保存和加载配置
- 支持自定义Chrome路径和数据根目录
- 快速启动不同的Chrome实例
- 桌面快捷方式自动创建
- 模块化代码结构，易于维护和扩展

## 系统要求

- Windows操作系统
- Python 3.8+
- PyQt6
- pywin32

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行程序：
```bash
python main.py
```

2. 首次运行时，在"设置"中配置：
   - Chrome可执行文件路径
   - 数据根目录（用于存储不同实例的配置文件）

3. 在主界面点击"添加新实例"创建新的Chrome实例：
   - 输入实例名称
   - 输入数据目录名
   - 确认创建

4. 通过桌面快捷方式或程序界面启动Chrome实例

## 项目结构

项目采用模块化结构，便于维护和扩展：

```
.
├── main.py                     # 主程序入口
├── chrome_manager/             # 主包
│   ├── __init__.py             # 包初始化文件
│   ├── constants.py            # 全局常量
│   ├── utils.py                # 工具函数
│   ├── config.py               # 配置管理
│   ├── shortcuts.py            # 快捷方式管理
│   ├── main_window.py          # 主窗口类
│   └── ui/                     # UI子包
│       ├── __init__.py         # UI子包初始化
│       ├── components.py       # 基础UI组件
│       ├── cards.py            # 卡片组件
│       ├── dialogs.py          # 对话框组件
│       └── message.py          # 消息对话框工具
```

## 模块说明

- **main.py**: 程序入口点，负责应用程序的初始化和启动
- **constants.py**: 全局常量定义，如颜色、字体等
- **utils.py**: 工具函数，如字体加载等实用功能
- **config.py**: 配置管理模块，负责配置的加载和保存
- **shortcuts.py**: 快捷方式管理模块，处理Chrome快捷方式的创建和管理
- **main_window.py**: 主窗口类，整合所有功能模块
- **ui/components.py**: 基础UI组件，如按钮、输入框等
- **ui/cards.py**: 卡片UI组件，如浏览器实例卡片
- **ui/dialogs.py**: 对话框组件，如添加快捷方式对话框、设置对话框等
- **ui/message.py**: 消息对话框工具类，统一处理各种消息提示

## 配置文件

配置文件保存在：`%APPDATA%\ChromeShortcuts\config.json`

## 许可证

MIT License 