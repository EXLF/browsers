import os
import sqlite3
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class DatabaseManager:
    def __init__(self, app_data_path):
        # 确保目录存在
        os.makedirs(app_data_path, exist_ok=True)
        
        # 数据库路径
        self.db_path = os.path.join(app_data_path, "chrome_manager.db")
        
        # 初始化加密
        self._init_encryption(app_data_path)
        
        # 连接数据库
        self.conn = sqlite3.connect(self.db_path)
        
        # 启用外键约束
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        # 创建表结构
        self._create_tables()
    
    def _init_encryption(self, app_data_path):
        """初始化加密系统"""
        key_path = os.path.join(app_data_path, "encryption.key")
        
        # 生成或读取密钥
        if not os.path.exists(key_path):
            # 生成一个安全的密钥
            salt = os.urandom(16)
            password = base64.urlsafe_b64encode(os.urandom(32))  # 随机生成密码
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            
            # 保存盐值和密钥
            with open(key_path, "wb") as f:
                f.write(salt + b"\n" + key)
        else:
            # 读取现有密钥
            with open(key_path, "rb") as f:
                content = f.read().split(b"\n")
                salt = content[0]
                key = content[1]
        
        # 初始化加密器
        self.encryptor = Fernet(key)
    
    def _create_tables(self):
        """创建数据库表结构"""
        cursor = self.conn.cursor()
        
        # 配置表 - 存储应用程序全局配置
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        )''')
        
        # Chrome实例表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chrome_instances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            data_dir TEXT,
            chrome_path TEXT
        )''')
        
        # 账号信息表 - 敏感字段将被加密
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS account_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instance_id INTEGER,
            wallet TEXT,            -- 加密
            twitter TEXT,           -- 加密
            discord TEXT,           -- 加密
            telegram TEXT,          -- 加密
            gmail TEXT,             -- 加密
            note TEXT,              -- 加密
            FOREIGN KEY (instance_id) REFERENCES chrome_instances(id) ON DELETE CASCADE
        )''')
        
        self.conn.commit()
    
    def _encrypt(self, value):
        """加密文本数据"""
        if value is None or value == "":
            return ""
        return self.encryptor.encrypt(value.encode()).decode()
    
    def _decrypt(self, encrypted_value):
        """解密文本数据"""
        if encrypted_value is None or encrypted_value == "":
            return ""
        try:
            return self.encryptor.decrypt(encrypted_value.encode()).decode()
        except Exception:
            return ""  # 解密失败时返回空字符串
    
    def save_config(self, config_dict):
        """保存全局配置"""
        cursor = self.conn.cursor()
        
        # 处理简单的键值对配置
        for key, value in config_dict.items():
            if key != "shortcuts" and key != "account_info":  # 这两项单独处理
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                cursor.execute(
                    "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                    (key, str(value))
                )
        
        self.conn.commit()
    
    def load_config(self):
        """加载全局配置"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT key, value FROM config")
            
            config = {}
            for key, value in cursor.fetchall():
                try:
                    # 尝试解析JSON，失败则保留原值
                    config[key] = json.loads(value)
                except:
                    config[key] = value
            
            # 加载Chrome实例列表
            try:
                config["shortcuts"] = self.get_all_chrome_instances()
            except Exception as e:
                print(f"加载Chrome实例列表时出错: {str(e)}")
                config["shortcuts"] = []
            
            # 加载账号信息
            try:
                config["account_info"] = self.get_all_account_info()
            except Exception as e:
                print(f"加载账号信息时出错: {str(e)}")
                config["account_info"] = {}
            
            return config
        except Exception as e:
            print(f"加载配置时出错: {str(e)}")
            # 返回一个空的配置字典
            return {}
    
    def clear_chrome_instances(self):
        """清空Chrome实例表"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM chrome_instances")
            self.conn.commit()
            print("已清空Chrome实例表")
        except Exception as e:
            print(f"清空Chrome实例表出错: {str(e)}")
            
    def save_chrome_instance(self, instance_data):
        """保存Chrome实例信息"""
        try:
            name = instance_data.get("name")
            data_dir = instance_data.get("data_dir")
            
            print(f"保存Chrome实例: 名称={name}, 数据目录={data_dir}")
            
            # 确保连接可用
            self._ensure_connection()
            
            cursor = self.conn.cursor()
            
            # 开始事务
            self.conn.execute("BEGIN TRANSACTION")
            
            # 检查是否已存在
            cursor.execute(
                "SELECT id FROM chrome_instances WHERE name = ?",
                (name,)
            )
            row = cursor.fetchone()
            
            if row:
                instance_id = row[0]
                print(f"更新现有实例, ID={instance_id}")
                # 更新现有记录
                cursor.execute(
                    """
                    UPDATE chrome_instances 
                    SET data_dir = ? 
                    WHERE id = ?
                    """,
                    (data_dir, instance_id)
                )
            else:
                print(f"插入新实例")
                # 插入新记录
                cursor.execute(
                    """
                    INSERT INTO chrome_instances (name, data_dir)
                    VALUES (?, ?)
                    """,
                    (name, data_dir)
                )
                instance_id = cursor.lastrowid
                print(f"插入新实例成功, ID={instance_id}")
            
            # 提交事务
            self.conn.commit()
            return instance_id
        except sqlite3.Error as e:
            # 回滚事务
            self.conn.rollback()
            print(f"数据库操作错误: {str(e)}")
            return None
        except Exception as e:
            # 回滚事务
            try:
                self.conn.rollback()
            except:
                pass
            print(f"保存Chrome实例出错: {str(e)}")
            return None
    
    def get_all_chrome_instances(self):
        """获取所有Chrome实例"""
        try:
            print(f"正在从数据库获取所有Chrome实例...")
            
            # 确保连接可用
            self._ensure_connection()
            
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT name, data_dir FROM chrome_instances
                """
            )
            
            instances = []
            for name, data_dir in cursor.fetchall():
                print(f"  找到实例: 名称={name}, 数据目录={data_dir}")
                instances.append({
                    "name": name,
                    "data_dir": data_dir
                })
            
            print(f"成功获取{len(instances)}个Chrome实例")
            return instances
        except sqlite3.Error as e:
            print(f"数据库操作错误: {str(e)}")
            return []
        except Exception as e:
            print(f"获取Chrome实例出错: {str(e)}")
            return []
    
    def delete_chrome_instance(self, name):
        """删除Chrome实例"""
        try:
            print(f"正在从数据库删除Chrome实例: {name}")
            cursor = self.conn.cursor()
            
            # 先获取实例ID
            cursor.execute(
                "SELECT id FROM chrome_instances WHERE name = ?",
                (name,)
            )
            row = cursor.fetchone()
            if not row:
                print(f"未找到要删除的实例: {name}")
                return False
                
            instance_id = row[0]
            print(f"找到要删除的实例ID: {instance_id}")
            
            # 删除关联的账号信息
            cursor.execute(
                "DELETE FROM account_info WHERE instance_id = ?",
                (instance_id,)
            )
            print(f"已删除实例关联的账号信息")
            
            # 删除实例
            cursor.execute(
                "DELETE FROM chrome_instances WHERE id = ?",
                (instance_id,)
            )
            print(f"已删除实例记录")
            
            self.conn.commit()
            print(f"成功从数据库删除Chrome实例: {name}")
            return True
        except Exception as e:
            print(f"删除Chrome实例出错: {str(e)}")
            return False
    
    def get_instance_id(self, name):
        """获取实例ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM chrome_instances WHERE name = ?", (name,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def save_account_info(self, instance_name, account_data):
        """保存账号信息"""
        instance_id = self.get_instance_id(instance_name)
        if not instance_id:
            # 实例不存在，静默返回False，不输出错误
            return False
        
        cursor = self.conn.cursor()
        
        # 先删除现有的账号信息
        cursor.execute("DELETE FROM account_info WHERE instance_id = ?", (instance_id,))
        
        # 插入新的账号信息（加密敏感字段）
        cursor.execute(
            """
            INSERT INTO account_info 
            (instance_id, wallet, twitter, discord, telegram, gmail, note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                instance_id,
                self._encrypt(account_data.get("wallet", "")),
                self._encrypt(account_data.get("twitter", "")),
                self._encrypt(account_data.get("discord", "")),
                self._encrypt(account_data.get("telegram", "")),
                self._encrypt(account_data.get("gmail", "")),
                self._encrypt(account_data.get("note", ""))
            )
        )
        
        self.conn.commit()
        return True
    
    def get_account_info(self, instance_name):
        """获取指定实例的账号信息"""
        instance_id = self.get_instance_id(instance_name)
        if not instance_id:
            return {}
        
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT wallet, twitter, discord, telegram, gmail, note
            FROM account_info
            WHERE instance_id = ?
            """,
            (instance_id,)
        )
        
        result = cursor.fetchone()
        if not result:
            return {}
        
        return {
            "wallet": self._decrypt(result[0]),
            "twitter": self._decrypt(result[1]),
            "discord": self._decrypt(result[2]),
            "telegram": self._decrypt(result[3]),
            "gmail": self._decrypt(result[4]),
            "note": self._decrypt(result[5])
        }
    
    def get_all_account_info(self):
        """获取所有实例的账号信息"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT c.name, a.wallet, a.twitter, a.discord, a.telegram, a.gmail, a.note
                FROM chrome_instances c
                LEFT JOIN account_info a ON c.id = a.instance_id
                """
            )
            
            all_accounts = {}
            for name, wallet, twitter, discord, telegram, gmail, note in cursor.fetchall():
                all_accounts[name] = {
                    "wallet": self._decrypt(wallet) if wallet else "",
                    "twitter": self._decrypt(twitter) if twitter else "",
                    "discord": self._decrypt(discord) if discord else "",
                    "telegram": self._decrypt(telegram) if telegram else "",
                    "gmail": self._decrypt(gmail) if gmail else "",
                    "note": self._decrypt(note) if note else ""
                }
            
            return all_accounts
        except Exception as e:
            # 如果发生错误（可能是表不存在或其他数据库错误），返回空字典
            print(f"获取账号信息时出错: {str(e)}")
            return {}
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def _ensure_connection(self):
        """确保数据库连接有效，如果连接丢失则重新连接"""
        try:
            # 执行一个简单查询测试连接是否有效
            self.conn.execute("SELECT 1")
        except (sqlite3.Error, AttributeError):
            # 如果连接无效，重新连接
            try:
                if hasattr(self, 'conn') and self.conn:
                    self.conn.close()
            except:
                pass
            
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA foreign_keys = ON")
            print("数据库连接已重新建立") 