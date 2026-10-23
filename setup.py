import getpass
import json
from pathlib import Path

root = Path(__file__).resolve().parent
print('配置DeepSeek：密钥仅写入本机config.local.json，不进入浏览器和学习备份。')
print('请勿将包含密钥的配置文件发给他人。')
key = getpass.getpass('输入DeepSeek API密钥（输入不显示）：').strip()
if not key:
    print('未输入密钥，配置未修改。')
else:
    model = input('模型名称（回车默认deepseek-flash）：').strip() or 'deepseek-flash'
    p = root / 'config.local.json'
    tmp = root / 'config.local.json.tmp'
    tmp.write_text(json.dumps({'DEEPSEEK_API_KEY': key, 'DEEPSEEK_MODEL': model}, indent=2), encoding='utf-8')
    tmp.replace(p)
    print('配置已保存。回到平台设置页点击“重新检查连接配置”。')
input('按回车退出…')
