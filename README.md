# SlackTest

## Usage:

### Installation
1. install fabric
1. initialize the cotton submodule
1. copy your SSH public key to `build/keys/deploy.pub`

### Bootstrap the Host for Production

```
fab -H [IP] -u root init
```

### Deploy the hello-world Application

```
fab -H [IP] ship
```


# Ubuntu Production Configuration Notes:

*Installed Packages*
- sudo
- ufw
- fail2ban
- git-core
- vim
- build-essential
- python2.7
- python-setuptools
- python-dev
- python-pip
- python-virtualenv
- bsd-mailx
- apache2
- php5
- libapache2-modsecurity

(Certain packages, like the python bits, git, and build-essential are for the build/release toolset)


*Apache2*
- `ServerSignature Off`
- `ServerTokens Prod`
- `Timeout = 10`
- `LimitRequestBody = 4096`
- `KeepAliveTimeout = 3`
- `MaxKeepAliveRequests = 256`
- `ListenBacklog 8191`

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

*Kernel Tuning*
- socket backlog tuning params to match apache's `ListenBacklog`

*Other Considerations*
- consider restricting inbound HTTP requests to those proxied by the load balancer
- tune the `mpm_preform module`, setting `StartServers`, `MaxClients`, etc based on performance-testing of the app
- consider libapache2-modevasive if DDoSes are high risk, or aren't addressed at the load balancer/edge
- consider chrooting SSHD, apache2, etc if a strong case can be made for it
- disable ARP for VIP, if application nodes are in a cluster system
- vanilla settings for fail2ban may need adjusting depending on local traffic/attack patterns
- tuning `net.ipv4.tcp_keepalive_*` and `net.core.?mem_*` should be considered after application profiling
- mail aliases should be set to handle system/app mail properly, in concert with global mail policies
- backups!
