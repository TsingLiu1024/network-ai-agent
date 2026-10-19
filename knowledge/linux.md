# Linux 网络检测

用 ip addr、ip route、resolvectl status 或 cat /etc/resolv.conf 作只读检查，
分别确认地址、默认路由和 DNS。ping 使用 -c 指定次数，而不是 Windows 的 -n。
ICMP 被策略阻断时 ping 失败不能证明 TCP 或 DNS 不可用。
容器内路由和网络命名空间不同于宿主；容器检测结果只能说明容器网络。

不要在远程管理会话中盲目重启网络服务、释放地址或修改默认路由，
这些操作可能断开管理连接。应先确认备用连接和回退方案。
