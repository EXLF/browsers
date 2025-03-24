"""
页面模块包，包含主窗口各个页面的实现
"""

from .home_page import HomePage
from .account_page import AccountPage
from .settings_page import SettingsPage 
from .script_page import ScriptPage

__all__ = ['HomePage', 'AccountPage', 'SettingsPage', 'ScriptPage'] 