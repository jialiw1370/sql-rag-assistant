# SQL RAG Assistant — SQL 学习助手

把《SQL Detective Cases: A Beginner's Guide to SQL for Kids》（2026，18 个原创案例）
做成一个能在线提问、在线做题的 RAG 学习助手。

用户问一个 SQL 问题（比如“JOIN 怎么写？”），先从 18 个案例里检索出最相关的
2–3 个案例，再用 LLM 结合案例生成解释和 SQL 例子。

## 现在的状态

Day 1：只有项目架子，还没有接口和页面。

- [ ] Day 2：`schema.sql` + 前 3 个案例进 SQLite
- [ ] Day 3：FastAPI `GET /` 和 `GET /cases`
- [ ] Day 4：`GET /cases/{id}` + 最简单的 SQL 判题
- [ ] Day 5：最简单的 HTML 页面
- [ ] Day 6：案例加到 8 个 + 第 1 个 pytest
- [ ] Day 7：README 写清楚怎么运行

之后（第 5–10 周）：18 个案例建成知识库（Chroma 向量数据库），接 LLM 做 RAG 回答，
再加 10 道测试题的人工评估，写进 README。

## 怎么运行

Day 1 还跑不起来。Day 3 之后：

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

然后在浏览器打开 http://127.0.0.1:8000/cases

## 技术栈（计划）

- Python + FastAPI + SQLite
- RAG：Chroma + LLM API（第 5 周起）
- 测试：pytest
- 前端：HTML（正在学习）
