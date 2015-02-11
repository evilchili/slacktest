# Ubuntu Production Configuration Notes:

- `apt-get update && apt-get install apache2 php5 libapache2-modsecurity postfix`

*Apache2*
- `ServerSignature Off`
- `ServerTokens Prod`
- `Timeout = 10`
- `LimitRequestBody = 4096`
- `KeepAliveTimeout = 3`
- `MaxKeepAliveRequests = 256`

*PHP*
- `expose_php off`
- `zlib.output_compression = On`
- `zlib.output_compression_level = 6`
- `allow_url_fopen = Off`
- `allow_url_include = Off`
- `session.cookie_httponly = 1`
- `disable_functions += system, show_source, symlink, exec, dl, shell_exec, passthru, phpinfo, escapeshellarg, escapeshellcmd,`

*OpenSSH*
- `PasswordAuthentication no`  (skipped for test)
- `PermitRootLogin forced-commands-only` (skipped for test)
- `AllowGroups staff` (+ `root` for test)

*Firewall*
- allow ssh only from known administrative IPs (skipped for test)
- allow incoming tcp 80 from anywhere
- install fail2ban


*Unattended Upgrades*
- `Unattended-Upgrade::Mail "root@localhost";`

*Other Considerations*
- tune the `mpm_preform module`, setting `StartServers`, `MaxClients`, etc based on performance-testing of the app
- consider libapache2-modevasive if DDoSes are high risk, or aren't addressed at the load balancer/edge
- consider chrooting SSHD, apache2, etc if a strong case can be made for it
- disable ARP for VIP, if application nodes are in a cluster system
