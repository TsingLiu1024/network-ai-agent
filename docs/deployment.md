# 配置与部署

唯一配置入口为 config/settings.py，支持 .env 和进程环境变量，环境变量优先。
主要配置见 .env.example。MODEL_PROVIDER 为标准名，LLM_PROVIDER 是兼容别名；
OLLAMA_URL 为标准名，OLLAMA_HOST 是兼容别名。两者同时存在时标准名优先。
所有相对知识/向量目录都相对于项目根目录，而非当前工作目录。

模型名、URL、凭证、超时与长度限制经过同一配置校验；启动校验只检查配置，
不代表外部服务可用。云模型凭证缺失时启动失败，不会静默切到本地模型。
不要设置含 userinfo、query 或 fragment 的模型 URL。远端推理请使用 HTTPS
或受信任的私有网络。

## Docker Compose

复制 .env.example 为 .env。容器访问宿主 Ollama 时设置
OLLAMA_URL=http://host.docker.internal:11434，宿主 Ollama 还需监听可达地址，
并用防火墙限制访问。容器内的 localhost 不是宿主机。

默认仅将端口发布到 127.0.0.1，容器以 uid/gid 10001 运行，不使用宿主网络、
不挂载宿主日志，不添加修复权限。镜像带 ping/nslookup；宿主限制 ICMP 时，
探测失败会返回明确失败信息。

```bash
docker compose config --quiet
docker compose build
docker compose run --rm -e EMBEDDING_LOCAL_ONLY=false network-ai-agent python -m rag.builder
docker compose up -d
```

模型与索引使用独立命名卷，知识目录只读挂载。模型预加载失败时可先
ENABLE_RAG=false 启动。自定义 bind mount 需要预先赋予 uid 10001 写权限；
不要对任意宿主目录递归修改权限。第一次构建镜像和下载模型需要网络，
模型准备可能耗时数分钟，诊断请求不会自动下载模型。

Docker HEALTHCHECK 检查服务存活，/ready 额外显示 RAG 状态。代理可用
/ready 作为部署就绪检查，监控同时检查 rag 字段以发现知识库降级。
API_KEY 为空时适合本机使用；对外部署必须设置强随机 API_KEY，并通过
反向代理启用 TLS、访问控制和按用户限流。每个进程有独立容量限制；
多 worker 部署时总容量是 worker 数乘 MAX_CONCURRENT_DIAGNOSES。

## 资源与超时

问题最多 2000 字符，请求体最多 16000 字节，接收请求体最多等待 5 秒。
API 等待 DIAGNOSIS_TIMEOUT 秒；同步操作位于有界线程池，超时/断开连接
不会提前释放并发名额，后台任务实际结束才释放。每个 subprocess 有硬超时。
HTTP 客户端配置连接/读取超时并在响应后检查预算；Python 线程不能强制中断
正在执行的第三方 C 扩展或网络调用。因此 API 超时不等于后台任务已结束；
需要更强隔离的生产环境应由进程级作业运行器执行推理/embedding。
不要将 DIAGNOSIS_TIMEOUT 设得低于正常模型响应时延。

每次诊断最多两次模型调用，模型输出最多 2048 tokens，另有字符数校验。
MAX_CONTEXT_LENGTH 是整个 prompt 的字符上限，不是精确 token 数；
会标记截断，不允许无界追加日志。ENABLE_TOKEN_OPTIMIZER 作为旧配置兼容保留，
长度硬上限始终生效。embedding 仅在启动准备和查询时运行；
正在运行的服务不自动热加载新语料。

## 依赖复现

requirements-core.txt 为 API、检索和离线测试依赖，requirements.txt 加入
真实 embedding 模型，requirements-dev.txt 加入测试工具。输入文件使用兼容
范围；requirements.lock 和 requirements-dev.lock 锁定完整传递依赖与哈希，
使用 pip install --require-hashes -r 对应的 lock 安装，Docker 和 CI 使用 lock。
lock 通过 uv 的 --universal --python-version 3.12 解析跨平台环境标记，
生产依赖额外使用 --torch-backend cpu，避免 Linux 镜像下载 CUDA 运行库。
CPU 包来自 [PyTorch 官方安装源](https://pytorch.org/get-started/locally/)，
requirements.lock 显式配置了该索引；所有包仍需匹配锁定哈希。
更新依赖时重新解析并运行测试、安全扫描与容器构建，不要只手改版本号。
CI 同时验证 Windows/Linux 的安装与镜像构建；CI 配置完成不代表尚未运行的
远端检查已经通过。
