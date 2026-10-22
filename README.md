# Network AI Agent

基于 FastAPI 的网络排障助手：读取可选的服务器检测证据，检索知识库，
生成经过结构校验的修复建议与诊断报告。支持 Ollama、DeepSeek、OpenAI，
提供不联网的 demo 模式。

**当前边界：只生成修复建议，诊断 API 不执行修复命令。检测对象是运行 API
的主机或容器，不是浏览器客户端的设备。没有测量结果时报告必须说明证据不足。**

## 快速开始

需要 Python 3.12 或 3.13。Windows 和 Linux 均可运行；Windows 事件日志只在
Windows 主机上提供。macOS 可使用模型建议，网络探测尚未完整验证。

```bash
git clone https://github.com/TsingLiu1024/network-ai-agent.git
cd network-ai-agent
python -m venv .venv
```

Windows PowerShell：` .venv\Scripts\Activate.ps1 `
Linux/macOS：`source .venv/bin/activate`

```bash
python -m pip install --require-hashes -r requirements.lock
```

复制 `.env.example` 为 `.env`，设置模型与凭证。默认 Ollama：

```dotenv
MODEL_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:7b
```

先用 Ollama 拉取配置的模型。然后启动：

```bash
ollama pull deepseek-r1:7b
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

API 文档：[Swagger UI](http://127.0.0.1:8000/docs)。
`/health` 是存活检查；`/ready` 返回初始化状态及 RAG 是否降级，
不代表外部模型当前可用。

### 完全离线演示

仅安装 `requirements-core.txt` 即可。设置：

```dotenv
MODEL_PROVIDER=demo
ENABLE_RAG=false
COLLECT_LOCAL_EVIDENCE=false
```

demo 返回明确标识的演示文本，不进行模型推理或真实诊断。

## 请求与结果

```bash
curl -X POST http://127.0.0.1:8000/api/v1/diagnose -H "Content-Type: application/json" -d '{"question":"Windows DNS 解析失败"}'
```

配置 `API_KEY` 后，增加 `X-API-Key` 请求头。问题限 1–2000 字符，请求体
限 16000 字节。旧的 `/diagnose` 路径和 `problem` 字段作为兼容入口保留；
新代码应使用 `/api/v1/diagnose` 与 `question`。

响应含 `request_id`、`status` 和 `result.stages`。每阶段都有
`success/data/message/metadata`：

| status | success | 含义 |
| --- | --- | --- |
| success | true | 必需推理及实际检测成功 |
| partial | false | 有可用建议，但检测缺失或某阶段降级 |
| failed | false | 最终诊断生成失败，HTTP 502 |
| demo | true | 明确标识的离线演示结果 |

容量用尽返回 503 与 Retry-After，超时返回 504，输入不合法返回 422。
修复建议包含结构化 reason、steps、commands；命令带适用平台、权限、风险及
验证方法，`execution_enabled` 始终为 false。JSON 校验保证结构，不保证模型
建议在你的环境中正确；执行前必须结合现场证据人工审查。

## 本机检测与日志隐私

默认不读取服务器日志或进行服务器网络探测。需要诊断部署主机时设置：

```dotenv
COLLECT_LOCAL_EVIDENCE=true
```

使用云端模型还需要 `ALLOW_CLOUD_LOG_UPLOAD=true`，才会采集并发送本机证据。
日志可能包含主机名、路径和业务信息；凭证模式会作尽力脱敏，不能保证覆盖所有
敏感字段。只为可信用户开放带检测权限的 API。

网络探测是到 `1.1.1.1` 的一次 ping 和对 `github.com` 的 DNS 查询，
两者失败不等于整个网络不可用。Linux 需要 `ping`、`nslookup` 命令。
Windows 采集最近 20 条 System 警告/错误事件，权限不足会明确降级。
容器内探测只代表容器；不提供容器到 Windows 宿主事件日志的访问。

## RAG 知识库

支持 `KNOWLEDGE_PATH` 下的 UTF-8 `.txt/.md`。默认使用可配置的多语言
sentence-transformers 模型。首次预加载需要下载模型：

```bash
# Linux/macOS
EMBEDDING_LOCAL_ONLY=false python -m rag.builder
```

PowerShell：
```powershell
$env:EMBEDDING_LOCAL_ONLY = 'false'
python -m rag.builder
Remove-Item Env:EMBEDDING_LOCAL_ONLY
```

之后保持 `EMBEDDING_LOCAL_ONLY=true`，服务启动只使用本地模型。
缺少模型或知识库时 RAG 会降级，API 仍可提供明确缺少检索依据的建议。
用 `ENABLE_RAG=false` 可完全关闭检索。模型加载发生在启动准备阶段，
不发生在 API 模块导入或诊断请求内。

检索返回相似度、来源文件和 chunk_id，低于阈值不返回。安全 JSON 快照保存文档
与向量，在内存中创建 FAISS 索引；不加载旧 pickle/FAISS 二进制索引。
启动时检查知识内容、模型配置及快照校验和，必要时在文件锁保护下重建。
更新知识后重新运行构建并重启服务，运行中使用已经加载的快照。
向量库和知识目录只允许可信管理员写入；快照校验和用于完整性检查，不是签名。

运行实际模型检索评估：
```bash
python scripts/evaluate_rag.py
```
输出 Hit@k、MRR 和逐条命中来源；测试中的确定性向量只验证流程，
不能作为真实模型质量指标。

## 部署与开发

- [配置、容器与部署说明](docs/deployment.md)
- [架构与失败处理](docs/architecture.md)
- [安全边界](SECURITY.md)
- [贡献与测试](CONTRIBUTING.md)

运行测试：
```bash
python -m pip install --require-hashes -r requirements-dev.lock
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
```

MIT License。
