# WSL 子系统网络排障

适用：运行 WSL 的 Windows 宿主。先确认问题发生在 Windows 宿主还是 WSL 内。

只读检查：wsl --status、wsl --list --verbose；在子系统检查
/etc/resolv.conf、ip route 与 DNS 查询。比较 Windows 与 WSL 对同一目标的
解析和连通性结果，再判断 DNS 转发、代理、VPN 或路由问题。
不要直接覆盖 resolv.conf 或禁用自动生成设置，先记录当前配置及生成方式。

wsl --shutdown 会停止所有运行中的 WSL 发行版与进程，可能中断工作。
只有用户明确确认并保存工作后才考虑使用，重启后复查网络；命令成功
不等于网络已修复。
