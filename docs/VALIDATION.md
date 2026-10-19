# 修复与验证记录

日期：2026-10-19。基线：a99af5e；分支：fix/diagnosis-hardening。

## 已完成

| 原问题 | 修复及回归验证 |
| --- | --- |
| 模型失败被包装为成功 | 统一 LLMError，检查 HTTP/响应结构/非空内容，API 区分 success/partial/failed/demo；真实流水线模拟断网返回 502 |
| 网络诊断缺乏检测证据 | 接入带时间、平台、目标与服务器范围的真实只读探测；日志采用完整 PowerShell JSON 管道，返回码与超时可见 |
| 配置及 README 不一致 | 一个 Settings 对象控制所有 provider 的模型、URL、凭证、超时与路径；旧配置名/路由/请求字段保留兼容入口 |
| 串行重复推理与阻塞事件循环 | 最多两次模型调用、并行证据采集、有界工作线程、总预算、取消及超时不提前释放容量，关闭时等待后台工作完成 |
| JSON 修复计划未经校验 | Pydantic 严格验证结构、平台、权限、风险与验证方法；诊断始终不执行命令 |
| 命令黑名单容易绕过 | 禁止任意 shell 字符串；本地辅助工具只接受预定义动作和明确确认；脚本默认拒绝执行并支持 ShouldProcess |
| 索引空目录、损坏、过时与 pickle 风险 | 文件锁、内容寻址、原子发布、安全 JSON 向量、来源/相关性；旧 pickle 不加载；空卷、损坏、极大数值及语料变更有回归 |
| 数据暴露与资源限制不足 | 本机采集与云端上传双重开关；API key、请求体和问题长度限制、响应字节上限、凭证尽力脱敏、错误不回显原始输入或上游内容 |
| 部署与测试缺失 | 修复 Docker CMD，非 root/本地端口/只读知识挂载、CPU 依赖哈希锁文件、CI、完整使用说明与检索评估 |

## 已实际执行的验证

- 现有环境完成前 76 项，完整锁定的干净 Python 3.12.4 虚拟环境：**77 项 pytest 全部通过**。
- pytest 覆盖：783/881 条语句，约 88.9%。这不是漏洞覆盖率。
- 干净环境已成功按 requirements-dev.lock 和完整 requirements.lock 安装，哈希检查启用；pip check 无依赖冲突。
- Ruff check、format --check、compileall、git diff --check 通过。
- 实际启动 uvicorn 独立进程，/ready、诊断 API、request_id、结构化计划和 demo 标识验证通过；进程已关闭。
- 实际下载并加载 sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2，中文知识索引与查询成功；随后在 HF_HUB_OFFLINE=1 下通过缓存复用与真实 API 检索测试。
- 4 条中文检索冒烟样例：Hit@3=100%，MRR=0.833。DNS 样例目标文档排第 3；其余三条排第 1。样本很小，不能作为总体准确率或生产效果保证。明细见 validation/retrieval-evaluation.json。
- 查询两份锁文件中的 62 个依赖版本，PyPI 版本 JSON 接口未返回有效已知漏洞记录；CPU torch 映射到相同公开版本查询。此检查不覆盖未知漏洞、镜像系统包或所有 CPU 构建差异。明细见 validation/dependency-audit.json；[查询方式](https://docs.pypi.org/api/json/#known-vulnerabilities)。
- 独立代码复核发现的两项问题已各自通过失败回归复现并修复：采集线程逃逸并发限制、异常大数值阻止损坏快照重建。
- docker compose config --quiet 通过，使用 .env.example 的空凭证副本。

## 尚未实际执行的外部验证

- 本机 Docker Desktop Linux 引擎未运行（命名管道不存在），未运行真实镜像构建/容器冒烟；已配置对应 CI job，但远端 CI 尚未触发。
- 没有调用付费云模型；三个 provider 的 HTTP 契约及错误路径使用模拟响应验证。
- 未在真实设备执行网络修复或读取真实 Windows 事件日志；相关成功/失败/超时和保护逻辑使用受控夹具验证。脚本无 -Execute 的拒绝路径使用真实 PowerShell，并屏蔽系统命令。
- Linux/Python 3.13 矩阵已配置，未在本机运行；当前主机为 Windows/Python 3.12。
- 新版 Starlette TestClient 对 httpx 发出一条上游废弃告警，测试结果通过。

## 使用与集成

代码保留在本地分支，没有推送或改动 GitHub main。使用仓库根 README 安装和配置。
修复包不包含真实凭证、模型缓存、日志或本机向量库。生成命令始终为建议；
结构校验和尽力脱敏不等于对所有环境的安全保证。
