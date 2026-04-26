# 贡献指南

欢迎把这个仓库继续补成更完整的计算机专业 Skills 地图。

## 可以贡献什么

- 新的 `SKILL.md`：例如课程实验、算法训练、云服务、AI Agent、论文精读、安全审计、移动开发等方向。
- 更好的分类与索引：让读者更容易找到自己需要的 skill。
- 使用案例：真实项目中如何组合多个 skills 完成任务。
- 安全修订：清理不该公开的 token、日志、个人路径或临时文件。
- 文档优化：让 README、学习路线和使用指南更容易被传播。

## 推荐的 Skill 结构

```text
skills/<skill-name>/
├── SKILL.md
├── scripts/        # 可选，放可复用脚本
├── references/     # 可选，放详细参考资料
├── templates/      # 可选，放模板文件
└── examples/       # 可选，放示例输入输出
```

## 写作建议

- 开头说明这个 skill 解决什么问题、何时触发。
- 给出最小可运行命令或使用步骤。
- 明确依赖的工具、环境变量和外部服务。
- 如果涉及付费 API、隐私数据或高风险操作，要写清楚边界。
- 尽量保留中文说明，必要时补英文关键词，方便搜索。

## 提交前检查

```bash
python3 scripts/build_docs.py
find skills -iname 'SKILL.md' | wc -l
```

不要提交：

- `.env`
- Token / API Key / Cookie
- 私钥、证书、数据库、日志文件
- 个人聊天记录或不可公开的项目内容

