# CSMAR机构账号配置指南

## 目录
1. [机构账号访问方式](#机构账号访问方式)
2. [配置步骤](#配置步骤)
3. [Python SDK安装](#python-sdk安装)
4. [环境变量配置](#环境变量配置)
5. [常见问题](#常见问题)
6. [技术支持](#技术支持)

## 机构账号访问方式

作为中南财经政法大学的用户，您可能有以下几种访问方式：

### 方式1：IP认证访问（推荐优先尝试）
- **条件**：在校内IP范围内访问
- **特点**：无需用户名密码，自动识别机构权限
- **适用场景**：校园网络内访问

### 方式2：个人子账号
- **条件**：在CSMAR网站注册个人账号，绑定机构权限
- **特点**：需要用户名/密码，可在校外访问
- **获取方式**：
  1. 访问 [us.gtadata.com](https://us.gtadata.com)
  2. 使用机构邮箱注册个人账号
  3. 联系图书馆管理员或CSMAR技术支持绑定机构权限

### 方式3：统一机构账号
- **条件**：部分机构有统一的机构账号
- **特点**：全校共享的账号，可能有并发限制
- **获取方式**：联系学校图书馆或CSMAR负责人

## 配置步骤

### 步骤1：确定您的访问方式

测试CSMAR连接：
```bash
cd /path/to/csmar-mcp-server
echo '{"action":"check_availability","params":{}}' | python src/python_client.py
```

### 步骤2：配置环境文件

根据诊断结果，创建或编辑 `.env` 文件：

#### 情况A：IP认证可用
```bash
cd /path/to/csmar-mcp-server
cp .env.example .env
# 编辑.env文件，留空用户名和密码
CSMAR_USERNAME=
CSMAR_PASSWORD=
CSMAR_LANG=0
```

#### 情况B：使用个人账号
```bash
cd /path/to/csmar-mcp-server
cp .env.example .env
# 编辑.env文件，填入您的凭据
CSMAR_USERNAME=您的个人账号
CSMAR_PASSWORD=您的密码
CSMAR_LANG=0  # 0=中文，1=英文
```

### 步骤3：测试配置

重启Claude Code后测试MCP工具：

```python
# 测试登录状态
mcp__csmar__csmar_login(
    account="您的账号",  # 如果不配置环境变量，手动登录
    pwd="您的密码",
    lang="0"
)

# 列出可用数据库（如果自动登录成功）
mcp__csmar__csmar_list_databases()

# 查看具体数据库的表
mcp__csmar__csmar_list_tables(database_name="财务报表")
```

## Python SDK安装

### 获取CSMAR-PYTHON SDK
1. **校内访问**：联系学校图书馆获取SDK安装包
2. **校外访问**：访问CSMAR技术支持获取

### 安装步骤
```bash
# 1. 解压SDK到Python的site-packages目录
#    例如: C:\Program Files\Python39\Lib\site-packages\csmarapi\

# 2. 安装依赖
pip install urllib3 websocket websocket_client pandas prettytable

# 3. 验证安装
python -c "from csmarapi.CsmarService import CsmarService; print('SDK导入成功')"
```

## 环境变量配置

### 项目配置文件位置
```
csmar-mcp-server/.env
```

### 完整配置示例
```env
# ==================== Python SDK配置 ====================
# 方式1：IP认证（留空）
CSMAR_USERNAME=
CSMAR_PASSWORD=

# 方式2：个人账号
# CSMAR_USERNAME=your_username
# CSMAR_PASSWORD=your_password

CSMAR_LANG=0  # 语言：0=中文，1=英文

# ==================== HTTP API配置（备用） ====================
CSMAR_API_BASE=https://api.gtarsc.com
CSMAR_API_KEY=your_api_key_if_available

# ==================== 服务器设置 ====================
PORT=3001
LOG_LEVEL=info
TIMEOUT=30000
MAX_RETRIES=3
```

### MCP服务器配置（.mcp.json）
确保环境变量正确传递：
```json
{
  "mcpServers": {
    "csmar": {
      "command": "node",
      "args": ["/path/to/csmar-mcp-server/src/index.js"],
      "env": {
        "CSMAR_USERNAME": "您的账号",
        "CSMAR_PASSWORD": "您的密码",
        "CSMAR_LANG": "0"
      }
    }
  }
}
```

## 常见问题

### Q1：如何知道使用哪种访问方式？
A：使用测试命令：`echo '{"action":"check_availability","params":{}}' | python src/python_client.py`，检查CSMAR SDK和登录状态。

### Q2：在校外如何使用机构权限？
A：需要获取个人子账号并绑定机构权限，或使用VPN连接到校内网络。

### Q3：提示"SDK未安装"怎么办？
A：
1. 确认已从机构获取CSMAR-PYTHON SDK
2. 检查SDK是否解压到正确的site-packages目录
3. 运行 `pip list | findstr csmarapi` 检查是否安装

### Q4：登录失败怎么办？
A：
1. 确认用户名/密码正确
2. 检查账号是否绑定机构权限
3. 尝试在浏览器登录 [us.gtadata.com](https://us.gtadata.com) 验证账号
4. 联系CSMAR技术支持

### Q5：如何获取更多的数据库访问权限？
A：联系图书馆管理员或CSMAR技术支持申请特定数据库的访问权限。

## 技术支持

### 校内支持
- **图书馆技术支持**：中南财经政法大学图书馆数字资源部
- **联系方式**：查询学校图书馆网站
- **服务内容**：数据库访问、账号问题、SDK获取

### CSMAR官方支持
- **技术支持邮箱**：service@gtadata.com
- **官方网站**：[us.gtadata.com](https://us.gtadata.com)
- **服务热线**：400-888-3636

### 项目技术支持
- **MCP服务器问题**：查看 `src/` 目录下的日志
- **Python客户端问题**：运行 `src/python_client.py` 测试
- **配置问题**：检查 `.env` 和 `config/.mcp.json` 文件

## 快速开始检查清单

- [ ] 1. 获取CSMAR-PYTHON SDK安装包
- [ ] 2. 安装SDK到Python site-packages目录
- [ ] 3. 安装依赖包：`pip install urllib3 websocket websocket_client pandas prettytable`
- [ ] 4. 测试连接：`echo '{"action":"check_availability","params":{}}' | python src/python_client.py`
- [ ] 5. 根据诊断结果创建 `.env` 文件
- [ ] 6. 重启Claude Code测试MCP工具
- [ ] 7. 验证数据访问：`mcp__csmar__csmar_list_databases()`

## 高级配置

### 使用多个账号
如果需要切换多个账号，可以创建不同的环境文件：

```bash
# 创建不同环境的配置文件
cp .env .env.campus    # 校内IP认证
cp .env .env.remote    # 校外个人账号

# 启动时指定环境文件
CSMAR_USERNAME=your_name CSMAR_PASSWORD=your_pwd node index.js
```

### 自动化测试
```python
# 自动化测试脚本
import subprocess
import json

def test_csmar_connection():
    cmd = 'echo \'{"action":"check_availability","params":{}}\' | python python_client.py'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return data.get("success", False) and data.get("csmar_available", False)
```

### 日志配置
在 `.env` 中调整日志级别：
```env
LOG_LEVEL=debug  # 更详细的日志，便于调试
```

---

**最后更新**：2026-04-06  
**适用版本**：CSMAR-PYTHON SDK v1.0+  
**适用机构**：中南财经政法大学  
**项目路径**：`csmar-mcp-server/`