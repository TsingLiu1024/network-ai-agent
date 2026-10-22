# DNS 解析故障

适用：Windows、Linux。现象：域名访问失败但已知 IP 可达。

先区分本机解析和上游 DNS 问题。只读检查：nslookup github.com；
Linux 可用 resolvectl status，Windows 可用 Get-DnsClientServerAddress。
比较默认解析与经授权的指定 DNS 查询，记录返回地址、超时、NXDOMAIN 等证据。
单个站点或单个 DNS 服务不可达不能证明整个互联网断网。

ipconfig /flushdns 仅清空 Windows 本机 DNS 缓存，不修复上游服务、
代理或防火墙故障。不要在没有证据时重置整个网络栈或随意更改 DNS 服务器。
更改配置前记录原值，确认企业内网域名和 VPN 的依赖，验证失败时恢复原值。
