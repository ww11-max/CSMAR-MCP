#!/usr/bin/env python3
"""
CSMAR Python客户端 - 用于Node.js MCP服务器调用CSMAR-PYTHON SDK
通过标准输入接收JSON命令，标准输出返回JSON结果
"""

import sys
import json
import traceback
import logging
import os
from typing import Dict, Any, Optional

# ==================== 路径设置 ====================
# 设置Python路径以确保可以导入CSMAR SDK（使用测试成功的配置）
def setup_python_paths():
    """设置Python路径，使用测试成功的配置"""
    # 测试成功的路径配置
    d_site_packages = r"D:\python\Lib\site-packages"
    csmarapi_dir = os.path.join(d_site_packages, "csmarapi")

    new_paths = [
        r"C:\Users\29929\AppData\Roaming\Python\Python314\site-packages",
        r"C:\Python314\Lib\site-packages",
        d_site_packages,
        csmarapi_dir,
    ]

    # 只添加存在的路径，并保持顺序
    existing_paths = [p for p in new_paths if os.path.exists(p)]

    # 构建新的sys.path：现有路径 + 不在new_paths中的原始路径
    original_paths = [p for p in sys.path if p not in existing_paths]
    sys.path = existing_paths + original_paths

    return existing_paths

# 执行路径设置
added_paths = setup_python_paths()

# 配置日志（输出到stderr，避免干扰JSON输出）
logging.basicConfig(
    level=logging.INFO,  # 改为INFO级别，以便看到更多日志
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

if added_paths:
    logger.info(f"设置了以下路径到sys.path前面: {added_paths}")
    logger.info(f"当前sys.path前10个: {sys.path[:10]}")

# 尝试导入CSMAR SDK
CSMAR_AVAILABLE = False
CsmarService = None
ReportUtil = None

try:
    from csmarapi.CsmarService import CsmarService
    from csmarapi.ReportUtil import ReportUtil
    CSMAR_AVAILABLE = True
    logger.info("CSMAR SDK导入成功")
except ImportError as e:
    logger.error(f"无法导入CSMAR SDK: {e}")
    logger.error(f"当前sys.path: {sys.path}")
    logger.error("请确保已安装CSMAR-PYTHON SDK:")
    logger.error("1. 下载CSMAR-PYTHON压缩包")
    logger.error("2. 解压到Python的site-packages目录")
    logger.error("3. 安装依赖: pip install urllib3 websocket websocket_client pandas prettytable")

class CSMARClient:
    """CSMAR客户端，管理会话和请求"""

    def __init__(self):
        self.csmar = None
        self.logged_in = False
        self.username = None

        # 设置工作目录到项目根目录，确保能找到token.txt
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
            if os.path.exists(project_root):
                os.chdir(project_root)
                logger.info(f"设置工作目录到: {project_root}")

                # 检查token.txt是否存在
                token_path = os.path.join(project_root, "token.txt")
                if os.path.exists(token_path):
                    logger.info(f"找到token.txt: {token_path}")
                    # 如果token.txt存在，假设已登录
                    self.logged_in = True
                else:
                    logger.warning(f"未找到token.txt: {token_path}")
        except Exception as e:
            logger.error(f"设置工作目录失败: {e}")

    def _ensure_csmar(self):
        """确保csmar实例存在"""
        if not self.csmar:
            if not CSMAR_AVAILABLE:
                raise RuntimeError("CSMAR SDK未安装")
            self.csmar = CsmarService()
            logger.info("创建CsmarService实例")
        return self.csmar

    def login(self, account: str, pwd: str, lang: str = "0") -> Dict[str, Any]:
        """登录CSMAR账户"""
        try:
            if not CSMAR_AVAILABLE:
                return {
                    "success": False,
                    "error": "CSMAR SDK未安装",
                    "detail": "请安装CSMAR-PYTHON SDK"
                }

            self.csmar = CsmarService()
            # 根据lang参数转换
            lang_code = 0 if lang == "0" else 1
            result = self.csmar.login(account, pwd, lang_code)

            # 处理不同的返回结果类型
            if result is None:
                # SDK可能在登录成功时返回None，但实际已登录
                # 尝试获取数据库列表来验证登录状态
                try:
                    test_dbs = self.csmar.getListDbs()
                    if test_dbs is not None:
                        self.logged_in = True
                        self.username = account
                        return {
                            "success": True,
                            "message": "登录成功（SDK返回None，但验证通过）",
                            "username": account
                        }
                    else:
                        # 无法验证登录状态，返回失败
                        return {
                            "success": False,
                            "error": "登录验证失败",
                            "detail": "SDK返回None且无法获取数据库列表"
                        }
                except Exception as test_e:
                    # 验证失败
                    return {
                        "success": False,
                        "error": "登录验证异常",
                        "detail": f"验证时出错: {str(test_e)}"
                    }
            elif isinstance(result, dict):
                if result.get("success", False):
                    self.logged_in = True
                    self.username = account
                    return {
                        "success": True,
                        "message": "登录成功",
                        "username": account
                    }
                else:
                    return {
                        "success": False,
                        "error": "登录失败",
                        "detail": result.get("msg", str(result))
                    }
            else:
                # 其他类型的返回结果
                try:
                    # 尝试将结果转换为字符串进行检查
                    result_str = str(result)
                    if "success" in result_str.lower() or "true" in result_str.lower():
                        self.logged_in = True
                        self.username = account
                        return {
                            "success": True,
                            "message": f"登录成功（非标准返回: {result_str[:100]}）",
                            "username": account
                        }
                    else:
                        return {
                            "success": False,
                            "error": "登录失败",
                            "detail": result_str[:200]
                        }
                except:
                    return {
                        "success": False,
                        "error": "登录返回无法解析的结果",
                        "detail": f"类型: {type(result)}, 值: {result}"
                    }

        except Exception as e:
            return {
                "success": False,
                "error": f"登录异常: {str(e)}",
                "traceback": traceback.format_exc()
            }

    def get_list_dbs(self) -> Dict[str, Any]:
        """获取数据库列表"""
        try:
            csmar = self._ensure_csmar()

            # 尝试获取数据库列表
            databases = csmar.getListDbs()

            # 处理None结果
            if databases is None:
                return {
                    "success": False,
                    "error": "数据库列表为空，可能需要重新登录",
                    "databases": [],
                    "count": 0
                }

            # 尝试转换为列表格式
            if hasattr(databases, '__iter__'):
                db_list = list(databases)
            elif isinstance(databases, dict):
                db_list = list(databases.values())
            else:
                db_list = [str(databases)]

            return {
                "success": True,
                "databases": db_list,
                "count": len(db_list)
            }

        except Exception as e:
            error_msg = f"获取数据库列表失败: {str(e)}"
            return {
                "success": False,
                "error": error_msg,
                "traceback": traceback.format_exc()
            }

    def get_list_tables(self, database_name: str) -> Dict[str, Any]:
        """获取指定数据库的表列表"""
        try:
            logger.info(f"get_list_tables called with database_name: {repr(database_name)}")
            csmar = self._ensure_csmar()

            # 首先获取数据库列表，以获取实际的数据库名称
            try:
                databases = csmar.getListDbs()
                actual_db_name = None

                if databases:
                    # 遍历数据库，查找匹配的
                    for db in databases:
                        if isinstance(db, dict):
                            db_name_from_list = db.get('databaseName')
                            if db_name_from_list and db_name_from_list == database_name:
                                actual_db_name = db_name_from_list
                                break
                            # 也尝试模糊匹配（去除空格等）
                            if db_name_from_list and db_name_from_list.strip() == database_name.strip():
                                actual_db_name = db_name_from_list
                                break
                        elif str(db) == database_name:
                            actual_db_name = str(db)
                            break

                if actual_db_name:
                    logger.info(f"找到匹配的数据库名称: {repr(actual_db_name)}")
                    database_name = actual_db_name
                else:
                    logger.warning(f"未在数据库列表中找到精确匹配: {repr(database_name)}")
                    # 使用原始名称，但记录数据库列表供调试
                    if databases:
                        db_names = []
                        for db in list(databases)[:5]:
                            if isinstance(db, dict):
                                db_names.append(db.get('databaseName', str(db)))
                            else:
                                db_names.append(str(db))
                        logger.info(f"数据库列表前5个: {db_names}")
                        logger.info(f"数据库列表前5个(repr): {[repr(name) for name in db_names]}")

            except Exception as e:
                logger.warning(f"获取数据库列表失败，使用原始名称: {e}")

            # 使用确定的数据库名称获取表列表
            logger.info(f"调用getListTables with: {repr(database_name)}")
            tables = csmar.getListTables(database_name)

            # 处理None结果
            if tables is None:
                return {
                    "success": False,
                    "error": f"数据库 '{database_name}' 的表列表为空",
                    "database": database_name,
                    "tables": [],
                    "count": 0
                }

            # 尝试转换为列表格式
            if hasattr(tables, '__iter__'):
                table_list = list(tables)
            elif isinstance(tables, dict):
                table_list = list(tables.values())
            else:
                table_list = [str(tables)]

            return {
                "success": True,
                "database": database_name,
                "tables": table_list,
                "count": len(table_list)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"获取表列表失败: {str(e)}",
                "traceback": traceback.format_exc()
            }

    def get_list_fields(self, table_name: str) -> Dict[str, Any]:
        """获取指定表的字段列表"""
        try:
            csmar = self._ensure_csmar()

            fields = csmar.getListFields(table_name)

            # 处理None结果
            if fields is None:
                return {
                    "success": False,
                    "error": f"表 '{table_name}' 的字段列表为空",
                    "table": table_name,
                    "fields": [],
                    "count": 0
                }

            # 尝试转换为列表格式
            if hasattr(fields, '__iter__'):
                field_list = list(fields)
            elif isinstance(fields, dict):
                field_list = list(fields.values())
            else:
                field_list = [str(fields)]

            return {
                "success": True,
                "table": table_name,
                "fields": field_list,
                "count": len(field_list)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"获取字段列表失败: {str(e)}",
                "traceback": traceback.format_exc()
            }

    def query_count(self, columns: list, condition: str, table_name: str,
                   start_time: Optional[str] = None, end_time: Optional[str] = None) -> Dict[str, Any]:
        """查询记录数量"""
        try:
            csmar = self._ensure_csmar()

            count = csmar.queryCount(columns, condition, table_name, start_time, end_time)

            return {
                "success": True,
                "table": table_name,
                "condition": condition,
                "count": int(count) if count else 0
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"查询数量失败: {str(e)}",
                "traceback": traceback.format_exc()
            }

    def query(self, columns: list, condition: str, table_name: str,
             start_time: Optional[str] = None, end_time: Optional[str] = None,
             format: str = "json", limit: Optional[int] = None) -> Dict[str, Any]:
        """查询数据"""
        try:
            csmar = self._ensure_csmar()

            if format == "dataframe":
                # 返回DataFrame格式
                data = csmar.query_df(columns, condition, table_name, start_time, end_time)
                # 将DataFrame转换为字典列表
                if hasattr(data, 'to_dict'):
                    result = data.to_dict('records')
                else:
                    result = data
            else:
                # 返回JSON格式
                data = csmar.query(columns, condition, table_name, start_time, end_time)
                result = data

            # 处理None结果
            if result is None:
                return {
                    "success": True,
                    "table": table_name,
                    "data": [],
                    "count": 0,
                    "message": "查询结果为空"
                }

            # 应用限制
            if limit and isinstance(result, list):
                result = result[:limit]

            return {
                "success": True,
                "table": table_name,
                "data": result,
                "count": len(result) if isinstance(result, list) else 1
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"查询数据失败: {str(e)}",
                "traceback": traceback.format_exc()
            }

    def preview(self, table_name: str) -> Dict[str, Any]:
        """预览表数据"""
        try:
            csmar = self._ensure_csmar()

            data = csmar.preview(table_name)

            # 处理None结果
            if data is None:
                return {
                    "success": True,
                    "table": table_name,
                    "preview": [],
                    "message": "预览数据为空"
                }

            return {
                "success": True,
                "table": table_name,
                "preview": data
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"预览数据失败: {str(e)}",
                "traceback": traceback.format_exc()
            }

def main():
    """主函数：从标准输入读取JSON命令，执行并输出JSON结果"""
    client = CSMARClient()

    # 从标准输入读取JSON
    try:
        input_data = sys.stdin.read()
        command = json.loads(input_data)
    except json.JSONDecodeError as e:
        result = {
            "success": False,
            "error": f"JSON解析错误: {str(e)}",
            "input_received": input_data[:200] if input_data else "空输入"
        }
        print(json.dumps(result, ensure_ascii=False))
        return
    except Exception as e:
        result = {
            "success": False,
            "error": f"输入读取错误: {str(e)}"
        }
        print(json.dumps(result, ensure_ascii=False))
        return

    # 解析命令
    action = command.get("action")
    params = command.get("params", {})

    # 执行对应动作
    if action == "login":
        result = client.login(
            params.get("account"),
            params.get("pwd"),
            params.get("lang", "0")
        )
    elif action == "list_databases":
        result = client.get_list_dbs()
    elif action == "list_tables":
        result = client.get_list_tables(params.get("database_name"))
    elif action == "list_fields":
        result = client.get_list_fields(params.get("table_name"))
    elif action == "query_count":
        result = client.query_count(
            params.get("columns", []),
            params.get("condition", ""),
            params.get("table_name"),
            params.get("start_time"),
            params.get("end_time")
        )
    elif action == "query":
        result = client.query(
            params.get("columns", []),
            params.get("condition", ""),
            params.get("table_name"),
            params.get("start_time"),
            params.get("end_time"),
            params.get("format", "json"),
            params.get("limit")
        )
    elif action == "preview":
        result = client.preview(params.get("table_name"))
    elif action == "check_availability":
        result = {
            "success": True,
            "csmar_available": CSMAR_AVAILABLE,
            "client_logged_in": client.logged_in,
            "username": client.username
        }
    else:
        result = {
            "success": False,
            "error": f"未知动作: {action}",
            "supported_actions": [
                "login", "list_databases", "list_tables", "list_fields",
                "query_count", "query", "preview", "check_availability"
            ]
        }

    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()