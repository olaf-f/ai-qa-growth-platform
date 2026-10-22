# AI QA Growth Platform

**中文名称：AI测试成长平台**  
**建议 Git 仓库名：`ai-qa-growth-platform`**

面向传统测试工程师向 AI 质量工程转型的本地学习平台，贯通能力诊断、课程训练、项目实战、知识管理和求职准备。

## 主要功能

- 能力诊断、分级学习路径、行业知识与阶段测验。
- RAG评测实战、作业点评、版本记录和作品集。
- 本地学习知识库、学习待办与每日进度记录。
- 简历Word/PDF导入、DeepSeek诊断、优化与帮写。
- 广州招聘需求、来源核验及岗位技能学习联动。

## 本地运行

需要 Python 3.10 或以上。在本项目目录安装依赖并启动：

```sh
python -m pip install -r requirements.txt
python server.py
```

浏览器访问 http://127.0.0.1:8765/ 。Windows也可双击 `启动平台.cmd`。

在线模型功能可通过 `配置DeepSeek.cmd` 配置；其他使用说明见 [开始使用.md](开始使用.md)。

## 上传 Git

将本目录作为仓库根目录，仓库名使用 `ai-qa-growth-platform`。

`.gitignore` 已排除本地模型配置 `config.local.json`、学习数据库目录 `.learning-data/` 和Python缓存。提交前检查待提交文件，避免包含个人简历、学习备份或其他私人资料。

招聘快照包含来源与核对日期，页面可见不保证仍有招聘名额。每天检查招聘信息的安排属于当前电脑的Codex任务，克隆仓库不会自动创建该任务。
