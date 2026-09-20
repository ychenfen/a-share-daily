# Contributing

感谢你愿意让 A-Share Pulse 更可靠。小而清晰、能验证的改动最容易被合并。

## 开始之前

1. 先搜索现有 Issues，避免重复工作。
2. 新数据源请说明公开文档、字段含义、更新时间和失败行为。
3. 新评分规则请同时说明正向、负向阈值和失效条件。
4. 不要提交 API Key、Cookie、Token 或其他凭据。

## 本地验证

项目只依赖 Python 标准库：

```bash
python3 scripts/scorecard.py
python3 scripts/chart.py
python3 scripts/build_site.py
python3 -m unittest discover -s tests -v
python3 scripts/validate.py
```

涉及页面时，请同时检查桌面和手机宽度。涉及 CSV/JSON 时，请保持字段向后兼容，
并在 `docs/DATA_SCHEMA.md` 中补充说明。

## 提交规范

使用 Conventional Commits：

- `feat(scope): ...` 新能力
- `fix(scope): ...` 错误修复
- `docs(scope): ...` 文档和社区内容
- `test(scope): ...` 测试改进

一个提交只解决一类问题。自动生成的数据应与生成它的代码变化放在同一提交中。

## 分析边界

本项目提供通用市场研究记录，不接受：

- 个性化投资建议；
- 收益承诺或夸张命中率；
- 没有来源和时间戳的新闻事实；
- 使用未来数据或事后筛选美化结果。

首次贡献可以从带有 `good first issue` 标签的任务开始。
