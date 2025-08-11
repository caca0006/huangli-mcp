# Huangli MCP

`huangli-mcp` 是一个为 **Claude Desktop** 提供的 **Model Context Protocol (MCP)** 服务，用于生成中国黄历（农历）数据。  
支持返回公历/农历信息、宜忌事项、干支纪年、冲煞、吉神凶煞、黄道黑道、节气、月相等信息。  
基于 [lunar-python](https://github.com/6tail/lunar-python) 和 [fastmcp](https://pypi.org/project/fastmcp) 实现，完全离线运行。

---

## 功能特点

- **公历 / 农历信息**：日期、生肖、节气、月相、星期
- **干支纪年**：年、月、日（兼容无时柱的旧版 lunar-python）
- **黄历核心数据**：
  - 宜 / 忌
  - 冲煞信息
  - 彭祖百忌
  - 吉神 / 凶煞
  - 喜神 / 福神 / 财神方位
  - 黄道日 / 黑道日
- **离线运行**：无需联网，全部计算本地完成
- **多语言支持**：`lang=zh`（中文）、`lang=en`（部分英文）

---

## 环境要求

- **Python** >= 3.9（建议 3.10+）
- **操作系统**：Windows / macOS / Linux
- **Claude Desktop**（已开启 MCP 功能）

---

## 安装步骤

### 1. 获取项目代码

```powershell
git clone https://github.com/yourname/huangli-mcp.git
cd huangli-mcp
```

### 2. 创建虚拟环境

```powershell
python -m venv .venv
```

### 3. 激活虚拟环境

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

### 4. 安装依赖

由于部分系统环境无法直接安装 lunar-python 新版，这里使用兼容 1.4.x 的依赖：

```powershell
python -m pip install --upgrade pip
python -m pip install fastmcp pytz "lunar-python>=1.4.0,<1.5"
```

---

## 测试运行

在虚拟环境激活状态下运行：

```powershell
python .\server.py stdio
```

如果程序挂起等待（无报错立即退出），说明服务已启动成功。

---

## Claude Desktop 配置

编辑 **`%APPDATA%\Claude\claude_desktop_config.json`**（Windows）  
确保 JSON 格式合法（英文逗号，最后一项无多余逗号）。

### 推荐：使用虚拟环境 Python

```json
{
  "mcpServers": {
    "huangli": {
      "command": "C:\\huangli-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\huangli-mcp\\server.py",
        "stdio"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### 备用：使用 uv

```json
{
  "mcpServers": {
    "huangli": {
      "command": "uv.exe",
      "args": [
        "run",
        "C:\\huangli-mcp\\server.py",
        "stdio"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

---

## 使用方法

### Claude 中调用工具

在 Claude 对话框输入：

```json
{
  "tool_name": "get_huangli",
  "arguments": {
    "date": "2025-08-11",
    "tz": "Asia/Shanghai",
    "lang": "zh"
  }
}
```

### 返回示例

```json
{
  "date": {
    "gregorian": {
      "year": 2025,
      "month": 8,
      "day": 11,
      "weekday": "星期一"
    },
    "lunar": {
      "year": 2025,
      "month": 7,
      "day": 18,
      "monthName": "七月",
      "dayName": "十八",
      "zodiac": "巳"
    },
    "solarTerm": "",
    "moonPhase": "",
    "timezone": "Asia/Shanghai"
  },
  "stemsBranches": {
    "yearGZ": "乙巳",
    "monthGZ": "...",
    "dayGZ": "...",
    "timeGZ": "",
    "nayin": {
      "year": "...",
      "month": "...",
      "day": "...",
      "time": ""
    }
  },
  "almanac": {
    "yi": ["嫁娶", "开市"],
    "ji": ["..."],
    "dayTianShen": "...",
    "huangDaoOrHeiDao": "黄道日",
    "chong": {
      "animal": "猴",
      "desc": "冲猴(庚申)"
    },
    "sha": "煞北",
    "pengzu": {
      "gan": "...",
      "zhi": "..."
    },
    "godsDirection": {
      "xi": "西南",
      "fu": "正北",
      "cai": "正东"
    },
    "stars": {
      "jiShen": ["月德", "天喜"],
      "xiongSha": ["五虚", "土府"]
    }
  }
}
```

---

## 常见问题

### 1. `ModuleNotFoundError`

依赖未安装，请先激活虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

然后安装：

```powershell
python -m pip install fastmcp pytz "lunar-python>=1.4.0,<1.5"
```

### 2. `Server disconnected`

- 确认 `python .\server.py stdio` 能在终端挂起运行
- Claude 配置使用虚拟环境 Python 路径
- 检查 `claude_desktop_config.json` 是否为合法 JSON

### 3. JSON 解析错误

- 使用英文标点
- 删除最后一项后的多余逗号

---

## License

MIT
