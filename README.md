# Chrome多实例快捷方式管理器

一个基于PyQt6开发的Chrome浏览器多实例管理工具，支持创建和管理多个Chrome用户配置文件。

## 功能特点

- 现代化UI界面设计
- 支持创建多个Chrome实例快捷方式
- 自动保存和加载配置
- 支持自定义Chrome路径和数据根目录
- 快速启动不同的Chrome实例
- 桌面快捷方式自动创建

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
python chrome_shortcut_manager.py
```

2. 首次运行时，在"设置"中配置：
   - Chrome可执行文件路径
   - 数据根目录（用于存储不同实例的配置文件）

3. 在主界面点击"添加新实例"创建新的Chrome实例：
   - 输入实例名称
   - 输入数据目录名
   - 确认创建

4. 通过桌面快捷方式或程序界面启动Chrome实例

## 配置文件

配置文件保存在：`%APPDATA%\ChromeShortcuts\config.json`

## 许可证

MIT License 