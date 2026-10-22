# 代理连接问题

适用：Windows、Linux。现象：浏览器、命令行或部分应用无法联网。

只读检查 HTTP_PROXY、HTTPS_PROXY、ALL_PROXY、NO_PROXY 与应用内独立代理设置；
不要将带用户名密码的代理 URL 发给模型或写入日志。确认代理程序运行、
监听地址和端口、规则及证书配置。区分 DNS 故障、代理拒绝连接和 TLS 错误。

Windows 可查看 netsh winhttp show proxy；WinHTTP、系统代理、浏览器代理并不
总是一致。使用受信任目标作有无代理的对比测试，记录差异，不要盲目关闭
企业代理或证书校验。配置更改前保存原值以便恢复。
