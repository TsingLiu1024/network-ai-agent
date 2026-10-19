# 架构与失败处理

Client -> FastAPI admission/auth/body validation -> bounded diagnosis thread
  -> concurrent optional server network probes + Windows logs
  -> prepared RAG search (source/score/chunk)
  -> RepairAgent (one model call, typed JSON)
  -> SupervisorAgent (one model call, evidence-aware report)

所有 Agent 保留 AgentResult 结构；工具使用 ToolResult，不返回裸字典。
模型层只返回非空文本或抛出带稳定 code 的 LLMError。HTTP 错误、空响应、
格式错误都不会变成成功的分析文本。异常响应不包含上游正文、凭证、路径或
异常堆栈。每请求生成服务端 request_id，可关联简短的失败日志。

NetworkAgent 和 LogAgent 收集证据，不重复调用模型；RAGAgent 只检索。
RepairAgent 必须校验 reason/steps/commands 的结构，非法输出会导致该阶段
失败。Supervisor 说明事实、假设、缺失证据和检索来源。失败阶段仍保留在
响应中，partial 不能当成完整成功。所有推理输出都需要人工判断。

API health 路由异步响应，不被诊断线程阻塞；并发名额绑定真实线程任务，
客户端取消/超时后不会提早释放。任务达到总预算后不启动下一阶段。

RAG 磁盘格式是受限 JSON 文档和向量快照，CURRENT 指向内容寻址的完整一代，
写入后原子发布指针。构建/读取使用同一文件锁，校验文件哈希、文档数量、
尺寸、向量维度及有限值，再创建内存 FAISS 内积索引。向量归一化后分数为
余弦相似度。旧 pickle 文件不会被读取。知识变化或快照损坏时重建。
