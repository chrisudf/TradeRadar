# 纳斯达克100期权扫描器 — 自动运行配置说明

## 文件清单
- `nasdaq100_scanner.py`  — 主扫描脚本
- `nasdaq_scanner_task.xml` — Windows 任务计划配置
- `setup_instructions.md`  — 本说明文档

---

## 第一步：配置 Gmail 应用专用密码

> Gmail 不允许直接用登录密码，必须生成「应用专用密码」

1. 打开 https://myaccount.google.com/security
2. 确认已开启**两步验证**（没有则先开启）
3. 搜索「应用专用密码」或访问 https://myaccount.google.com/apppasswords
4. 点击「创建」→ 名称随意填（如 `nasdaq_scanner`）→ 点击「创建」
5. 复制生成的 **16位密码**（格式：`xxxx xxxx xxxx xxxx`）

---

## 第二步：修改脚本配置

打开 `nasdaq100_scanner.py`，找到顶部的邮件配置区域，填入你的信息：

```python
EMAIL_SENDER   = "your_email@gmail.com"      # 你的 Gmail 地址
EMAIL_PASSWORD = "xxxx xxxx xxxx xxxx"        # 上一步生成的16位应用专用密码
EMAIL_RECEIVER = "your_email@gmail.com"       # 接收通知的邮箱（可以是同一个）
```

---

## 第三步：确认 Python 路径

在命令提示符（CMD）中运行：
```
where python
```
记下输出的路径，例如：
```
C:\Users\张三\AppData\Local\Programs\Python\Python311\python.exe
```

---

## 第四步：安装依赖库（只需做一次）

```
pip install yfinance scipy numpy
```

---

## 第五步：配置 Windows 任务计划程序

### 方法一：导入 XML（推荐）

1. 用记事本打开 `nasdaq_scanner_task.xml`
2. 将 `<Command>` 和 `<Arguments>` 中的路径替换为你的实际路径：
   ```xml
   <Command>C:\Users\你的用户名\AppData\Local\Programs\Python\Python311\python.exe</Command>
   <Arguments>C:\路径\到\nasdaq100_scanner.py</Arguments>
   <WorkingDirectory>C:\路径\到\脚本所在文件夹\</WorkingDirectory>
   ```
3. 保存文件
4. 按 `Win + S` 搜索「任务计划程序」并打开
5. 右键「任务计划程序库」→「导入任务」→ 选择修改好的 XML 文件
6. 点击「确定」完成导入

### 方法二：手动创建

1. 打开「任务计划程序」
2. 右侧点击「创建基本任务」
3. 名称：`Nasdaq100Scanner`，点击下一步
4. 触发器：**每天**，时间设为 `03:00:00`（北京时间 / 澳洲时间 05:00），点击下一步
5. 操作：**启动程序**
   - 程序：填入 python.exe 完整路径
   - 参数：填入 `nasdaq100_scanner.py` 完整路径
   - 起始于：填入脚本所在文件夹路径
6. 点击完成

---

## 第六步：测试

### 手动测试脚本
在 CMD 中运行：
```
python C:\路径\到\nasdaq100_scanner.py
```
确认扫描正常、邮件能收到。

### 手动触发任务计划
在任务计划程序中找到 `Nasdaq100Scanner`，右键 → 「运行」，
观察脚本是否正常执行。

---

## 注意事项

| 问题 | 说明 |
|------|------|
| 电脑需开机 | 任务计划程序要求电脑在 03:00 时处于开机状态 |
| 已启用「开始时可用」 | 如果 03:00 时电脑关机，开机后会自动补跑 |
| 周末照常运行 | 美股周末休市，期权数据可能不全，邮件仍会发出但结果为空 |
| 每天都发邮件 | 无论有无满足条件，每天都会收到一封扫描报告 |

---

## 邮件说明

每天北京时间 03:00（澳洲时间 05:00）自动发送，主题格式为：
- `⚠️ IMPORTANT | 🟢 X只全满足 | 纳斯达克100期权扫描 YYYY-MM-DD`（有全满足时）
- `纳斯达克100期权扫描 YYYY-MM-DD | 今日无全满足`（无全满足时）

邮件内容包含：
- 当日三项条件通过统计
- 满足全部三项条件的股票表格（股价、IV30/RV30、TS斜率、预期波幅）
- 满足两项条件的股票分组表格（按三种组合分类）

---

*免责声明：仅供学习研究，不构成投资建议。*