# Vercel在线部署

导入GitHub仓库，Framework Preset选择Other。仓库中的vercel.json指定Python构建脚本与public输出目录。

- 课程、测验、RAG实战、简历编辑与招聘快照可在线访问。
- 待办与每日记录保存在访问者自己的浏览器中，可导入、导出备份；无跨设备自动同步。
- D盘私人学习资料、SQLite数据库、原有个人记录和本地模型配置不上传。
- Word/PDF在线解析上限4MB；文件会发送到Vercel函数处理，请先自行清除不希望上传的信息。
- 在线AI默认关闭。启用需在Vercel设置DEEPSEEK_API_KEY、DEEPSEEK_MODEL及TESTLAB_ACCESS_TOKEN；后者为单独的访问口令，用来限制公共站点消耗模型额度。勿把模型密钥填写在前端。口令只用于小范围个人访问，公开多人服务应另加用户登录、配额和审计。
- 招聘快照从GitHub部署版本读取；本地定时更新不会自动提交到GitHub，需要另行发布后才更新在线站点。

本地版继续通过server.py运行，不加载cloud.js。
