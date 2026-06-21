#!/usr/bin/env python3
"""
Cisco 网络技术知识库生成器
从 network_notes.md 解析笔记，生成知识图谱 + 知识库 + 问答系统的单文件 HTML 应用。
"""

import re
import json
import os
from datetime import datetime

# ============================================================
# Part 1: 领域定义
# ============================================================

DOMAINS = [
    {"id": "net_fundamentals", "name": "网络基础", "icon": "\U0001f310", "color": "#4a9eff",
     "desc": "计算机网络基本概念、分类、协议模型与基础命令"},
    {"id": "ethernet_encap", "name": "以太网与数据封装", "icon": "\U0001f4e6", "color": "#58d68d",
     "desc": "IEEE802.x标准、CSMA/CD、VLAN概念、数据封装与解封装"},
    {"id": "collision_broadcast", "name": "冲突域与广播域", "icon": "\U0001f4e1", "color": "#f39c12",
     "desc": "共享介质、总线结构、冲突域、广播域、Hub vs Switch"},
    {"id": "switching_tech", "name": "交换技术", "icon": "\U0001f500", "color": "#9b59b6",
     "desc": "电路交换、报文交换、分组交换、局域网交换、SDN/NFV"},
    {"id": "vlan_trunk", "name": "跨交换机VLAN", "icon": "\U0001f3ed", "color": "#e74c3c",
     "desc": "Trunk、802.1Q、VLAN配置、三层交换、SVI"},
    {"id": "stp_etherchannel", "name": "STP与EtherChannel", "icon": "\U0001f333", "color": "#1abc9c",
     "desc": "生成树协议PVST+、根桥选举、PortFast、链路聚合"},
    {"id": "routing_basic", "name": "路由协议基础", "icon": "\U0001f6e3\ufe0f", "color": "#e67e22",
     "desc": "静态路由、RIP跳数与自动汇总、OSPF基础"},
    {"id": "ospf_advanced", "name": "OSPF深入", "icon": "\U0001f5fa\ufe0f", "color": "#2ecc71",
     "desc": "ABR、虚链路、5种分组、邻居状态机、重分布、Stub区域"},
    {"id": "vrrp_dhcp", "name": "VRRP与DHCP", "icon": "\U0001f4e8", "color": "#3498db",
     "desc": "网关冗余VRRP、DORA流程、DHCP中继、租期管理"},
    {"id": "email_proto", "name": "邮件协议", "icon": "\U0001f4e7", "color": "#e91e63",
     "desc": "SMTP、POP3、IMAP协议对比"},
    {"id": "acl", "name": "ACL访问控制", "icon": "\U0001f6e1\ufe0f", "color": "#ff5722",
     "desc": "标准ACL、扩展ACL、时间ACL、通配符掩码"},
    {"id": "port_security", "name": "端口安全", "icon": "\U0001f512", "color": "#795548",
     "desc": "port-security、sticky MAC"},
    {"id": "nat", "name": "NAT地址转换", "icon": "\U0001f504", "color": "#607d8b",
     "desc": "静态NAT、动态NAT、PAT端口地址转换"},
    {"id": "net_commands", "name": "网络命令与数制", "icon": "\U0001f4bb", "color": "#8bc34a",
     "desc": "ping、ipconfig、二进制/十六进制转换"},
]

# ============================================================
# Part 2: 知识图谱节点定义
# ============================================================

NODES = [
    # --- 领域节点 (type=domain) ---
    {"id": "d_net_fundamentals", "label": "网络基础", "type": "domain", "domain": "net_fundamentals",
     "desc": "计算机网络的基本概念、分类方法和协议模型", "size": 50, "importance": 5},
    {"id": "d_ethernet_encap", "label": "以太网与封装", "type": "domain", "domain": "ethernet_encap",
     "desc": "以太网标准、CSMA/CD和数据封装/解封装全流程", "size": 50, "importance": 5},
    {"id": "d_collision_broadcast", "label": "冲突域与广播域", "type": "domain", "domain": "collision_broadcast",
     "desc": "共享介质环境下的冲突域和广播域概念", "size": 50, "importance": 5},
    {"id": "d_switching_tech", "label": "交换技术", "type": "domain", "domain": "switching_tech",
     "desc": "电路交换、报文交换、分组交换等核心交换技术", "size": 50, "importance": 5},
    {"id": "d_vlan_trunk", "label": "跨交换机VLAN", "type": "domain", "domain": "vlan_trunk",
     "desc": "VLAN划分、Trunk配置和三层交换", "size": 50, "importance": 5},
    {"id": "d_stp_etherchannel", "label": "STP与链路聚合", "type": "domain", "domain": "stp_etherchannel",
     "desc": "生成树协议和EtherChannel链路聚合", "size": 50, "importance": 5},
    {"id": "d_routing_basic", "label": "路由协议基础", "type": "domain", "domain": "routing_basic",
     "desc": "静态路由、RIP和OSPF基础", "size": 50, "importance": 5},
    {"id": "d_ospf_advanced", "label": "OSPF深入", "type": "domain", "domain": "ospf_advanced",
     "desc": "OSPF高级特性：虚链路、重分布、Stub区域", "size": 50, "importance": 5},
    {"id": "d_vrrp_dhcp", "label": "VRRP与DHCP", "type": "domain", "domain": "vrrp_dhcp",
     "desc": "网关冗余和动态IP地址分配", "size": 50, "importance": 5},
    {"id": "d_email_proto", "label": "邮件协议", "type": "domain", "domain": "email_proto",
     "desc": "SMTP、POP3、IMAP邮件协议", "size": 50, "importance": 5},
    {"id": "d_acl", "label": "ACL访问控制", "type": "domain", "domain": "acl",
     "desc": "访问控制列表的原理与配置", "size": 50, "importance": 5},
    {"id": "d_port_security", "label": "端口安全", "type": "domain", "domain": "port_security",
     "desc": "交换机端口安全技术", "size": 50, "importance": 5},
    {"id": "d_nat", "label": "NAT地址转换", "type": "domain", "domain": "nat",
     "desc": "网络地址转换技术", "size": 50, "importance": 5},
    {"id": "d_net_commands", "label": "网络命令", "type": "domain", "domain": "net_commands",
     "desc": "常用网络诊断命令和数制转换", "size": 50, "importance": 5},

    # --- 主题节点 (type=topic) ---
    {"id": "t_net_classify", "label": "网络分类", "type": "topic", "domain": "net_fundamentals",
     "desc": "按地理位置(LAN/MAN/WAN)、传输介质、拓扑结构、交换方式分类", "size": 35, "importance": 4},
    {"id": "t_osi_model", "label": "OSI七层模型", "type": "topic", "domain": "net_fundamentals",
     "desc": "物理层→数据链路层→网络层→传输层→会话层→表示层→应用层", "size": 40, "importance": 5},
    {"id": "t_tcpip_model", "label": "TCP/IP四层模型", "type": "topic", "domain": "net_fundamentals",
     "desc": "网络接口层→网际互连层→传输层→应用层", "size": 38, "importance": 5},
    {"id": "t_switch_cmd", "label": "交换机基础命令", "type": "topic", "domain": "net_fundamentals",
     "desc": "enable、conf t、hostname、write、reload等基础IOS命令", "size": 30, "importance": 3},
    {"id": "t_ieee802", "label": "IEEE802标准族", "type": "topic", "domain": "ethernet_encap",
     "desc": "802.1概述、802.2 LLC、802.3以太网、802.11无线等标准", "size": 32, "importance": 4},
    {"id": "t_csma_cd", "label": "CSMA/CD", "type": "topic", "domain": "ethernet_encap",
     "desc": "载波侦听多路访问/冲突检测，先听后发、边发边听、冲突停发", "size": 35, "importance": 4},
    {"id": "t_vlan_concept", "label": "VLAN概念", "type": "topic", "domain": "ethernet_encap",
     "desc": "虚拟局域网，将物理网络划分为逻辑子网，隔离广播域增强安全", "size": 38, "importance": 5},
    {"id": "t_encapsulation", "label": "数据封装/解封装", "type": "topic", "domain": "ethernet_encap",
     "desc": "发送端自上而下封装(段→包→帧→比特)，接收端自下而上解封装", "size": 40, "importance": 5},
    {"id": "t_utf8_encoding", "label": "UTF-8编码", "type": "topic", "domain": "ethernet_encap",
     "desc": "表示层将Unicode字符转换为UTF-8字节流作为数据有效载荷", "size": 25, "importance": 3},
    {"id": "t_collision_domain", "label": "冲突域", "type": "topic", "domain": "collision_broadcast",
     "desc": "共享同一传输介质、可能发生数据冲突的设备集合。Hub同一冲突域，Switch每端口独立", "size": 35, "importance": 4},
    {"id": "t_broadcast_domain", "label": "广播域", "type": "topic", "domain": "collision_broadcast",
     "desc": "能接收到同样广播消息的设备集合。交换机不隔离广播域，路由器隔离", "size": 35, "importance": 4},
    {"id": "t_hub_vs_switch", "label": "Hub vs Switch", "type": "topic", "domain": "collision_broadcast",
     "desc": "Hub是物理层设备不隔离冲突域，Switch是链路层设备每端口独立冲突域", "size": 30, "importance": 3},
    {"id": "t_circuit_switch", "label": "电路交换", "type": "topic", "domain": "switching_tech",
     "desc": "建立专用物理路径，通信期间独占，如传统电话网络PSTN", "size": 32, "importance": 4},
    {"id": "t_message_switch", "label": "报文交换", "type": "topic", "domain": "switching_tech",
     "desc": "存储-转发完整报文，无需建立连接，如早期电报和电子邮件", "size": 30, "importance": 3},
    {"id": "t_packet_switch", "label": "分组交换", "type": "topic", "domain": "switching_tech",
     "desc": "数据分割成小包独立路由，资源利用率高，如互联网数据传输", "size": 35, "importance": 4},
    {"id": "t_lan_switch", "label": "局域网交换", "type": "topic", "domain": "switching_tech",
     "desc": "端口交换、帧交换(直通/存储转发)、信元交换(ATM)", "size": 32, "importance": 4},
    {"id": "t_sdn_nfv", "label": "SDN/NFV", "type": "topic", "domain": "switching_tech",
     "desc": "软件定义网络和网络功能虚拟化，现代网络发展趋势", "size": 28, "importance": 3},
    {"id": "t_trunk_8021q", "label": "Trunk与802.1Q", "type": "topic", "domain": "vlan_trunk",
     "desc": "Trunk链路允许多VLAN通过，802.1Q标准添加VLAN标签实现逻辑复用", "size": 38, "importance": 5},
    {"id": "t_vlan_config", "label": "VLAN配置", "type": "topic", "domain": "vlan_trunk",
     "desc": "创建VLAN、分配Access端口、配置Trunk端口、验证配置", "size": 36, "importance": 5},
    {"id": "t_layer3_switch", "label": "三层交换与SVI", "type": "topic", "domain": "vlan_trunk",
     "desc": "三层交换机通过SVI实现VLAN间路由，每个VLAN需独立网段", "size": 35, "importance": 4},
    {"id": "t_mac_table", "label": "MAC地址表", "type": "topic", "domain": "vlan_trunk",
     "desc": "交换机自学习源MAC、查表转发、老化机制(默认300秒)", "size": 30, "importance": 4},
    {"id": "t_vtp", "label": "VTP协议", "type": "topic", "domain": "vlan_trunk",
     "desc": "VLAN Trunking Protocol，多交换机间同步VLAN信息", "size": 25, "importance": 3},
    {"id": "t_stp", "label": "生成树协议STP", "type": "topic", "domain": "stp_etherchannel",
     "desc": "通过逻辑阻塞端口防止环路：选举根桥→根端口→指定端口→阻塞", "size": 40, "importance": 5},
    {"id": "t_pvst", "label": "PVST+", "type": "topic", "domain": "stp_etherchannel",
     "desc": "Per-VLAN Spanning Tree，思科增强版STP，每VLAN独立生成树实例", "size": 30, "importance": 4},
    {"id": "t_portfast", "label": "PortFast", "type": "topic", "domain": "stp_etherchannel",
     "desc": "接入端口快速转发，跳过监听/学习状态直接进入转发状态", "size": 28, "importance": 3},
    {"id": "t_etherchannel", "label": "EtherChannel", "type": "topic", "domain": "stp_etherchannel",
     "desc": "链路聚合技术，将多条物理链路捆绑为一条逻辑链路提高带宽", "size": 35, "importance": 4},
    {"id": "t_static_route", "label": "静态路由", "type": "topic", "domain": "routing_basic",
     "desc": "手动配置路由表项，ip route 目的 掩码 下一跳，适用于小型网络", "size": 32, "importance": 4},
    {"id": "t_floating_static", "label": "浮动静态路由", "type": "topic", "domain": "routing_basic",
     "desc": "通过调整AD值实现路由备份，主路由失效时备用路由生效", "size": 28, "importance": 3},
    {"id": "t_rip", "label": "RIP协议", "type": "topic", "domain": "routing_basic",
     "desc": "距离矢量协议，跳数度量，最大15跳，自动汇总导致不连续子网问题", "size": 38, "importance": 5},
    {"id": "t_ospf_basic", "label": "OSPF基础", "type": "topic", "domain": "routing_basic",
     "desc": "链路状态协议，Cost=参考带宽/接口带宽，Area分层设计", "size": 40, "importance": 5},
    {"id": "t_abr", "label": "ABR区域边界路由器", "type": "topic", "domain": "ospf_advanced",
     "desc": "连接Area 0和其他区域的路由器，维护多份LSDB", "size": 32, "importance": 4},
    {"id": "t_virtual_link", "label": "OSPF虚链路", "type": "topic", "domain": "ospf_advanced",
     "desc": "Area 0的逻辑延伸，使用单播传递LSA，解决区域不连续问题", "size": 35, "importance": 4},
    {"id": "t_ospf_packets", "label": "OSPF五种分组", "type": "topic", "domain": "ospf_advanced",
     "desc": "Hello、DBD、LSR、LSU、LSAck，用于邻居发现和LSDB同步", "size": 35, "importance": 4},
    {"id": "t_ospf_states", "label": "邻居状态机", "type": "topic", "domain": "ospf_advanced",
     "desc": "Down→Init→2-Way→ExStart→Exchange→Loading→Full", "size": 33, "importance": 4},
    {"id": "t_redistribution", "label": "路由重分布", "type": "topic", "domain": "ospf_advanced",
     "desc": "边界路由器在不同路由协议间翻译路由信息，需防环路", "size": 35, "importance": 4},
    {"id": "t_stub_area", "label": "Stub/NSSA区域", "type": "topic", "domain": "ospf_advanced",
     "desc": "限制LSA类型减少路由表大小，Totally Stub阻止3类LSA", "size": 30, "importance": 3},
    {"id": "t_loopback", "label": "Loopback接口", "type": "topic", "domain": "ospf_advanced",
     "desc": "虚拟接口永远UP，OSPF默认将其掩码改为/32宣告", "size": 28, "importance": 3},
    {"id": "t_vrrp", "label": "VRRP", "type": "topic", "domain": "vrrp_dhcp",
     "desc": "虚拟路由冗余协议，多路由器虚拟为一台，解决网关单点故障", "size": 32, "importance": 4},
    {"id": "t_dhcp", "label": "DHCP", "type": "topic", "domain": "vrrp_dhcp",
     "desc": "动态主机配置协议，DORA流程自动分配IP地址", "size": 40, "importance": 5},
    {"id": "t_dhcp_dora", "label": "DORA流程", "type": "topic", "domain": "vrrp_dhcp",
     "desc": "Discover→Offer→Request→ACK，四步完成IP自动分配", "size": 35, "importance": 5},
    {"id": "t_dhcp_relay", "label": "DHCP中继", "type": "topic", "domain": "vrrp_dhcp",
     "desc": "ip helper-address，路由器转发DHCP广播到远程服务器", "size": 30, "importance": 4},
    {"id": "t_dhcp_lease", "label": "DHCP租期管理", "type": "topic", "domain": "vrrp_dhcp",
     "desc": "T1=50%续租、T2=87.5%重绑定，过期释放IP", "size": 25, "importance": 3},
    {"id": "t_smtp", "label": "SMTP", "type": "topic", "domain": "email_proto",
     "desc": "简单邮件传输协议，端口25/465/587，用于邮件发送和中继", "size": 30, "importance": 3},
    {"id": "t_pop3", "label": "POP3", "type": "topic", "domain": "email_proto",
     "desc": "邮局协议v3，端口110/995，下载邮件到本地可离线查看", "size": 28, "importance": 3},
    {"id": "t_imap", "label": "IMAP", "type": "topic", "domain": "email_proto",
     "desc": "互联网邮件访问协议，端口143/993，服务器端管理多设备同步", "size": 28, "importance": 3},
    {"id": "t_acl_standard", "label": "标准ACL", "type": "topic", "domain": "acl",
     "desc": "仅基于源IP匹配，编号1-99/1300-1999，控制粒度粗", "size": 32, "importance": 4},
    {"id": "t_acl_extended", "label": "扩展ACL", "type": "topic", "domain": "acl",
     "desc": "基于源IP+目的IP+协议+端口多维匹配，编号100-199，细粒度控制", "size": 35, "importance": 4},
    {"id": "t_acl_wildcard", "label": "通配符掩码", "type": "topic", "domain": "acl",
     "desc": "0=精确匹配，1=忽略，0.0.0.255=/24网段，host=单台主机", "size": 28, "importance": 3},
    {"id": "t_acl_time", "label": "时间ACL", "type": "topic", "domain": "acl",
     "desc": "time-range定义时间段绑定ACL规则，实现基于时间的访问控制", "size": 25, "importance": 3},
    {"id": "t_acl_implicit_deny", "label": "隐含拒绝", "type": "topic", "domain": "acl",
     "desc": "ACL末尾默认deny any，未匹配任何规则的包被丢弃", "size": 28, "importance": 4},
    {"id": "t_port_sec", "label": "端口安全配置", "type": "topic", "domain": "port_security",
     "desc": "switchport port-security限制端口MAC地址数量，sticky自动学习", "size": 30, "importance": 3},
    {"id": "t_nat_static", "label": "静态NAT", "type": "topic", "domain": "nat",
     "desc": "一对一固定映射私有IP到公网IP，用于对外提供服务", "size": 30, "importance": 4},
    {"id": "t_nat_dynamic", "label": "动态NAT", "type": "topic", "domain": "nat",
     "desc": "地址池多对多映射，内网主机轮流使用公网IP", "size": 28, "importance": 3},
    {"id": "t_pat", "label": "PAT(端口地址转换)", "type": "topic", "domain": "nat",
     "desc": "多对一端口复用，多内网设备共用一个公网IP通过端口号区分", "size": 35, "importance": 5},
    {"id": "t_ping", "label": "ping命令", "type": "topic", "domain": "net_commands",
     "desc": "ICMP回显请求测试连通性，-t持续ping、-a解析主机名、-n指定包数", "size": 28, "importance": 3},
    {"id": "t_ipconfig", "label": "ipconfig命令", "type": "topic", "domain": "net_commands",
     "desc": "查看IP配置：/all详细信息、/release释放、/renew续租、/flushdns清缓存", "size": 28, "importance": 3},
    {"id": "t_number_convert", "label": "数制转换", "type": "topic", "domain": "net_commands",
     "desc": "二进制/十六进制转十进制，按权相加法", "size": 25, "importance": 3},

    # --- 协议节点 (type=protocol) ---
    {"id": "p_tcp", "label": "TCP", "type": "protocol", "domain": "net_fundamentals",
     "desc": "传输控制协议，面向连接、可靠、三次握手、确认重传、有序到达", "size": 38, "importance": 5},
    {"id": "p_udp", "label": "UDP", "type": "protocol", "domain": "net_fundamentals",
     "desc": "用户数据报协议，无连接、不可靠、开销小速度快，适用实时场景", "size": 35, "importance": 5},
    {"id": "p_ip", "label": "IP", "type": "protocol", "domain": "net_fundamentals",
     "desc": "网际协议，网络层核心，规定数据包格式和寻址方案", "size": 40, "importance": 5},
    {"id": "p_icmp", "label": "ICMP", "type": "protocol", "domain": "net_fundamentals",
     "desc": "互联网控制报文协议，传递错误报告和网络诊断信息", "size": 28, "importance": 3},
    {"id": "p_arp", "label": "ARP", "type": "protocol", "domain": "net_fundamentals",
     "desc": "地址解析协议，通过IP地址解析对应MAC地址", "size": 30, "importance": 4},
    {"id": "p_dns", "label": "DNS", "type": "protocol", "domain": "net_fundamentals",
     "desc": "域名系统，将域名转换为IP地址", "size": 30, "importance": 4},
    {"id": "p_http", "label": "HTTP/HTTPS", "type": "protocol", "domain": "net_fundamentals",
     "desc": "超文本传输协议，Web请求-响应协议", "size": 30, "importance": 4},
    {"id": "p_ftp", "label": "FTP", "type": "protocol", "domain": "net_fundamentals",
     "desc": "文件传输协议，用于网络文件上传和下载", "size": 25, "importance": 3},
    {"id": "p_ospf", "label": "OSPF", "type": "protocol", "domain": "routing_basic",
     "desc": "开放最短路径优先，链路状态IGP协议，Cost度量，Area分层", "size": 42, "importance": 5},
    {"id": "p_rip", "label": "RIP", "type": "protocol", "domain": "routing_basic",
     "desc": "路由信息协议，距离矢量，跳数度量，最大15跳", "size": 35, "importance": 4},
    {"id": "p_dhcp", "label": "DHCP", "type": "protocol", "domain": "vrrp_dhcp",
     "desc": "动态主机配置协议，UDP 67/68端口，自动分配IP", "size": 35, "importance": 5},
    {"id": "p_nat", "label": "NAT", "type": "protocol", "domain": "nat",
     "desc": "网络地址转换，解决IPv4地址短缺", "size": 32, "importance": 4},
    {"id": "p_stp", "label": "STP", "type": "protocol", "domain": "stp_etherchannel",
     "desc": "生成树协议，防止二层环路导致广播风暴", "size": 35, "importance": 5},
    {"id": "p_vrrp", "label": "VRRP", "type": "protocol", "domain": "vrrp_dhcp",
     "desc": "虚拟路由冗余协议，网关冗余备份", "size": 28, "importance": 3},
    {"id": "p_8021q", "label": "802.1Q", "type": "protocol", "domain": "vlan_trunk",
     "desc": "VLAN标签标准，在以太网帧中插入4字节VLAN Tag", "size": 30, "importance": 4},

    # --- 概念节点 (type=concept) ---
    {"id": "c_digital_data_signal", "label": "数字/数据/信号", "type": "concept", "domain": "net_fundamentals",
     "desc": "数字是基础符号，数据是原始记录，信息是有用数据，信号是传输载体", "size": 25, "importance": 3},
    {"id": "c_topology", "label": "拓扑结构", "type": "concept", "domain": "net_fundamentals",
     "desc": "总线型、星形、环形、树状型、网状型", "size": 28, "importance": 3},
    {"id": "c_private_ip", "label": "私有IP地址", "type": "concept", "domain": "routing_basic",
     "desc": "A类10.0.0.0/8，B类172.16.0.0/12，C类192.168.0.0/16", "size": 30, "importance": 4},
    {"id": "c_supervlan", "label": "Super VLAN", "type": "concept", "domain": "vlan_trunk",
     "desc": "VLAN聚合技术，多个子VLAN共享一个Super VLAN的IP地址节省地址资源", "size": 25, "importance": 3},
    {"id": "c_dora", "label": "DORA过程", "type": "concept", "domain": "vrrp_dhcp",
     "desc": "Discover→Offer→Request→ACK，DHCP四步IP分配流程", "size": 32, "importance": 4},
    {"id": "c_implicit_deny", "label": "隐含拒绝规则", "type": "concept", "domain": "acl",
     "desc": "ACL遍历所有规则未匹配则默认丢弃，顺序至关重要", "size": 28, "importance": 4},
    {"id": "c_discontinuous_subnet", "label": "不连续子网", "type": "concept", "domain": "routing_basic",
     "desc": "同一主类网络被其他网络隔开，RIP自动汇总导致路由冲突，需no auto-summary", "size": 30, "importance": 4},
    {"id": "c_root_bridge", "label": "根桥选举", "type": "concept", "domain": "stp_etherchannel",
     "desc": "STP中桥优先级+MAC地址决定根桥，数值越小优先级越高", "size": 30, "importance": 4},
    {"id": "c_encap_layers", "label": "数据形态变化", "type": "concept", "domain": "ethernet_encap",
     "desc": "传输层→段(Segment)，网络层→包(Packet)，链路层→帧(Frame)，物理层→比特流(Bits)", "size": 30, "importance": 4},
    {"id": "c_bus_topology", "label": "总线型拓扑", "type": "concept", "domain": "collision_broadcast",
     "desc": "所有计算机连接到一根同轴电缆(总线)，同一时间只能一台发送", "size": 25, "importance": 3},
    {"id": "c_flooding", "label": "泛洪转发", "type": "concept", "domain": "vlan_trunk",
     "desc": "交换机查表失败时将帧转发到除接收端口外的所有端口", "size": 25, "importance": 3},
    {"id": "c_cost_formula", "label": "OSPF Cost计算", "type": "concept", "domain": "routing_basic",
     "desc": "Cost = 参考带宽(默认100Mbps) / 接口带宽，带宽越高开销越低", "size": 28, "importance": 4},

    # --- 命令组节点 (type=command_group) ---
    {"id": "cg_vlan_create", "label": "vlan + name", "type": "command_group", "domain": "vlan_trunk",
     "desc": "vlan 10\\nname Sales  创建VLAN并命名", "size": 22, "importance": 3},
    {"id": "cg_switchport_access", "label": "switchport access", "type": "command_group", "domain": "vlan_trunk",
     "desc": "switchport mode access\\nswitchport access vlan 10  配置接入端口", "size": 22, "importance": 3},
    {"id": "cg_switchport_trunk", "label": "switchport trunk", "type": "command_group", "domain": "vlan_trunk",
     "desc": "switchport mode trunk\\nswitchport trunk allowed vlan 10,20  配置Trunk端口", "size": 22, "importance": 3},
    {"id": "cg_stp_priority", "label": "spanning-tree priority", "type": "command_group", "domain": "stp_etherchannel",
     "desc": "spanning-tree vlan 1 priority 4096  配置根桥优先级", "size": 22, "importance": 3},
    {"id": "cg_stp_portfast", "label": "spanning-tree portfast", "type": "command_group", "domain": "stp_etherchannel",
     "desc": "spanning-tree portfast  接入端口快速转发", "size": 20, "importance": 3},
    {"id": "cg_channel_group", "label": "channel-group", "type": "command_group", "domain": "stp_etherchannel",
     "desc": "channel-group 1 mode on  物理口加入EtherChannel", "size": 22, "importance": 3},
    {"id": "cg_ip_route", "label": "ip route", "type": "command_group", "domain": "routing_basic",
     "desc": "ip route 目的 掩码 下一跳 [AD]  配置静态路由", "size": 22, "importance": 3},
    {"id": "cg_router_rip", "label": "router rip", "type": "command_group", "domain": "routing_basic",
     "desc": "router rip\\nversion 2\\nno auto-summary\\nnetwork X.X.X.X  启用RIP并宣告网段", "size": 22, "importance": 3},
    {"id": "cg_router_ospf", "label": "router ospf", "type": "command_group", "domain": "routing_basic",
     "desc": "router ospf 1\\nnetwork X.X.X.X 0.0.0.255 area 0  启用OSPF并宣告", "size": 22, "importance": 3},
    {"id": "cg_redistribute", "label": "redistribute", "type": "command_group", "domain": "ospf_advanced",
     "desc": "redistribute rip subnets / redistribute ospf 1 metric 1  路由重分布", "size": 22, "importance": 3},
    {"id": "cg_ip_helper", "label": "ip helper-address", "type": "command_group", "domain": "vrrp_dhcp",
     "desc": "ip helper-address 服务器IP  配置DHCP中继", "size": 22, "importance": 3},
    {"id": "cg_access_list_std", "label": "access-list std", "type": "command_group", "domain": "acl",
     "desc": "access-list 10 deny host 192.168.1.50\\naccess-list 10 permit any  标准ACL", "size": 22, "importance": 3},
    {"id": "cg_access_list_ext", "label": "access-list ext", "type": "command_group", "domain": "acl",
     "desc": "access-list 101 deny tcp 源 反掩码 any eq 23  扩展ACL", "size": 22, "importance": 3},
    {"id": "cg_ip_nat", "label": "ip nat", "type": "command_group", "domain": "nat",
     "desc": "ip nat inside/outside\\nip nat inside source list 1 interface X overload  NAT配置", "size": 22, "importance": 3},
    {"id": "cg_port_security", "label": "port-security", "type": "command_group", "domain": "port_security",
     "desc": "switchport port-security\\nswitchport port-security mac-address sticky  端口安全", "size": 22, "importance": 3},
    {"id": "cg_ip_routing", "label": "ip routing", "type": "command_group", "domain": "vlan_trunk",
     "desc": "ip routing  三层交换机启用IP路由功能", "size": 20, "importance": 3},
    {"id": "cg_sdm_prefer", "label": "sdm prefer", "type": "command_group", "domain": "vlan_trunk",
     "desc": "sdm prefer routing  切换3560 SDM模板为路由模式需reload", "size": 20, "importance": 3},
]

# ============================================================
# Part 3: 知识图谱边定义
# ============================================================

EDGES = [
    # 领域→主题 belongs_to (反向: 主题属于领域)
    # 网络基础
    {"s": "t_net_classify", "t": "d_net_fundamentals", "type": "belongs_to", "label": "属于"},
    {"s": "t_osi_model", "t": "d_net_fundamentals", "type": "belongs_to", "label": "属于"},
    {"s": "t_tcpip_model", "t": "d_net_fundamentals", "type": "belongs_to", "label": "属于"},
    {"s": "t_switch_cmd", "t": "d_net_fundamentals", "type": "belongs_to", "label": "属于"},
    {"s": "c_digital_data_signal", "t": "d_net_fundamentals", "type": "belongs_to", "label": "属于"},
    {"s": "c_topology", "t": "d_net_fundamentals", "type": "belongs_to", "label": "属于"},
    # 以太网
    {"s": "t_ieee802", "t": "d_ethernet_encap", "type": "belongs_to", "label": "属于"},
    {"s": "t_csma_cd", "t": "d_ethernet_encap", "type": "belongs_to", "label": "属于"},
    {"s": "t_vlan_concept", "t": "d_ethernet_encap", "type": "belongs_to", "label": "属于"},
    {"s": "t_encapsulation", "t": "d_ethernet_encap", "type": "belongs_to", "label": "属于"},
    {"s": "t_utf8_encoding", "t": "d_ethernet_encap", "type": "belongs_to", "label": "属于"},
    {"s": "c_encap_layers", "t": "d_ethernet_encap", "type": "belongs_to", "label": "属于"},
    # 冲突域
    {"s": "t_collision_domain", "t": "d_collision_broadcast", "type": "belongs_to", "label": "属于"},
    {"s": "t_broadcast_domain", "t": "d_collision_broadcast", "type": "belongs_to", "label": "属于"},
    {"s": "t_hub_vs_switch", "t": "d_collision_broadcast", "type": "belongs_to", "label": "属于"},
    {"s": "c_bus_topology", "t": "d_collision_broadcast", "type": "belongs_to", "label": "属于"},
    # 交换技术
    {"s": "t_circuit_switch", "t": "d_switching_tech", "type": "belongs_to", "label": "属于"},
    {"s": "t_message_switch", "t": "d_switching_tech", "type": "belongs_to", "label": "属于"},
    {"s": "t_packet_switch", "t": "d_switching_tech", "type": "belongs_to", "label": "属于"},
    {"s": "t_lan_switch", "t": "d_switching_tech", "type": "belongs_to", "label": "属于"},
    {"s": "t_sdn_nfv", "t": "d_switching_tech", "type": "belongs_to", "label": "属于"},
    # VLAN
    {"s": "t_trunk_8021q", "t": "d_vlan_trunk", "type": "belongs_to", "label": "属于"},
    {"s": "t_vlan_config", "t": "d_vlan_trunk", "type": "belongs_to", "label": "属于"},
    {"s": "t_layer3_switch", "t": "d_vlan_trunk", "type": "belongs_to", "label": "属于"},
    {"s": "t_mac_table", "t": "d_vlan_trunk", "type": "belongs_to", "label": "属于"},
    {"s": "t_vtp", "t": "d_vlan_trunk", "type": "belongs_to", "label": "属于"},
    {"s": "c_supervlan", "t": "d_vlan_trunk", "type": "belongs_to", "label": "属于"},
    {"s": "c_flooding", "t": "d_vlan_trunk", "type": "belongs_to", "label": "属于"},
    # STP
    {"s": "t_stp", "t": "d_stp_etherchannel", "type": "belongs_to", "label": "属于"},
    {"s": "t_pvst", "t": "d_stp_etherchannel", "type": "belongs_to", "label": "属于"},
    {"s": "t_portfast", "t": "d_stp_etherchannel", "type": "belongs_to", "label": "属于"},
    {"s": "t_etherchannel", "t": "d_stp_etherchannel", "type": "belongs_to", "label": "属于"},
    {"s": "c_root_bridge", "t": "d_stp_etherchannel", "type": "belongs_to", "label": "属于"},
    # 路由
    {"s": "t_static_route", "t": "d_routing_basic", "type": "belongs_to", "label": "属于"},
    {"s": "t_floating_static", "t": "d_routing_basic", "type": "belongs_to", "label": "属于"},
    {"s": "t_rip", "t": "d_routing_basic", "type": "belongs_to", "label": "属于"},
    {"s": "t_ospf_basic", "t": "d_routing_basic", "type": "belongs_to", "label": "属于"},
    {"s": "c_private_ip", "t": "d_routing_basic", "type": "belongs_to", "label": "属于"},
    {"s": "c_discontinuous_subnet", "t": "d_routing_basic", "type": "belongs_to", "label": "属于"},
    {"s": "c_cost_formula", "t": "d_routing_basic", "type": "belongs_to", "label": "属于"},
    # OSPF深入
    {"s": "t_abr", "t": "d_ospf_advanced", "type": "belongs_to", "label": "属于"},
    {"s": "t_virtual_link", "t": "d_ospf_advanced", "type": "belongs_to", "label": "属于"},
    {"s": "t_ospf_packets", "t": "d_ospf_advanced", "type": "belongs_to", "label": "属于"},
    {"s": "t_ospf_states", "t": "d_ospf_advanced", "type": "belongs_to", "label": "属于"},
    {"s": "t_redistribution", "t": "d_ospf_advanced", "type": "belongs_to", "label": "属于"},
    {"s": "t_stub_area", "t": "d_ospf_advanced", "type": "belongs_to", "label": "属于"},
    {"s": "t_loopback", "t": "d_ospf_advanced", "type": "belongs_to", "label": "属于"},
    # VRRP/DHCP
    {"s": "t_vrrp", "t": "d_vrrp_dhcp", "type": "belongs_to", "label": "属于"},
    {"s": "t_dhcp", "t": "d_vrrp_dhcp", "type": "belongs_to", "label": "属于"},
    {"s": "t_dhcp_dora", "t": "d_vrrp_dhcp", "type": "belongs_to", "label": "属于"},
    {"s": "t_dhcp_relay", "t": "d_vrrp_dhcp", "type": "belongs_to", "label": "属于"},
    {"s": "t_dhcp_lease", "t": "d_vrrp_dhcp", "type": "belongs_to", "label": "属于"},
    {"s": "c_dora", "t": "d_vrrp_dhcp", "type": "belongs_to", "label": "属于"},
    # 邮件
    {"s": "t_smtp", "t": "d_email_proto", "type": "belongs_to", "label": "属于"},
    {"s": "t_pop3", "t": "d_email_proto", "type": "belongs_to", "label": "属于"},
    {"s": "t_imap", "t": "d_email_proto", "type": "belongs_to", "label": "属于"},
    # ACL
    {"s": "t_acl_standard", "t": "d_acl", "type": "belongs_to", "label": "属于"},
    {"s": "t_acl_extended", "t": "d_acl", "type": "belongs_to", "label": "属于"},
    {"s": "t_acl_wildcard", "t": "d_acl", "type": "belongs_to", "label": "属于"},
    {"s": "t_acl_time", "t": "d_acl", "type": "belongs_to", "label": "属于"},
    {"s": "t_acl_implicit_deny", "t": "d_acl", "type": "belongs_to", "label": "属于"},
    {"s": "c_implicit_deny", "t": "d_acl", "type": "belongs_to", "label": "属于"},
    # 端口安全
    {"s": "t_port_sec", "t": "d_port_security", "type": "belongs_to", "label": "属于"},
    # NAT
    {"s": "t_nat_static", "t": "d_nat", "type": "belongs_to", "label": "属于"},
    {"s": "t_nat_dynamic", "t": "d_nat", "type": "belongs_to", "label": "属于"},
    {"s": "t_pat", "t": "d_nat", "type": "belongs_to", "label": "属于"},
    # 命令
    {"s": "t_ping", "t": "d_net_commands", "type": "belongs_to", "label": "属于"},
    {"s": "t_ipconfig", "t": "d_net_commands", "type": "belongs_to", "label": "属于"},
    {"s": "t_number_convert", "t": "d_net_commands", "type": "belongs_to", "label": "属于"},

    # --- 协议 belongs_to 层 ---
    {"s": "p_tcp", "t": "t_osi_model", "type": "belongs_to", "label": "传输层"},
    {"s": "p_udp", "t": "t_osi_model", "type": "belongs_to", "label": "传输层"},
    {"s": "p_ip", "t": "t_osi_model", "type": "belongs_to", "label": "网络层"},
    {"s": "p_icmp", "t": "t_osi_model", "type": "belongs_to", "label": "网络层"},
    {"s": "p_arp", "t": "t_osi_model", "type": "belongs_to", "label": "网络层"},
    {"s": "p_dns", "t": "t_osi_model", "type": "belongs_to", "label": "应用层"},
    {"s": "p_http", "t": "t_osi_model", "type": "belongs_to", "label": "应用层"},
    {"s": "p_ftp", "t": "t_osi_model", "type": "belongs_to", "label": "应用层"},
    {"s": "p_ospf", "t": "t_ospf_basic", "type": "belongs_to", "label": "协议"},
    {"s": "p_rip", "t": "t_rip", "type": "belongs_to", "label": "协议"},
    {"s": "p_dhcp", "t": "t_dhcp", "type": "belongs_to", "label": "协议"},
    {"s": "p_nat", "t": "t_nat_static", "type": "belongs_to", "label": "协议"},
    {"s": "p_stp", "t": "t_stp", "type": "belongs_to", "label": "协议"},
    {"s": "p_vrrp", "t": "t_vrrp", "type": "belongs_to", "label": "协议"},
    {"s": "p_8021q", "t": "t_trunk_8021q", "type": "belongs_to", "label": "协议"},

    # --- 命令 configures 主题 ---
    {"s": "cg_vlan_create", "t": "t_vlan_config", "type": "configures", "label": "配置"},
    {"s": "cg_switchport_access", "t": "t_vlan_config", "type": "configures", "label": "配置"},
    {"s": "cg_switchport_trunk", "t": "t_trunk_8021q", "type": "configures", "label": "配置"},
    {"s": "cg_stp_priority", "t": "t_stp", "type": "configures", "label": "配置"},
    {"s": "cg_stp_portfast", "t": "t_portfast", "type": "configures", "label": "配置"},
    {"s": "cg_channel_group", "t": "t_etherchannel", "type": "configures", "label": "配置"},
    {"s": "cg_ip_route", "t": "t_static_route", "type": "configures", "label": "配置"},
    {"s": "cg_router_rip", "t": "t_rip", "type": "configures", "label": "配置"},
    {"s": "cg_router_ospf", "t": "t_ospf_basic", "type": "configures", "label": "配置"},
    {"s": "cg_redistribute", "t": "t_redistribution", "type": "configures", "label": "配置"},
    {"s": "cg_ip_helper", "t": "t_dhcp_relay", "type": "configures", "label": "配置"},
    {"s": "cg_access_list_std", "t": "t_acl_standard", "type": "configures", "label": "配置"},
    {"s": "cg_access_list_ext", "t": "t_acl_extended", "type": "configures", "label": "配置"},
    {"s": "cg_ip_nat", "t": "t_pat", "type": "configures", "label": "配置"},
    {"s": "cg_port_security", "t": "t_port_sec", "type": "configures", "label": "配置"},
    {"s": "cg_ip_routing", "t": "t_layer3_switch", "type": "configures", "label": "配置"},
    {"s": "cg_sdm_prefer", "t": "t_layer3_switch", "type": "configures", "label": "配置"},

    # --- uses 关系 ---
    {"s": "t_ospf_basic", "t": "c_cost_formula", "type": "uses", "label": "使用"},
    {"s": "t_rip", "t": "c_discontinuous_subnet", "type": "uses", "label": "涉及"},
    {"s": "t_dhcp_dora", "t": "c_dora", "type": "uses", "label": "使用"},
    {"s": "t_stp", "t": "c_root_bridge", "type": "uses", "label": "使用"},
    {"s": "t_encapsulation", "t": "c_encap_layers", "type": "uses", "label": "使用"},
    {"s": "t_encapsulation", "t": "t_utf8_encoding", "type": "uses", "label": "使用"},
    {"s": "t_collision_domain", "t": "t_csma_cd", "type": "uses", "label": "使用"},
    {"s": "t_collision_domain", "t": "c_bus_topology", "type": "uses", "label": "基于"},
    {"s": "t_acl_standard", "t": "t_acl_wildcard", "type": "uses", "label": "使用"},
    {"s": "t_acl_extended", "t": "t_acl_wildcard", "type": "uses", "label": "使用"},

    # --- related_to 关系 ---
    {"s": "t_osi_model", "t": "t_tcpip_model", "type": "related_to", "label": "对比"},
    {"s": "p_tcp", "t": "p_udp", "type": "related_to", "label": "对比"},
    {"s": "p_ospf", "t": "p_rip", "type": "related_to", "label": "对比"},
    {"s": "t_rip", "t": "t_ospf_basic", "type": "related_to", "label": "对比"},
    {"s": "t_collision_domain", "t": "t_broadcast_domain", "type": "related_to", "label": "对比"},
    {"s": "t_hub_vs_switch", "t": "t_collision_domain", "type": "related_to", "label": "对比"},
    {"s": "t_smtp", "t": "t_pop3", "type": "related_to", "label": "对比"},
    {"s": "t_pop3", "t": "t_imap", "type": "related_to", "label": "对比"},
    {"s": "t_nat_static", "t": "t_nat_dynamic", "type": "related_to", "label": "对比"},
    {"s": "t_nat_dynamic", "t": "t_pat", "type": "related_to", "label": "对比"},
    {"s": "t_acl_standard", "t": "t_acl_extended", "type": "related_to", "label": "对比"},
    {"s": "t_circuit_switch", "t": "t_packet_switch", "type": "related_to", "label": "对比"},
    {"s": "t_circuit_switch", "t": "t_message_switch", "type": "related_to", "label": "对比"},
    {"s": "t_vlan_concept", "t": "t_broadcast_domain", "type": "related_to", "label": "关联"},
    {"s": "t_trunk_8021q", "t": "t_vlan_config", "type": "related_to", "label": "关联"},
    {"s": "t_layer3_switch", "t": "t_vlan_config", "type": "related_to", "label": "关联"},
    {"s": "t_mac_table", "t": "t_vlan_concept", "type": "related_to", "label": "关联"},
    {"s": "t_vrrp", "t": "t_layer3_switch", "type": "related_to", "label": "关联"},
    {"s": "t_ospf_basic", "t": "t_abr", "type": "related_to", "label": "关联"},
    {"s": "t_abr", "t": "t_virtual_link", "type": "related_to", "label": "关联"},
    {"s": "t_ospf_packets", "t": "t_ospf_states", "type": "related_to", "label": "关联"},
    {"s": "t_redistribution", "t": "t_ospf_basic", "type": "related_to", "label": "关联"},
    {"s": "t_redistribution", "t": "t_rip", "type": "related_to", "label": "关联"},
    {"s": "t_dhcp", "t": "t_dhcp_dora", "type": "related_to", "label": "关联"},
    {"s": "t_dhcp_relay", "t": "t_dhcp", "type": "related_to", "label": "依赖"},
    {"s": "t_port_sec", "t": "t_vlan_config", "type": "related_to", "label": "关联"},

    # --- depends_on 关系 ---
    {"s": "t_vlan_config", "t": "t_vlan_concept", "type": "depends_on", "label": "依赖"},
    {"s": "t_trunk_8021q", "t": "t_vlan_config", "type": "depends_on", "label": "依赖"},
    {"s": "t_ospf_advanced", "t": "t_ospf_basic", "type": "depends_on", "label": "依赖"} if False else None,
    {"s": "t_stub_area", "t": "t_abr", "type": "depends_on", "label": "依赖"},
    {"s": "t_pat", "t": "t_nat_static", "type": "depends_on", "label": "依赖"},
    {"s": "t_floating_static", "t": "t_static_route", "type": "depends_on", "label": "依赖"},

    # --- 演进 ---
    {"s": "t_circuit_switch", "t": "t_message_switch", "type": "related_to", "label": "演进→"},
    {"s": "t_message_switch", "t": "t_packet_switch", "type": "related_to", "label": "演进→"},
]

# Remove None entries
EDGES = [e for e in EDGES if e is not None]

# ============================================================
# Part 4: 知识库条目
# ============================================================

KNOWLEDGE_BASE = [
    {"id": "kb_01", "category": "网络基础", "domainId": "net_fundamentals",
     "title": "OSI七层模型与TCP/IP四层模型",
     "tags": ["OSI", "TCP/IP", "协议模型", "分层", "七层"],
     "theory": "OSI七层模型：物理层→数据链路层→网络层→传输层→会话层→表示层→应用层。TCP/IP四层模型：网络接口层(物理+链路)→网际互连层(网络)→传输层→应用层(会话+表示+应用)。OSI是理论参考模型，TCP/IP是实际使用的协议族。",
     "commands": [],
     "configExample": None},
    {"id": "kb_02", "category": "网络基础", "domainId": "net_fundamentals",
     "title": "每层对应的协议",
     "tags": ["HTTP", "DNS", "FTP", "TCP", "UDP", "IP", "ARP", "以太网"],
     "theory": "应用层：HTTP/HTTPS(80/443)、DNS(53)、FTP(21)、SMTP(25)、Telnet(23)、SNMP(161)。传输层：TCP(可靠面向连接)、UDP(无连接快速)。网络层：IP(寻址路由)、ICMP(错误报告)、ARP(IP→MAC)、RARP(MAC→IP)。网络接口层：以太网(IEEE802.3)、PPP(点对点)。",
     "commands": [],
     "configExample": None},
    {"id": "kb_03", "category": "网络基础", "domainId": "net_fundamentals",
     "title": "交换机基础配置命令",
     "tags": ["enable", "configure", "hostname", "interface", "IOS"],
     "theory": "思科IOS基础命令是网络配置的起点。enable进入特权模式，conf t进入全局配置，hostname设主机名，interface进入接口配置，speed设速率，shutdown/no shutdown开关端口。",
     "commands": [
         {"cmd": "enable", "desc": "进入特权模式"},
         {"cmd": "configure terminal", "desc": "进入全局配置模式"},
         {"cmd": "hostname <名称>", "desc": "修改主机名"},
         {"cmd": "interface fa0/1", "desc": "进入1号端口配置"},
         {"cmd": "speed {10|100|auto}", "desc": "设置端口速率"},
         {"cmd": "shutdown / no shutdown", "desc": "关闭/开启端口"},
         {"cmd": "write", "desc": "保存配置"},
         {"cmd": "reload", "desc": "重启设备"},
         {"cmd": "show running-config", "desc": "查看运行配置"},
     ],
     "configExample": None},
    {"id": "kb_04", "category": "以太网与封装", "domainId": "ethernet_encap",
     "title": "IEEE802标准族",
     "tags": ["IEEE", "802.3", "802.11", "以太网", "CSMA/CD", "无线"],
     "theory": "IEEE802系列标准定义局域网技术规范。802.1概述/体系结构，802.2逻辑链路控制(LLC)，802.3以太网CSMA/CD，802.4令牌总线，802.5令牌环，802.11无线局域网(a/b/g/n)。符合802.3标准的局域网称为以太网。",
     "commands": [],
     "configExample": None},
    {"id": "kb_05", "category": "以太网与封装", "domainId": "ethernet_encap",
     "title": "数据封装与解封装全流程",
     "tags": ["封装", "解封装", "段", "包", "帧", "比特流", "UTF-8"],
     "theory": "发送端自上而下封装：应用层产生数据→表示层UTF-8编码→会话层建立会话→传输层加TCP/UDP头(段Segment)→网络层加IP头(包Packet)→链路层加帧头帧尾(帧Frame)→物理层转比特流。接收端自下而上解封装：物理层收信号→链路层检查FCS和MAC→网络层检查IP和TTL→传输层按端口分发→会话/表示/应用层还原数据。",
     "commands": [],
     "configExample": None},
    {"id": "kb_06", "category": "冲突域与广播域", "domainId": "collision_broadcast",
     "title": "冲突域与广播域详解",
     "tags": ["冲突域", "广播域", "Hub", "Switch", "Router", "CSMA/CD"],
     "theory": "冲突域：共享同一传输介质、可能发生数据冲突的设备集合。Hub(物理层)所有端口同一冲突域，Switch(链路层)每端口独立冲突域。广播域：能收到同一广播的设备集合。Switch不隔离广播域(转发到所有端口)，Router(网络层)天然隔离广播域。CSMA/CD规则：先听后发、边发边听、冲突停发、随机等待。",
     "commands": [],
     "configExample": None},
    {"id": "kb_07", "category": "交换技术", "domainId": "switching_tech",
     "title": "三种交换技术对比",
     "tags": ["电路交换", "报文交换", "分组交换", "PSTN", "互联网"],
     "theory": "电路交换：建立专用物理路径，通信期间独占，时延小但线路利用率低(如PSTN电话)。报文交换：存储-转发完整报文，无需建立连接但时延高(如电子邮件)。分组交换：数据分割成小包独立路由，资源利用率高(如互联网)。局域网交换分端口交换、帧交换(直通/存储转发)和信元交换(ATM)。",
     "commands": [],
     "configExample": None},
    {"id": "kb_08", "category": "跨交换机VLAN", "domainId": "vlan_trunk",
     "title": "跨交换机VLAN完整配置",
     "tags": ["VLAN", "Trunk", "802.1Q", "Access", "switchport"],
     "theory": "跨交换机VLAN需三步：1.在两台交换机上创建相同VLAN(vlan 10 + name Sales)；2.将PC接入端口设为Access模式(switchport mode access + access vlan 10)；3.交换机间互联端口设为Trunk模式(switchport mode trunk + allowed vlan 10,20)。Trunk使用802.1Q标准在帧中插入VLAN标签。",
     "commands": [
         {"cmd": "vlan 10", "desc": "创建VLAN 10"},
         {"cmd": "name Sales", "desc": "VLAN命名为Sales"},
         {"cmd": "switchport mode access", "desc": "端口设为Access模式"},
         {"cmd": "switchport access vlan 10", "desc": "端口划入VLAN 10"},
         {"cmd": "switchport mode trunk", "desc": "端口设为Trunk模式"},
         {"cmd": "switchport trunk allowed vlan 10,20", "desc": "Trunk允许VLAN 10和20"},
         {"cmd": "show vlan brief", "desc": "查看VLAN信息"},
         {"cmd": "show interfaces trunk", "desc": "检查Trunk状态"},
     ],
     "configExample": "! SW1 VLAN创建\nSW1(config)# vlan 10\nSW1(config-vlan)# name Sales\nSW1(config-vlan)# exit\n\n! SW1 接入端口\nSW1(config)# interface fa0/1\nSW1(config-if)# switchport mode access\nSW1(config-if)# switchport access vlan 10\nSW1(config-if)# no shutdown\n\n! SW1 Trunk端口\nSW1(config)# interface fa0/24\nSW1(config-if)# switchport mode trunk\nSW1(config-if)# switchport trunk allowed vlan 10,20"},
    {"id": "kb_09", "category": "跨交换机VLAN", "domainId": "vlan_trunk",
     "title": "三层交换机与SVI配置",
     "tags": ["三层交换", "SVI", "ip routing", "sdm prefer", "VLAN间路由"],
     "theory": "三层交换机通过SVI(Switch Virtual Interface)实现VLAN间路由。每个VLAN的SVI需配独立网段的IP(不能相同)。配置流程：sdm prefer routing→reload→ip routing→创建VLAN→配SVI IP。不同VLAN的SVI不能配同一IP或同一网段，否则路由表混乱。Super VLAN(VLAN聚合)可让多个子VLAN共享一个网关IP节省地址。",
     "commands": [
         {"cmd": "sdm prefer routing", "desc": "切换SDM模板为路由模式(3560)"},
         {"cmd": "ip routing", "desc": "启用三层路由功能"},
         {"cmd": "interface vlan 10", "desc": "创建VLAN 10的SVI接口"},
         {"cmd": "ip address 192.168.10.1 255.255.255.0", "desc": "配置SVI IP地址"},
     ],
     "configExample": "! 3560三层交换配置\nS1(config)# sdm prefer routing\nS1# reload\nS1(config)# ip routing\nS1(config)# interface vlan 10\nS1(config-if)# ip address 192.168.10.1 255.255.255.0\nS1(config-if)# no shutdown"},
    {"id": "kb_10", "category": "STP与链路聚合", "domainId": "stp_etherchannel",
     "title": "生成树协议(STP)完整配置",
     "tags": ["STP", "PVST+", "根桥", "PortFast", "spanning-tree"],
     "theory": "STP通过逻辑阻塞端口防止二层环路。核心步骤：选举根桥(优先级最小)→确定根端口(到根桥Cost最小)→确定指定端口→阻塞剩余端口。思科PVST+每VLAN独立实例。优先级默认32768，数值越小越优先。PortFast让接入端口跳过监听/学习状态直接转发。",
     "commands": [
         {"cmd": "spanning-tree mode pvst", "desc": "启用PVST+模式"},
         {"cmd": "spanning-tree vlan 1 priority 4096", "desc": "设置桥优先级(越小越优先)"},
         {"cmd": "spanning-tree portfast", "desc": "接入端口快速转发"},
         {"cmd": "show spanning-tree summary", "desc": "查看STP摘要"},
     ],
     "configExample": "! 根桥配置\nSwitch3(config)# spanning-tree mode pvst\nSwitch3(config)# spanning-tree vlan 1 priority 4096\n\n! 接入端口\nSwitch3(config)# interface fa0/3\nSwitch3(config-if)# switchport mode access\nSwitch3(config-if)# spanning-tree portfast\n\n! 中继端口\nSwitch3(config)# interface range fa0/1 - 2\nSwitch3(config-if-range)# switchport mode trunk"},
    {"id": "kb_11", "category": "STP与链路聚合", "domainId": "stp_etherchannel",
     "title": "EtherChannel链路聚合配置",
     "tags": ["EtherChannel", "channel-group", "链路聚合", "Port-channel"],
     "theory": "EtherChannel将多条物理链路捆绑为一条逻辑链路提高带宽和冗余。配置要点：物理口必须先shutdown，配完全一致的switchport/trunk/vlan配置，再加channel-group，最后no shutdown。成员端口配置不一致会显示suspended(s)。",
     "commands": [
         {"cmd": "interface port-channel 1", "desc": "创建逻辑Port-channel接口"},
         {"cmd": "channel-group 1 mode on", "desc": "物理口加入通道组"},
         {"cmd": "show etherchannel summary", "desc": "查看EtherChannel状态"},
     ],
     "configExample": "! 先配物理口一致\nSwitch(config)# interface range fa0/1 - 2\nSwitch(config-if-range)# shutdown\nSwitch(config-if-range)# switchport mode trunk\nSwitch(config-if-range)# channel-group 1 mode on\nSwitch(config-if-range)# no shutdown\n\n! 再配Po口\nSwitch(config)# interface port-channel 1\nSwitch(config-if)# switchport mode trunk"},
    {"id": "kb_12", "category": "路由协议", "domainId": "routing_basic",
     "title": "静态路由与浮动静态路由",
     "tags": ["静态路由", "ip route", "浮动路由", "AD", "默认路由"],
     "theory": "静态路由：ip route 目的网段 子网掩码 下一跳IP。浮动静态路由通过设更高AD值(管理距离)实现备份，主路由失效时备用路由自动生效。默认路由：ip route 0.0.0.0 0.0.0.0 下一跳。同一网段=同一广播域。业务IP给客户，互联IP给路由器互联，管理IP给交换机远程管理。",
     "commands": [
         {"cmd": "ip route 192.168.2.0 255.255.255.0 10.0.0.2", "desc": "静态路由到192.168.2.0网段"},
         {"cmd": "ip route 192.168.2.0 255.255.255.0 10.0.0.3 200", "desc": "浮动静态路由AD=200(备用)"},
         {"cmd": "ip route 0.0.0.0 0.0.0.0 10.0.0.1", "desc": "默认路由"},
     ],
     "configExample": None},
    {"id": "kb_13", "category": "路由协议", "domainId": "routing_basic",
     "title": "RIP协议配置与不连续子网问题",
     "tags": ["RIP", "跳数", "自动汇总", "no auto-summary", "不连续子网"],
     "theory": "RIP是距离矢量协议，度量参数为跳数(Hop Count)，最大15跳(16=不可达)。RIPv2默认开启自动汇总(auto-summary)，在不连续子网环境下会导致路由冲突(R1和R3都向R2宣告同一主类网络)。解决方案：使用no auto-summary关闭自动汇总，并逐个子网宣告。",
     "commands": [
         {"cmd": "router rip", "desc": "启用RIP路由进程"},
         {"cmd": "version 2", "desc": "指定RIPv2"},
         {"cmd": "no auto-summary", "desc": "关闭自动汇总(关键！)"},
         {"cmd": "network 192.168.1.0", "desc": "宣告直连主类网络"},
     ],
     "configExample": "! R1 不连续子网配置\nR1(config)# router rip\nR1(config-router)# version 2\nR1(config-router)# no auto-summary\nR1(config-router)# network 172.16.0.0\nR1(config-router)# network 12.0.0.0"},
    {"id": "kb_14", "category": "路由协议", "domainId": "routing_basic",
     "title": "OSPF基础与Cost计算",
     "tags": ["OSPF", "Cost", "链路状态", "Area", "SPF"],
     "theory": "OSPF是链路状态IGP协议，度量参数为Cost(开销)，计算公式：Cost = 参考带宽(默认100Mbps) / 接口带宽。带宽越高Cost越低路径越优先。例如100M链路Cost=1，10M链路Cost=10。OSPF使用Area分层设计，Area 0是骨干区域，所有非骨干区域必须直连Area 0。",
     "commands": [
         {"cmd": "router ospf 1", "desc": "启用OSPF进程1"},
         {"cmd": "network 192.168.1.0 0.0.0.255 area 0", "desc": "宣告子网到Area 0"},
         {"cmd": "show ip ospf neighbor", "desc": "查看OSPF邻居"},
         {"cmd": "show ip route ospf", "desc": "查看OSPF路由表"},
     ],
     "configExample": None},
    {"id": "kb_15", "category": "OSPF深入", "domainId": "ospf_advanced",
     "title": "OSPF虚链路详解",
     "tags": ["虚链路", "virtual-link", "ABR", "Area 0", "单播"],
     "theory": "虚链路是Area 0的逻辑延伸，用于解决非骨干区域不直连Area 0的问题。与普通链路区别：1.本质：虚链路传递LSA不传业务数据；2.报文：使用单播(普通链路用组播224.0.0.5)；3.配置：在OSPF进程下area X virtual-link router-id；4.思科虚链路建立后抑制Hello包。ABR(区域边界路由器)连接Area 0和其他区域，维护多份LSDB。",
     "commands": [
         {"cmd": "area 1 virtual-link <router-id>", "desc": "配置虚链路到指定路由器"},
     ],
     "configExample": None},
    {"id": "kb_16", "category": "OSPF深入", "domainId": "ospf_advanced",
     "title": "OSPF五种分组与邻居状态机",
     "tags": ["Hello", "DBD", "LSR", "LSU", "邻居状态", "Full"],
     "theory": "五种分组：Hello(发现维护邻居)、DBD(数据库描述)、LSR(链路状态请求)、LSU(链路状态更新)、LSAck(确认)。邻居状态机：Down→Init(收到Hello)→2-Way(双向Hello)→ExStart(主从选举)→Exchange(交换DBD)→Loading(请求LSU)→Full(LSDB同步完成)。三张核心表：邻居表、LSDB、路由表。",
     "commands": [
         {"cmd": "show ip ospf neighbor", "desc": "查看邻居状态"},
         {"cmd": "show ip ospf database", "desc": "查看LSDB"},
     ],
     "configExample": None},
    {"id": "kb_17", "category": "OSPF深入", "domainId": "ospf_advanced",
     "title": "RIP/OSPF路由重分布",
     "tags": ["重分布", "redistribute", "边界路由器", "route-map"],
     "theory": "边界路由器在不同路由协议间翻译路由信息。单向重分布：仅将一个协议的路由注入另一个。双向重分布：两个协议互相注入。需注意防环路，可用route-map过滤。配置：在边界路由器的OSPF进程下redistribute rip subnets，在RIP进程下redistribute ospf 1 metric 1。",
     "commands": [
         {"cmd": "redistribute rip subnets", "desc": "OSPF中重分布RIP路由"},
         {"cmd": "redistribute ospf 1 metric 1", "desc": "RIP中重分布OSPF路由"},
     ],
     "configExample": None},
    {"id": "kb_18", "category": "OSPF深入", "domainId": "ospf_advanced",
     "title": "OSPF Stub/NSSA区域",
     "tags": ["Stub", "Totally Stub", "NSSA", "LSA类型"],
     "theory": "Stub区域：阻止5类LSA(外部路由)进入，ABR自动注入默认路由。Totally Stub区域：阻止3类和5类LSA，仅保留区域内路由和默认路由。NSSA(Not-So-Stubby Area)：允许引入外部路由(7类LSA)但阻止5类LSA。配置：area X stub / area X stub no-summary(Totally Stub)。",
     "commands": [
         {"cmd": "area 1 stub", "desc": "配置为Stub区域"},
         {"cmd": "area 1 stub no-summary", "desc": "配置为Totally Stub区域"},
         {"cmd": "area 1 nssa", "desc": "配置为NSSA区域"},
     ],
     "configExample": None},
    {"id": "kb_19", "category": "VRRP与DHCP", "domainId": "vrrp_dhcp",
     "title": "DHCP DORA流程详解",
     "tags": ["DHCP", "DORA", "Discover", "Offer", "Request", "ACK", "UDP 67/68"],
     "theory": "D-Discover：客户端广播(0.0.0.0→255.255.255.255)寻找DHCP服务器。O-Offer：服务器回复可用IP+租期+Server ID。R-Request：客户端广播选择某服务器IP，拒绝其他Offer。A-ACK：服务器确认分配，客户端绑定IP。服务器端口UDP 67，客户端端口UDP 68。",
     "commands": [
         {"cmd": "ip dhcp pool <名称>", "desc": "创建DHCP地址池"},
         {"cmd": "network 192.168.1.0 255.255.255.0", "desc": "指定可分配网段"},
         {"cmd": "default-router 192.168.1.1", "desc": "指定默认网关"},
         {"cmd": "dns-server 8.8.8.8", "desc": "指定DNS服务器"},
         {"cmd": "ip dhcp excluded-address 192.168.1.1 192.168.1.10", "desc": "排除不分配的地址"},
     ],
     "configExample": "! 单网段DHCP配置\nRouter(config)# ip dhcp excluded-address 192.168.1.1 192.168.1.10\nRouter(config)# ip dhcp pool LAN\nRouter(dhcp-config)# network 192.168.1.0 255.255.255.0\nRouter(dhcp-config)# default-router 192.168.1.1\nRouter(dhcp-config)# dns-server 8.8.8.8"},
    {"id": "kb_20", "category": "VRRP与DHCP", "domainId": "vrrp_dhcp",
     "title": "DHCP中继(ip helper-address)",
     "tags": ["DHCP中继", "ip helper-address", "Option 82", "跨网段"],
     "theory": "路由器默认不转发广播，跨网段客户端无法联系远程DHCP服务器。解决方案：在路由器接口配置ip helper-address指向DHCP服务器IP，路由器将DHCP广播转为单播转发。Option 82记录客户端物理位置信息。ASA防火墙也支持DHCP中继。",
     "commands": [
         {"cmd": "ip helper-address 10.0.0.100", "desc": "转发DHCP广播到指定服务器"},
     ],
     "configExample": "! DHCP中继配置\nRouter(config)# interface gi0/0\nRouter(config-if)# ip helper-address 10.0.0.100"},
    {"id": "kb_21", "category": "邮件协议", "domainId": "email_proto",
     "title": "SMTP/POP3/IMAP对比",
     "tags": ["SMTP", "POP3", "IMAP", "邮件", "端口"],
     "theory": "SMTP(端口25/465/587)：发送邮件和中继，推送协议。POP3(端口110/995)：下载到本地可离线，下载后可删除服务器副本，不支持多设备同步。IMAP(端口143/993)：服务器端管理，支持多设备同步状态(已读/未读/文件夹)，需要持续联网。",
     "commands": [],
     "configExample": None},
    {"id": "kb_22", "category": "ACL", "domainId": "acl",
     "title": "ACL访问控制列表详解",
     "tags": ["ACL", "标准ACL", "扩展ACL", "通配符掩码", "permit", "deny"],
     "theory": "ACL逐条匹配，命中即停。标准ACL(1-99)仅匹配源IP，控制粒度粗。扩展ACL(100-199)匹配源IP+目的IP+协议+端口，细粒度控制。通配符掩码：0=精确匹配，1=忽略。隐含拒绝：末尾默认deny any。ACL顺序至关重要，先deny any后permit全部失效。扩展ACL应配在靠近源端接口。",
     "commands": [
         {"cmd": "access-list 10 deny host 192.168.1.50", "desc": "标准ACL拒绝特定主机"},
         {"cmd": "access-list 10 permit any", "desc": "标准ACL允许其他"},
         {"cmd": "access-list 101 deny tcp 192.168.1.0 0.0.0.255 any eq 23", "desc": "扩展ACL禁止Telnet"},
         {"cmd": "access-list 101 permit ip any any", "desc": "扩展ACL允许其他IP"},
         {"cmd": "ip access-group 10 in", "desc": "接口应用ACL(入方向)"},
     ],
     "configExample": "! 扩展ACL示例\nRouter(config)# access-list 101 deny tcp 192.168.1.0 0.0.0.255 any eq 23\nRouter(config)# access-list 101 permit tcp 192.168.1.0 0.0.0.255 any eq 80\nRouter(config)# access-list 101 permit ip any any\nRouter(config)# interface gi0/0\nRouter(config-if)# ip access-group 101 in"},
    {"id": "kb_23", "category": "ACL", "domainId": "acl",
     "title": "时间ACL与高级ACL",
     "tags": ["time-range", "时间ACL", "NBAR2", "ISE"],
     "theory": "时间ACL通过time-range定义时间段绑定ACL规则。如work-hours定义周一到周五9-17点，绑定deny规则限制上班时间访问。高级方案：Cisco ISE基于身份的ACL、NBAR2应用级识别。",
     "commands": [
         {"cmd": "time-range work-hours", "desc": "定义时间范围"},
         {"cmd": "periodic weekdays 9:00 to 17:00", "desc": "设置工作日时间"},
         {"cmd": "access-list 110 deny tcp any any eq 80 time-range work-hours", "desc": "时间ACL禁止上班上网"},
     ],
     "configExample": None},
    {"id": "kb_24", "category": "端口安全", "domainId": "port_security",
     "title": "交换机端口安全配置",
     "tags": ["port-security", "sticky", "MAC地址", "端口安全"],
     "theory": "端口安全限制端口允许的MAC地址数量，防止未授权设备接入。switchport port-security启用安全，mac-address sticky自动学习当前MAC为安全地址。违例处理：protect(丢弃不告警)、restrict(丢弃+告警)、shutdown(关闭端口)。",
     "commands": [
         {"cmd": "switchport mode access", "desc": "先设为Access模式(必须)"},
         {"cmd": "switchport port-security", "desc": "启用端口安全"},
         {"cmd": "switchport port-security mac-address sticky", "desc": "自动学习MAC地址"},
         {"cmd": "switchport port-security maximum 2", "desc": "最大允许2个MAC"},
         {"cmd": "show port-security", "desc": "查看端口安全状态"},
     ],
     "configExample": "! 端口安全配置\nSwitch(config)# interface fa0/1\nSwitch(config-if)# switchport mode access\nSwitch(config-if)# switchport port-security\nSwitch(config-if)# switchport port-security mac-address sticky\nSwitch(config-if)# switchport port-security maximum 2"},
    {"id": "kb_25", "category": "NAT", "domainId": "nat",
     "title": "NAT三种模式配置",
     "tags": ["NAT", "静态NAT", "动态NAT", "PAT", "overload", "ip nat"],
     "theory": "NAT(网络地址转换)解决IPv4地址短缺。静态NAT：一对一固定映射(对外服务器)。动态NAT：地址池多对多映射(轮流使用)。PAT(端口地址转换/Overload)：多对一端口复用，多内网设备共用一个公网IP通过端口号区分，最常用。必须先定义inside/outside接口。",
     "commands": [
         {"cmd": "ip nat inside", "desc": "标记内部接口"},
         {"cmd": "ip nat outside", "desc": "标记外部接口"},
         {"cmd": "ip nat inside source static 192.168.1.100 203.0.113.5", "desc": "静态NAT一对一映射"},
         {"cmd": "ip nat inside source list 1 interface gi0/0 overload", "desc": "PAT端口复用(最常用)"},
         {"cmd": "show ip nat translations", "desc": "查看NAT转换表"},
     ],
     "configExample": "! PAT配置(最常用)\nRouter(config)# access-list 1 permit 192.168.1.0 0.0.0.255\nRouter(config)# ip nat inside source list 1 interface gi0/0 overload\n\n! 标记接口\nRouter(config)# interface gi0/0\nRouter(config-if)# ip nat inside\nRouter(config)# interface s0/0/0\nRouter(config-if)# ip nat outside"},
    {"id": "kb_26", "category": "网络命令", "domainId": "net_commands",
     "title": "ping与ipconfig命令",
     "tags": ["ping", "ipconfig", "ICMP", "网络诊断"],
     "theory": "ping：ICMP回显请求测试连通性。-t持续ping，-a解析NetBIOS主机名，-n count指定包数。ipconfig：/all显示TCP/IP详细信息(含MAC、DHCP服务器)，/release释放DHCP租约，/renew续租，/flushdns清除DNS缓存。",
     "commands": [
         {"cmd": "ping 192.168.1.1 -t", "desc": "持续ping目标"},
         {"cmd": "ping 192.168.1.1 -n 20", "desc": "发送20个测试包"},
         {"cmd": "ipconfig /all", "desc": "查看详细TCP/IP配置"},
         {"cmd": "ipconfig /release", "desc": "释放DHCP地址"},
         {"cmd": "ipconfig /renew", "desc": "续租DHCP地址"},
         {"cmd": "ipconfig /flushdns", "desc": "清除DNS缓存"},
     ],
     "configExample": None},
    {"id": "kb_27", "category": "网络命令", "domainId": "net_commands",
     "title": "二进制与十六进制转换",
     "tags": ["二进制", "十六进制", "十进制", "按权相加"],
     "theory": "二进制转十进制用按权相加法：每位乘以2的相应次幂再相加。如1011→1×2³+0×2²+1×2¹+1×2⁰=11。十六进制转十进制类似：每位乘以16的相应次幂，A-F代表10-15。如38A→3×16²+8×16¹+10×16⁰=906。",
     "commands": [],
     "configExample": None},
    {"id": "kb_28", "category": "跨交换机VLAN", "domainId": "vlan_trunk",
     "title": "MAC地址表工作原理",
     "tags": ["MAC地址表", "自学习", "泛洪", "老化"],
     "theory": "交换机地址表工作三步骤：1.自学习：收到帧时提取源MAC记录端口对应关系；2.查表转发：目的MAC匹配则单播转发，不匹配则泛洪(除接收口外所有端口)；3.老化机制：动态表项默认300秒过期，未刷新则删除。地址表项包含VLAN ID，确保同VLAN隔离。",
     "commands": [
         {"cmd": "show mac address-table", "desc": "查看MAC地址表"},
     ],
     "configExample": None},
    {"id": "kb_29", "category": "跨交换机VLAN", "domainId": "vlan_trunk",
     "title": "私有IP地址范围",
     "tags": ["私有IP", "A类", "B类", "C类", "RFC1918"],
     "theory": "A类：10.0.0.0/8(10.0.0.0-10.255.255.255)，1600万+地址，大型企业/数据中心。B类：172.16.0.0/12(172.16.0.0-172.31.255.255)，16个B类网络，中型企业/Docker默认。C类：192.168.0.0/16(192.168.0.0-192.168.255.255)，256个C类网络，家庭/小型办公最常用。",
     "commands": [],
     "configExample": None},
    {"id": "kb_30", "category": "OSPF深入", "domainId": "ospf_advanced",
     "title": "Loopback接口与OSPF",
     "tags": ["Loopback", "/32", "掩码", "虚拟接口"],
     "theory": "Loopback是虚拟接口永远UP，常用于路由器ID和稳定性测试。误区：Loopback不必配/32，可以配任何掩码。但OSPF对Loopback特殊处理：默认将宣告的Loopback IP改为/32主机路由，不管实际掩码是什么。如需保留原始掩码，需用ip ospf network point-to-point。",
     "commands": [
         {"cmd": "interface loopback 0", "desc": "创建Loopback接口"},
         {"cmd": "ip address 1.1.1.1 255.255.255.255", "desc": "配置Loopback IP"},
         {"cmd": "ip ospf network point-to-point", "desc": "保留原始掩码宣告"},
     ],
     "configExample": None},
]

print(f"[INFO] 定义了 {len(DOMAINS)} 个领域, {len(NODES)} 个节点, {len(EDGES)} 条边, {len(KNOWLEDGE_BASE)} 个知识库条目")

# ============================================================
# Part 5: Q&A 问答对生成
# ============================================================

# 硬编码核心问答对
QA_HARDCODED = [
    # 网络基础
    {"q": "什么是计算机网络？", "a": "将地理位置不同的具有独立功能的多台计算机及其外部设备，通过通信线路连接起来的计算机集合。功能包括资源共享、数据通信、均衡负载、分布式处理、提高可靠性和集中处理。", "kw": ["计算机网络", "定义", "功能", "LAN", "WAN"], "cat": "网络基础", "diff": "基础"},
    {"q": "计算机网络按地理位置怎么分类？", "a": "按地理位置划分：局域网(LAN)、城域网(MAN)、广域网(WAN)。按传输介质：有线(双绞线、同轴电缆、光纤)和无线(微波、红外、卫星)。按拓扑结构：总线型、星形、环形、树状型、网状型。按交换方式：电路交换、分组交换、报文交换。", "kw": ["分类", "LAN", "MAN", "WAN", "拓扑", "交换"], "cat": "网络基础", "diff": "基础"},
    {"q": "OSI七层模型是哪七层？", "a": "物理层→数据链路层→网络层→传输层→会话层→表示层→应用层。由ISO国际标准化组织制定。每层功能独立，逐层封装，对等通信。", "kw": ["OSI", "七层", "模型", "物理层", "传输层", "应用层"], "cat": "网络基础", "diff": "基础"},
    {"q": "TCP/IP四层模型和OSI七层模型有什么区别？", "a": "TCP/IP将OSI的七层简化为四层：物理层+数据链路层合并为网络接口层，网络层对应网际互连层(IP/ARP/IGMP)，传输层不变(TCP/UDP)，会话层+表示层+应用层合并为应用层(DNS/FTP/HTTP)。OSI是理论参考模型，TCP/IP是实际使用的协议族。", "kw": ["TCP/IP", "OSI", "四层", "七层", "对比", "模型"], "cat": "网络基础", "diff": "基础"},
    {"q": "TCP和UDP有什么区别？", "a": "TCP：面向连接、可靠、三次握手建立连接、确认重传、有序到达，适用文件传输/邮件/Web浏览。UDP：无连接、不可靠、开销小速度快，适用语音/视频/直播/DNS查询。", "kw": ["TCP", "UDP", "区别", "可靠", "连接", "三次握手"], "cat": "网络基础", "diff": "基础"},
    {"q": "应用层有哪些常见协议？", "a": "HTTP/HTTPS(超文本传输，80/443)、DNS(域名解析，53)、FTP(文件传输，21)、SMTP(邮件发送，25)、Telnet(远程登录，23)、SNMP(网络管理，161)。", "kw": ["应用层", "HTTP", "DNS", "FTP", "SMTP", "Telnet", "SNMP", "协议"], "cat": "网络基础", "diff": "基础"},
    {"q": "什么是ARP协议？", "a": "ARP(地址解析协议)，功能是通过已知IP地址解析出同一物理网络上对应的MAC地址。RARP是反向ARP，从MAC地址解析IP地址。", "kw": ["ARP", "MAC地址", "IP地址", "解析", "RARP"], "cat": "网络基础", "diff": "基础"},
    {"q": "交换机有哪些基础配置命令？", "a": "enable进入特权模式，conf t进入全局配置，hostname改主机名，interface fa0/1进入端口，speed设速率，shutdown/no shutdown开关端口，write保存，reload重启，show running-config查看配置。", "kw": ["交换机", "命令", "enable", "configure", "interface", "IOS"], "cat": "网络基础", "diff": "基础"},
    # 以太网与封装
    {"q": "什么是CSMA/CD？", "a": "载波侦听多路访问/冲突检测，早期以太网的介质访问控制方法。三条规则：先听后发(Carrier Sense)——说话前听有无人说话；边发边听(Collision Detect)——说话同时监听冲突；冲突停发——检测到冲突立即停止并发送阻塞信号，随机等待后重试。", "kw": ["CSMA/CD", "冲突检测", "以太网", "先听后发", "边发边听"], "cat": "以太网与封装", "diff": "基础"},
    {"q": "什么是VLAN？有什么作用？", "a": "VLAN(虚拟局域网)将物理网络划分为多个逻辑子网。作用：1.隔离广播域限制广播流量提高性能；2.增强安全性逻辑分组控制数据流；3.简化管理灵活逻辑分组比物理布线更方便。IEEE 802.1Q是VLAN标签标准。可按端口、IP地址、MAC地址划分。", "kw": ["VLAN", "虚拟局域网", "广播域", "802.1Q", "隔离"], "cat": "以太网与封装", "diff": "基础"},
    {"q": "数据封装的过程是什么？", "a": "发送端自上而下：应用层→表示层(UTF-8编码)→会话层→传输层(加TCP/UDP头，数据变为段Segment)→网络层(加IP头，变为包Packet)→链路层(加帧头帧尾，变为帧Frame)→物理层(转为比特流)。接收端自下而上解封装。就像寄快递：写信→层层打包→运输→层层拆包→读信。", "kw": ["封装", "解封装", "段", "包", "帧", "比特流", "Segment", "Packet", "Frame"], "cat": "以太网与封装", "diff": "基础"},
    {"q": "封装过程中每层的数据形态叫什么？", "a": "传输层→段(Segment)，网络层→包(Packet)，数据链路层→帧(Frame)，物理层→比特流(Bits)。每层添加头部信息：传输层加源/目的端口和序列号，网络层加源/目的IP和TTL，链路层加源/目的MAC和FCS校验。", "kw": ["数据形态", "段", "包", "帧", "比特流", "头部"], "cat": "以太网与封装", "diff": "基础"},
    {"q": "UTF-8编码在数据封装中的作用是什么？", "a": "表示层将Unicode字符转换为UTF-8字节流作为数据的有效载荷(Payload)。例如'你好'→UTF-8编码为E4 BD A0 E5 A5 BD(十六进制)。UTF-8编码决定了原始数据变成什么样的二进制，封装决定这些二进制被包裹在什么样的'信封'里。", "kw": ["UTF-8", "编码", "表示层", "Payload", "有效载荷"], "cat": "以太网与封装", "diff": "进阶"},
    # 冲突域与广播域
    {"q": "什么是冲突域？", "a": "冲突域是网络中所有共享同一传输介质、并且可能发生数据冲突的设备集合。在这个区域内，如果一台设备发数据，其他设备都必须监听，且可能发生撞车。集线器(Hub)连接的所有设备处于同一冲突域；交换机的每个端口是独立的冲突域。", "kw": ["冲突域", "Collision Domain", "Hub", "交换机", "共享介质"], "cat": "冲突域与广播域", "diff": "基础"},
    {"q": "什么是广播域？", "a": "广播域是能接收到同样广播消息的设备集合。交换机(Switch)不隔离广播域，收到广播帧(目标MAC FF:FF:FF:FF:FF:FF)会转发到除接收口外所有端口。路由器(Router)是隔离广播域的天然屏障，不转发二层广播。要隔绝广播必须用路由器或VLAN。", "kw": ["广播域", "Broadcast Domain", "交换机", "路由器", "广播", "隔离"], "cat": "冲突域与广播域", "diff": "基础"},
    {"q": "Hub和Switch在冲突域上有什么区别？", "a": "Hub(集线器)是物理层设备，没有智能，把收到的电信号放大转发给所有端口，所有端口在同一冲突域。Switch(交换机)是数据链路层设备，每个端口是独立冲突域，提供专用带宽，从根本上隔离了冲突域。交换机让每个端口变成独立的'私有通道'，全双工模式下不再需要CSMA/CD。", "kw": ["Hub", "Switch", "冲突域", "物理层", "链路层", "集线器"], "cat": "冲突域与广播域", "diff": "基础"},
    {"q": "总线型拓扑是什么？有什么问题？", "a": "所有计算机连接到一根同轴电缆(总线)上，这就是共享介质。同一时间只能一台发送数据，其他人都在监听。问题：两人同时说话数据会冲突碰撞，就像办公室里所有人共用一张大桌子和一个大喇叭。", "kw": ["总线型", "拓扑", "共享介质", "同轴电缆", "冲突"], "cat": "冲突域与广播域", "diff": "基础"},
    # 交换技术
    {"q": "电路交换、报文交换和分组交换有什么区别？", "a": "电路交换：建立专用物理路径，通信期间独占，时延小稳定但线路利用率低(如PSTN电话)。报文交换：存储-转发完整报文，无需连接但时延高(如电子邮件)。分组交换：数据分割成小包独立路由选择，资源利用率高(如互联网)。分组交换是现代互联网的基础。", "kw": ["电路交换", "报文交换", "分组交换", "对比", "PSTN", "互联网"], "cat": "交换技术", "diff": "基础"},
    {"q": "局域网交换技术有哪几种？", "a": "1.端口交换：基于物理层调整端口连接实现负载平衡。2.帧交换：最广泛应用，分直通交换(只读前14字节即转发，线速)和存储转发(完整读取验错)。3.信元交换：固定53字节信元，如ATM异步传输模式，带宽可达数Gbps。", "kw": ["局域网交换", "帧交换", "端口交换", "信元交换", "ATM", "直通", "存储转发"], "cat": "交换技术", "diff": "进阶"},
    {"q": "SDN和NFV是什么？", "a": "SDN(软件定义网络)：通过集中式控制器实现网络的灵活控制和动态调整，控制平面与数据平面分离。NFV(网络功能虚拟化)：将网络功能从专用硬件解耦到软件运行，提高灵活性降低成本。两者都是现代网络发展趋势。", "kw": ["SDN", "NFV", "软件定义", "虚拟化", "控制器"], "cat": "交换技术", "diff": "进阶"},
    # VLAN
    {"q": "如何配置跨交换机VLAN？", "a": "三步：1.两台交换机创建相同VLAN(vlan 10 + name Sales)；2.PC接入端口设为Access(switchport mode access + access vlan 10)；3.交换机间互联端口设为Trunk(switchport mode trunk + allowed vlan 10,20)。必须保证VLAN ID和名称一致。", "kw": ["跨交换机", "VLAN配置", "Trunk", "Access", "switchport"], "cat": "跨交换机VLAN", "diff": "基础"},
    {"q": "Trunk端口是什么？802.1Q做什么？", "a": "Trunk是交换机间的连接模式，允许多个VLAN的数据通过同一条链路传输。802.1Q是IEEE标准，在以太网帧中插入4字节VLAN标签(Tag)，包含VLAN ID，实现逻辑信道复用。配置命令：switchport mode trunk + switchport trunk allowed vlan 10,20。", "kw": ["Trunk", "802.1Q", "VLAN标签", "Tag", "多VLAN"], "cat": "跨交换机VLAN", "diff": "基础"},
    {"q": "三层交换机SVI为什么不能配同一个IP？", "a": "IP地址必须唯一，两个VLAN配同一IP交换机会报'IP地址重叠'。路由表也无法建立：VLAN 10配192.168.10.1/24会产生直连路由，VLAN 20也配同网段则路由表混乱不知该从哪个VLAN转发。正确做法：每个VLAN配独立网段。特殊情况Super VLAN可让多个子VLAN共享一个网关IP。", "kw": ["SVI", "三层交换", "IP地址", "唯一", "Super VLAN", "路由表"], "cat": "跨交换机VLAN", "diff": "进阶"},
    {"q": "交换机的MAC地址表是怎么工作的？", "a": "三步：1.自学习——收到帧提取源MAC记录端口对应关系；2.查表转发——目的MAC匹配则单播转发，不匹配则泛洪到除接收口外所有端口；3.老化——动态表项默认300秒过期删除。表项包含VLAN ID确保隔离。BPDU等特殊帧不参与地址学习。", "kw": ["MAC地址表", "自学习", "泛洪", "老化", "300秒"], "cat": "跨交换机VLAN", "diff": "基础"},
    {"q": "3560三层交换机配置VLAN间路由的完整流程？", "a": "sdm prefer routing→reload(切换SDM模板)→ip routing(启用路由)→EtherChannel先物理口加channel-group再Po口配L2 Trunk(encapsulation dot1q)→vlan X创建VLAN→SVI配IP。连L2交换机必须L2 Trunk不能no switchport。VLAN未创建则SVI起不来、trunk不active。", "kw": ["3560", "sdm prefer", "ip routing", "EtherChannel", "SVI", "三层交换"], "cat": "跨交换机VLAN", "diff": "进阶"},
    # STP
    {"q": "生成树协议STP的作用和原理是什么？", "a": "STP通过逻辑阻塞端口防止二层环路导致的广播风暴。核心步骤：1.选举根桥(桥优先级+MAC最小)→2.确定根端口(到根桥Cost最小)→3.确定指定端口→4.阻塞剩余端口。思科默认PVST+每VLAN独立实例。优先级默认32768，越小越优先。", "kw": ["STP", "生成树", "环路", "广播风暴", "根桥", "阻塞"], "cat": "STP与链路聚合", "diff": "基础"},
    {"q": "如何配置STP根桥？", "a": "spanning-tree mode pvst启用PVST+，spanning-tree vlan 1 priority 4096设置优先级(默认32768越小越优先)。接入PC端口加spanning-tree portfast跳过监听/学习状态直接转发。中继端口配switchport mode trunk。", "kw": ["STP", "根桥", "priority", "PortFast", "spanning-tree"], "cat": "STP与链路聚合", "diff": "基础"},
    {"q": "PortFast是什么？为什么需要？", "a": "PortFast让接入端口跳过STP的监听(Listening)和学习(Learning)状态直接进入转发(Forwarding)状态，避免PC接入时等待30-50秒。只应配在连接PC/服务器的接入端口，不能配在交换机间互联端口，否则可能导致环路。", "kw": ["PortFast", "快速转发", "接入端口", "Listening", "Learning"], "cat": "STP与链路聚合", "diff": "基础"},
    {"q": "EtherChannel是什么？怎么配置？", "a": "EtherChannel将多条物理链路捆绑为一条逻辑链路提高带宽和冗余。配置：先物理口shutdown→配完全一致的switchport/trunk/vlan→加channel-group 1 mode on→no shutdown。成员口配置不一致会显示suspended(s)。逻辑口Port-channel再配Trunk。", "kw": ["EtherChannel", "链路聚合", "channel-group", "Port-channel", "suspended"], "cat": "STP与链路聚合", "diff": "进阶"},
    {"q": "EtherChannel物理口显示suspended(s)怎么解决？", "a": "suspended说明成员端口配置不一致。修复方法：两个口都先shutdown→配完全相同的switchport/trunk/vlan配置→再各自加channel-group→最后no shutdown。", "kw": ["EtherChannel", "suspended", "成员端口", "配置不一致", "channel-group"], "cat": "STP与链路聚合", "diff": "进阶"},
    # 路由
    {"q": "静态路由怎么配置？", "a": "ip route 目的网段 子网掩码 下一跳IP。例如ip route 192.168.2.0 255.255.255.0 10.0.0.2。浮动静态路由加AD参数作备份：ip route X X X 200(默认AD=1，设大则备用)。默认路由：ip route 0.0.0.0 0.0.0.0 下一跳。", "kw": ["静态路由", "ip route", "下一跳", "默认路由", "浮动"], "cat": "路由协议", "diff": "基础"},
    {"q": "RIP协议有什么特点和限制？", "a": "RIP是距离矢量协议，度量参数为跳数(Hop Count)，直连0跳经过一个路由器1跳。最大15跳，16跳不可达，限制大型网络应用。RIPv2默认自动汇总(auto-summary)，不连续子网环境会导致路由冲突，需no auto-summary关闭。配置：router rip→version 2→no auto-summary→network X。", "kw": ["RIP", "跳数", "15跳", "自动汇总", "no auto-summary", "不连续子网"], "cat": "路由协议", "diff": "基础"},
    {"q": "RIP不连续子网问题是什么？怎么解决？", "a": "同一主类网络(如172.16.0.0/16)被其他网络(如12.0.0.0/8)隔开时，RIPv2自动汇总会把172.16.1.0/24和172.16.2.0/24都汇总为172.16.0.0/16发给中间路由器R2，R2收到两条相同路由冲突。解决：所有路由器加no auto-summary关闭自动汇总。", "kw": ["RIP", "不连续子网", "自动汇总", "no auto-summary", "主类网络"], "cat": "路由协议", "diff": "进阶"},
    {"q": "OSPF的Cost怎么计算？", "a": "Cost = 参考带宽(默认100Mbps) / 接口带宽。带宽越高Cost越低路径越优先。100M链路Cost=100/100=1，10M链路Cost=100/10=10，1G链路Cost=100/1000=0.1(取整为1)。路径总Cost是该路径上所有出接口Cost之和。", "kw": ["OSPF", "Cost", "计算", "参考带宽", "接口带宽", "100Mbps"], "cat": "路由协议", "diff": "基础"},
    {"q": "OSPF和RIP有什么区别？", "a": "OSPF是链路状态协议，用Cost(带宽)度量，支持Area分层，收敛快，适合大型网络。RIP是距离矢量协议，用跳数度量，最大15跳，自动汇总有问题，收敛慢，适合小型网络。OSPF用组播224.0.0.5，RIP用广播。", "kw": ["OSPF", "RIP", "对比", "链路状态", "距离矢量", "Cost", "跳数"], "cat": "路由协议", "diff": "基础"},
    # OSPF深入
    {"q": "OSPF虚链路和普通链路有什么区别？", "a": "1.本质：虚链路是Area 0延伸传递LSA不传业务数据；2.报文：虚链路用单播，普通链路用组播224.0.0.5；3.配置：虚链路在OSPF进程下area X virtual-link router-id，不在接口下；4.维护：思科虚链路建立后抑制Hello包减少开销。用于解决非骨干区域不直连Area 0的问题。", "kw": ["OSPF", "虚链路", "virtual-link", "ABR", "Area 0", "单播"], "cat": "OSPF深入", "diff": "进阶"},
    {"q": "OSPF有哪五种分组类型？", "a": "Hello：发现和维护邻居关系。DBD(数据库描述)：摘要LSDB内容。LSR(链路状态请求)：请求特定LSA详细信息。LSU(链路状态更新)：发送完整LSA信息。LSAck(链路状态确认)：确认收到LSU。", "kw": ["OSPF", "五种分组", "Hello", "DBD", "LSR", "LSU", "LSAck"], "cat": "OSPF深入", "diff": "进阶"},
    {"q": "OSPF邻居状态机有哪些状态？", "a": "Down(初始)→Init(收到Hello)→2-Way(双向收到Hello确认)→ExStart(主从选举DD序列号)→Exchange(交换DBD摘要)→Loading(请求缺失LSA的LSU)→Full(LSDB完全同步)。三张核心表：邻居表、LSDB链路状态数据库、路由表。", "kw": ["OSPF", "邻居状态", "Down", "Init", "2-Way", "ExStart", "Exchange", "Full"], "cat": "OSPF深入", "diff": "进阶"},
    {"q": "什么是ABR？有什么功能？", "a": "ABR(区域边界路由器)是连接Area 0(骨干区域)和其他区域的路由器。ABR维护多份LSDB(每个区域一份)，负责在区域间传递路由摘要信息，是Area间通信的桥梁。所有非骨干区域必须直连Area 0或通过虚链路连接到Area 0。", "kw": ["ABR", "区域边界", "Area 0", "骨干区域", "LSDB"], "cat": "OSPF深入", "diff": "进阶"},
    {"q": "路由重分布是什么？怎么配置？", "a": "边界路由器在不同路由协议间翻译路由信息。单向重分布：仅注入一个方向。双向：互相注入。OSPF中配：redistribute rip subnets。RIP中配：redistribute ospf 1 metric 1。需注意防环路，可用route-map过滤。常见问题：metric不匹配、管理距离冲突。", "kw": ["重分布", "redistribute", "边界路由器", "route-map", "OSPF", "RIP"], "cat": "OSPF深入", "diff": "进阶"},
    {"q": "OSPF的Stub和NSSA区域是什么？", "a": "Stub区域：阻止5类LSA(外部路由)进入，ABR自动注入默认路由。Totally Stub：阻止3类+5类LSA，仅保留区域内路由和默认路由(area X stub no-summary)。NSSA(Not-So-Stubby)：允许引入外部路由(7类LSA)但阻止5类LSA。目的是减少路由表大小和LSA泛洪开销。", "kw": ["Stub", "Totally Stub", "NSSA", "LSA", "5类", "7类", "默认路由"], "cat": "OSPF深入", "diff": "进阶"},
    {"q": "Loopback接口必须配/32掩码吗？", "a": "不是必须。Loopback可以配任何掩码(/24、/16等)。但OSPF对Loopback有特殊处理：不管实际掩码是什么，默认都将其宣告为/32主机路由。如需保留原始掩码，需在Loopback接口配ip ospf network point-to-point。", "kw": ["Loopback", "/32", "掩码", "OSPF", "point-to-point"], "cat": "OSPF深入", "diff": "进阶"},
    # VRRP与DHCP
    {"q": "什么是VRRP？", "a": "VRRP(虚拟路由冗余协议)将多台路由器虚拟成一台虚拟设备，实现网关冗余备份。主网关(Master)故障时自动切换到备份(Backup)设备，确保网络通信不中断。解决单点故障问题，保障关键业务连续性。", "kw": ["VRRP", "网关冗余", "Master", "Backup", "单点故障"], "cat": "VRRP与DHCP", "diff": "基础"},
    {"q": "DHCP的DORA过程是什么？", "a": "D-Discover：客户端广播(源0.0.0.0→目的255.255.255.255)寻找DHCP服务器。O-Offer：服务器回复可用IP+租期+Server ID。R-Request：客户端广播选择某服务器的IP，拒绝其他Offer。A-ACK：服务器确认分配，客户端正式绑定IP。服务器端口UDP 67，客户端UDP 68。", "kw": ["DHCP", "DORA", "Discover", "Offer", "Request", "ACK", "广播", "UDP"], "cat": "VRRP与DHCP", "diff": "基础"},
    {"q": "DHCP中继怎么配置？为什么需要？", "a": "路由器默认不转发广播包，跨网段客户端无法联系远程DHCP服务器。解决：在路由器接口配ip helper-address 服务器IP，路由器将DHCP广播转为单播转发。Option 82可记录客户端物理位置。ASA防火墙也支持DHCP中继。", "kw": ["DHCP中继", "ip helper-address", "跨网段", "广播", "Option 82"], "cat": "VRRP与DHCP", "diff": "进阶"},
    {"q": "DHCP租期管理是怎么工作的？", "a": "DHCP分配IP有租期(Lease)。T1=50%租期时客户端尝试向原服务器续租(Renew)。T2=87.5%租期时向任何服务器重绑定(Rebind)。过期后IP释放回地址池可分配给其他设备。ipconfig/release手动释放，ipconfig/renew手动续租。", "kw": ["DHCP", "租期", "T1", "T2", "续租", "Renew", "Rebind"], "cat": "VRRP与DHCP", "diff": "进阶"},
    {"q": "思科路由器怎么配置DHCP服务器？", "a": "ip dhcp excluded-address 排除地址范围(如网关)。ip dhcp pool 名称进入DHCP配置。network指定可分配网段和掩码。default-router指定默认网关。dns-server指定DNS。还可用host命令做静态绑定。", "kw": ["DHCP配置", "ip dhcp pool", "excluded-address", "default-router", "dns-server"], "cat": "VRRP与DHCP", "diff": "基础"},
    # 邮件
    {"q": "SMTP、POP3、IMAP有什么区别？", "a": "SMTP(端口25/465/587)：发送邮件和中继，推送协议。POP3(110/995)：下载邮件到本地可离线，下载后可删服务器副本，不支持多设备同步状态。IMAP(143/993)：服务器端管理邮件，多设备同步已读/未读/文件夹状态，需持续联网。", "kw": ["SMTP", "POP3", "IMAP", "邮件", "端口", "同步"], "cat": "邮件协议", "diff": "基础"},
    # ACL
    {"q": "标准ACL和扩展ACL有什么区别？", "a": "标准ACL(编号1-99/1300-1999)：仅基于源IP匹配，控制粒度粗。扩展ACL(100-199/2000-2699)：匹配源IP+目的IP+协议+端口，细粒度控制。标准ACL适合简单限制，扩展ACL可精确到'只禁止某网段访问特定端口'。扩展ACL应配在靠近源端接口。", "kw": ["标准ACL", "扩展ACL", "区别", "源IP", "目的IP", "端口"], "cat": "ACL", "diff": "基础"},
    {"q": "什么是ACL的隐含拒绝？", "a": "隐含拒绝(Implicit Deny)是ACL最重要的原则：数据包遍历所有规则未匹配任何一条，默认被拒绝丢弃。因此ACL末尾通常需显式加permit any允许其他流量(除非确实想阻断所有未明确允许的)。ACL规则顺序至关重要：先deny any则后面permit全部失效。", "kw": ["隐含拒绝", "Implicit Deny", "ACL", "顺序", "permit any"], "cat": "ACL", "diff": "基础"},
    {"q": "通配符掩码是什么？和子网掩码有什么区别？", "a": "通配符掩码(Wildcard Mask)用于ACL匹配：0=必须精确匹配，1=忽略该位。0.0.0.255对应/24网段，host关键字=0.0.0.0(精确匹配单台主机)。与子网掩码相反：子网掩码1=网络位0=主机位，通配符掩码0=匹配1=忽略。", "kw": ["通配符掩码", "Wildcard", "ACL", "0匹配", "1忽略", "host"], "cat": "ACL", "diff": "基础"},
    {"q": "时间ACL怎么配置？", "a": "先定义time-range：time-range work-hours→periodic weekdays 9:00 to 17:00。然后在ACL规则中绑定：access-list 110 deny tcp any any eq 80 time-range work-hours。实现基于时间段的访问控制，如限制上班时间上网。", "kw": ["时间ACL", "time-range", "时间段", "periodic", "weekdays"], "cat": "ACL", "diff": "进阶"},
    {"q": "ACL怎么应用到接口上？方向in和out有什么区别？", "a": "ip access-group 编号 in/out应用到接口。in方向：数据包进入接口时先过ACL检查再路由。out方向：数据包经路由确定出接口后过ACL检查再发出。扩展ACL推荐配在靠近源端的in方向，尽早丢弃非法流量节省带宽。", "kw": ["ACL", "接口", "in", "out", "方向", "access-group"], "cat": "ACL", "diff": "基础"},
    # 端口安全
    {"q": "端口安全怎么配置？", "a": "必须先将端口设为Access模式(switchport mode access)。然后switchport port-security启用安全。mac-address sticky自动学习当前MAC为安全地址。maximum设置最大允许MAC数。违例处理：protect(静默丢弃)、restrict(丢弃+日志)、shutdown(关闭端口)。", "kw": ["端口安全", "port-security", "sticky", "MAC", "maximum"], "cat": "端口安全", "diff": "基础"},
    # NAT
    {"q": "NAT有哪几种类型？", "a": "静态NAT：一对一固定映射私有IP到公网IP，用于对外提供服务。动态NAT：地址池多对多映射，内网主机轮流使用公网IP。PAT(端口地址转换/Overload)：多对一端口复用，多内网设备共用一个公网IP通过端口号区分，最常用。", "kw": ["NAT", "静态", "动态", "PAT", "Overload", "端口复用"], "cat": "NAT", "diff": "基础"},
    {"q": "PAT怎么配置？", "a": "1.定义inside/outside接口(ip nat inside/outside)。2.创建ACL允许内网网段(access-list 1 permit 192.168.1.0 0.0.0.255)。3.配PAT：ip nat inside source list 1 interface gi0/0 overload。overload是关键参数开启端口复用。", "kw": ["PAT", "配置", "overload", "ip nat", "inside", "outside"], "cat": "NAT", "diff": "基础"},
    {"q": "静态NAT和动态NAT有什么区别？", "a": "静态NAT：一对一永久映射(ip nat inside source static 内网IP 公网IP)，用于对外服务器。不需要ACL和overload。动态NAT：创建公网IP地址池(ip nat pool)，多内网设备轮流使用池中IP，用完则无法上网。PAT最常用解决多对一问题。", "kw": ["静态NAT", "动态NAT", "一对一", "地址池", "映射"], "cat": "NAT", "diff": "基础"},
    # 网络命令
    {"q": "ping命令有哪些参数？", "a": "ping测试连通性，发送ICMP回显请求。-t：持续ping直到Ctrl+C。-a：解析NetBIOS主机名。-n count：指定发送测试包个数(默认4)，可测平均/最快/最慢时间。是网络故障排查的首选工具。", "kw": ["ping", "ICMP", "-t", "-a", "-n", "连通性"], "cat": "网络命令", "diff": "基础"},
    {"q": "ipconfig有哪些常用参数？", "a": "ipconfig /all：显示TCP/IP详细信息(含MAC、DHCP服务器、租期)。/release：释放DHCP租约归还IP。/renew：向DHCP服务器续租IP。/flushdns：清除DNS解析缓存。是Windows网络诊断的基本命令。", "kw": ["ipconfig", "/all", "/release", "/renew", "/flushdns", "DHCP"], "cat": "网络命令", "diff": "基础"},
    {"q": "二进制怎么转十进制？", "a": "使用按权相加法。从最右边(最低位)开始，位置编号从0起，每位权值为2^位置编号。例如1011：1×2³+0×2²+1×2¹+1×2⁰=8+0+2+1=11。小数部分权值为负次幂：.01=0×2⁻¹+1×2⁻²=0.25。", "kw": ["二进制", "十进制", "转换", "按权相加", "次幂"], "cat": "网络命令", "diff": "基础"},
    # 实战经验
    {"q": "Packet Tracer配完网络后ping不通服务器怎么办？", "a": "先检查服务器Desktop→IP Configuration的默认网关是否填了对应VLAN的SVI地址(.254)，这是最常见遗漏。再检查：1.VLAN是否显式创建(vlan X)；2.Trunk是否active(show interfaces trunk)；3.SVI是否up；4.PC的IP/掩码/网关是否正确。", "kw": ["ping不通", "默认网关", "SVI", "Packet Tracer", "排错"], "cat": "实战经验", "diff": "基础"},
    {"q": "Packet Tracer中VLAN的SVI起不来怎么办？", "a": "VLAN必须用vlan X显式创建(2960和3560都需要)，否则即使Trunk允许该VLAN，show interfaces trunk的'active in management domain'显示none，SVI也起不来。3560还需先sdm prefer routing→reload→ip routing。", "kw": ["SVI", "起不来", "vlan创建", "sdm prefer", "Packet Tracer"], "cat": "实战经验", "diff": "进阶"},
    {"q": "Packet Tracer端口从Trunk切回Access怎么操作？", "a": "直接switchport access vlan X不会自动切回。no switchport mode trunk可能报错可跳过。正确做法：直接switchport mode access→switchport access vlan X即可。切回后生成树可能卡在LSN状态不转发，接入端口应加spanning-tree portfast跳过等待。", "kw": ["Trunk切Access", "switchport mode", "portfast", "生成树", "LSN"], "cat": "实战经验", "diff": "进阶"},
    {"q": "OSPF network宣告有什么注意事项？", "a": "Packet Tracer中OSPF network宣告避免用宽通配符(如0.0.255.255)，改用逐个子网/24(0.0.0.255)分别宣告更可靠。宽通配符可能导致意外宣告不该宣告的网段。", "kw": ["OSPF", "network", "宣告", "通配符", "Packet Tracer"], "cat": "实战经验", "diff": "进阶"},
    {"q": "Packet Tracer接口表端口名和实际连线不一致怎么办？", "a": "Packet Tracer接口表中的端口名可能与实际拓扑连线不一致(如表写Gig1/1实际是Gig0/2)。配端口聚合/Trunk时以用户实际连线为准，需要主动确认实际连接的是哪个端口。", "kw": ["接口表", "端口名", "不一致", "Packet Tracer", "连线"], "cat": "实战经验", "diff": "基础"},
]

# 从知识库自动生成 Q&A
def generate_qa_from_kb():
    qas = []
    for kb in KNOWLEDGE_BASE:
        # 策略1: 理论转问题
        qas.append({
            "q": f"请解释{kb['title']}的核心概念",
            "a": kb["theory"],
            "kw": kb["tags"] + [kb["category"]],
            "cat": kb["category"],
            "diff": "基础"
        })
        # 策略2: 命令转问题
        if kb["commands"]:
            cmd_text = "\n".join([f"- {c['cmd']}  # {c['desc']}" for c in kb["commands"]])
            qas.append({
                "q": f"{kb['title']}涉及哪些关键命令？",
                "a": f"关键命令如下：\n{cmd_text}",
                "kw": kb["tags"] + ["命令", "配置"],
                "cat": kb["category"],
                "diff": "基础"
            })
        # 策略3: 配置示例转问题
        if kb["configExample"]:
            qas.append({
                "q": f"如何配置{kb['title']}？给出配置示例",
                "a": kb["configExample"],
                "kw": kb["tags"] + ["配置示例", "实战"],
                "cat": kb["category"],
                "diff": "进阶"
            })
    return qas

# 从节点自动生成 Q&A
def generate_qa_from_nodes():
    qas = []
    for node in NODES:
        if node["type"] == "protocol":
            qas.append({
                "q": f"什么是{node['label']}协议？",
                "a": node["desc"],
                "kw": [node["label"]] + [d["name"] for d in DOMAINS if d["id"] == node["domain"]],
                "cat": next((d["name"] for d in DOMAINS if d["id"] == node["domain"]), ""),
                "diff": "基础"
            })
        elif node["type"] == "concept":
            qas.append({
                "q": f"什么是{node['label']}？",
                "a": node["desc"],
                "kw": [node["label"]],
                "cat": next((d["name"] for d in DOMAINS if d["id"] == node["domain"]), ""),
                "diff": "基础"
            })
        elif node["type"] == "command_group":
            qas.append({
                "q": f"命令 {node['label']} 怎么用？",
                "a": node["desc"].replace("\\n", "\n"),
                "kw": [node["label"]],
                "cat": next((d["name"] for d in DOMAINS if d["id"] == node["domain"]), ""),
                "diff": "基础"
            })
    return qas

ALL_QAS = QA_HARDCODED + generate_qa_from_kb() + generate_qa_from_nodes()
# 去重
seen_q = set()
UNIQUE_QAS = []
for qa in ALL_QAS:
    if qa["q"] not in seen_q:
        seen_q.add(qa["q"])
        UNIQUE_QAS.append(qa)
ALL_QAS = UNIQUE_QAS

print(f"[INFO] 生成了 {len(ALL_QAS)} 个问答对")

# ============================================================
# Part 6: Markdown 解析 (从原始笔记提取补充文本)
# ============================================================

def parse_markdown(filepath):
    """读取 markdown 文件并提取段落文本"""
    if not os.path.exists(filepath):
        print(f"[WARN] Markdown 文件不存在: {filepath}")
        return ""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

# ============================================================
# Part 7: 组装数据并生成 HTML
# ============================================================

def build_data_json():
    """将所有数据组装为 JSON"""
    data = {
        "meta": {
            "title": "Cisco网络技术知识库",
            "generatedAt": datetime.now().isoformat(),
            "stats": {
                "domains": len(DOMAINS),
                "nodes": len(NODES),
                "edges": len(EDGES),
                "knowledgeBase": len(KNOWLEDGE_BASE),
                "qas": len(ALL_QAS)
            }
        },
        "domains": DOMAINS,
        "nodes": NODES,
        "edges": EDGES,
        "knowledgeBase": KNOWLEDGE_BASE,
        "qas": ALL_QAS
    }
    return json.dumps(data, ensure_ascii=False, separators=(',', ':'))

def build_html(data_json):
    """生成完整的 HTML 文件"""
    return HTML_TEMPLATE.replace("%%DATA_JSON%%", data_json)

# HTML 模板 (包含 CSS + JS)
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cisco网络技术知识库</title>
<script src="https://unpkg.com/vis-network@9.1.6/standalone/umd/vis-network.min.js"></script>
<style>
:root {
  --bg-primary: #0d1117;
  --bg-secondary: #161b22;
  --bg-card: #1c2128;
  --bg-hover: #272d36;
  --text-primary: #e6edf3;
  --text-secondary: #8b949e;
  --text-muted: #6e7681;
  --border: #30363d;
  --accent-blue: #58a6ff;
  --accent-green: #3fb950;
  --accent-orange: #d29922;
  --accent-red: #f85149;
  --accent-purple: #bc8cff;
  --highlight: rgba(255, 213, 0, 0.25);
  --font-main: "Microsoft YaHei", "PingFang SC", sans-serif;
  --font-mono: "Cascadia Code", "Consolas", monospace;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: var(--font-main); background: var(--bg-primary); color: var(--text-primary); overflow: hidden; height: 100vh; }
.header { background: var(--bg-secondary); border-bottom: 1px solid var(--border); padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; }
.header h1 { font-size: 20px; font-weight: 600; }
.header h1 span { color: var(--accent-blue); }
.header-stats { display: flex; gap: 16px; font-size: 13px; color: var(--text-secondary); }
.header-stats .stat { display: flex; align-items: center; gap: 4px; }
.header-stats .stat strong { color: var(--accent-green); font-size: 15px; }
.tab-bar { background: var(--bg-secondary); border-bottom: 1px solid var(--border); display: flex; padding: 0 24px; }
.tab-btn { padding: 10px 24px; cursor: pointer; font-size: 14px; color: var(--text-secondary); border: none; background: none; border-bottom: 2px solid transparent; transition: all 0.2s; font-family: var(--font-main); }
.tab-btn:hover { color: var(--text-primary); background: var(--bg-hover); }
.tab-btn.active { color: var(--accent-blue); border-bottom-color: var(--accent-blue); }
.tab-content { display: none; height: calc(100vh - 98px); }
.tab-content.active { display: flex; }

/* === 知识图谱 Tab === */
.graph-panel { display: flex; width: 100%; height: 100%; }
.graph-sidebar { width: 260px; background: var(--bg-secondary); border-right: 1px solid var(--border); padding: 16px; overflow-y: auto; flex-shrink: 0; }
.graph-sidebar h3 { font-size: 14px; margin-bottom: 12px; color: var(--text-secondary); }
.graph-search { width: 100%; padding: 8px 12px; background: var(--bg-primary); border: 1px solid var(--border); border-radius: 6px; color: var(--text-primary); font-size: 13px; margin-bottom: 12px; font-family: var(--font-main); }
.graph-search:focus { outline: none; border-color: var(--accent-blue); }
.domain-filter { margin-bottom: 16px; }
.domain-filter label { display: flex; align-items: center; gap: 8px; padding: 4px 0; font-size: 12px; color: var(--text-secondary); cursor: pointer; }
.domain-filter label:hover { color: var(--text-primary); }
.domain-filter input[type="checkbox"] { accent-color: var(--accent-blue); }
.domain-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
.graph-container { flex: 1; position: relative; }
#graph-network { width: 100%; height: 100%; }
.graph-detail { width: 320px; background: var(--bg-secondary); border-left: 1px solid var(--border); padding: 20px; overflow-y: auto; flex-shrink: 0; }
.graph-detail h3 { font-size: 16px; margin-bottom: 8px; }
.graph-detail .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; margin-bottom: 12px; }
.badge-domain { background: rgba(88,166,255,0.15); color: var(--accent-blue); }
.badge-topic { background: rgba(188,140,255,0.15); color: var(--accent-purple); }
.badge-protocol { background: rgba(63,185,80,0.15); color: var(--accent-green); }
.badge-concept { background: rgba(210,153,34,0.15); color: var(--accent-orange); }
.badge-command { background: rgba(248,81,73,0.15); color: var(--accent-red); }
.graph-detail p { font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 12px; }
.graph-detail .related-list { list-style: none; }
.graph-detail .related-list li { padding: 6px 10px; margin: 4px 0; background: var(--bg-primary); border-radius: 4px; font-size: 12px; cursor: pointer; }
.graph-detail .related-list li:hover { background: var(--bg-hover); color: var(--accent-blue); }
.graph-legend { margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--border); }
.graph-legend h4 { font-size: 12px; color: var(--text-muted); margin-bottom: 8px; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--text-secondary); padding: 2px 0; }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; }

/* === 知识库 Tab === */
.kb-panel { flex-direction: column; width: 100%; overflow: hidden; }
.kb-toolbar { padding: 16px 24px; background: var(--bg-secondary); border-bottom: 1px solid var(--border); display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.kb-search { flex: 1; min-width: 200px; padding: 8px 14px; background: var(--bg-primary); border: 1px solid var(--border); border-radius: 6px; color: var(--text-primary); font-size: 14px; font-family: var(--font-main); }
.kb-search:focus { outline: none; border-color: var(--accent-blue); }
.kb-filters { display: flex; gap: 6px; flex-wrap: wrap; }
.kb-filter-btn { padding: 4px 12px; border-radius: 14px; font-size: 12px; border: 1px solid var(--border); background: none; color: var(--text-secondary); cursor: pointer; font-family: var(--font-main); transition: all 0.2s; }
.kb-filter-btn:hover { border-color: var(--accent-blue); color: var(--accent-blue); }
.kb-filter-btn.active { background: var(--accent-blue); color: #fff; border-color: var(--accent-blue); }
.kb-grid { flex: 1; overflow-y: auto; padding: 20px 24px; display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 16px; align-content: start; }
.kb-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 16px; transition: all 0.2s; cursor: pointer; }
.kb-card:hover { border-color: var(--accent-blue); transform: translateY(-2px); }
.kb-card h4 { font-size: 15px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
.kb-card .card-cat { font-size: 11px; padding: 2px 8px; border-radius: 10px; background: rgba(88,166,255,0.12); color: var(--accent-blue); }
.kb-card .card-tags { display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 8px; }
.kb-card .tag { font-size: 11px; padding: 1px 6px; background: var(--bg-primary); border-radius: 3px; color: var(--text-muted); }
.kb-card .card-theory { font-size: 13px; color: var(--text-secondary); line-height: 1.6; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.kb-card.expanded .card-theory { -webkit-line-clamp: unset; }
.kb-card .card-cmds { margin-top: 10px; }
.kb-card .cmd-item { display: flex; align-items: flex-start; gap: 8px; padding: 4px 0; font-size: 12px; }
.kb-card .cmd-code { font-family: var(--font-mono); color: var(--accent-green); background: var(--bg-primary); padding: 2px 8px; border-radius: 3px; font-size: 12px; white-space: nowrap; }
.kb-card .cmd-desc { color: var(--text-muted); }
.kb-card .card-config { margin-top: 10px; background: var(--bg-primary); border-radius: 4px; padding: 10px; font-family: var(--font-mono); font-size: 12px; color: var(--accent-green); white-space: pre-wrap; max-height: 200px; overflow-y: auto; display: none; }
.kb-card.expanded .card-config { display: block; }
.kb-card .expand-hint { text-align: center; font-size: 11px; color: var(--text-muted); margin-top: 8px; }
.copy-btn { background: var(--bg-primary); border: 1px solid var(--border); color: var(--text-secondary); padding: 2px 8px; border-radius: 3px; font-size: 11px; cursor: pointer; margin-left: auto; }
.copy-btn:hover { color: var(--accent-blue); border-color: var(--accent-blue); }

/* === 问答系统 Tab === */
.qa-panel { flex-direction: column; width: 100%; overflow: hidden; }
.qa-hero { padding: 32px 24px 20px; text-align: center; background: var(--bg-secondary); border-bottom: 1px solid var(--border); }
.qa-hero h2 { font-size: 18px; margin-bottom: 16px; color: var(--text-primary); }
.qa-search-wrap { max-width: 600px; margin: 0 auto; }
.qa-search { width: 100%; padding: 12px 18px; background: var(--bg-primary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary); font-size: 16px; font-family: var(--font-main); }
.qa-search:focus { outline: none; border-color: var(--accent-blue); box-shadow: 0 0 0 3px rgba(88,166,255,0.15); }
.qa-quick-tags { display: flex; gap: 6px; justify-content: center; flex-wrap: wrap; margin-top: 12px; }
.qa-tag { padding: 4px 12px; border-radius: 14px; font-size: 12px; border: 1px solid var(--border); background: none; color: var(--text-secondary); cursor: pointer; font-family: var(--font-main); }
.qa-tag:hover { border-color: var(--accent-green); color: var(--accent-green); }
.qa-results { flex: 1; overflow-y: auto; padding: 20px 24px; max-width: 800px; margin: 0 auto; width: 100%; }
.qa-result-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 16px; margin-bottom: 12px; }
.qa-result-card:hover { border-color: var(--accent-blue); }
.qa-question { font-size: 15px; font-weight: 600; margin-bottom: 8px; color: var(--text-primary); }
.qa-answer { font-size: 13px; color: var(--text-secondary); line-height: 1.7; white-space: pre-wrap; }
.qa-answer mark { background: var(--highlight); color: var(--text-primary); padding: 0 2px; border-radius: 2px; }
.qa-meta { display: flex; gap: 8px; margin-top: 8px; }
.qa-meta span { font-size: 11px; padding: 2px 8px; border-radius: 10px; }
.qa-cat-badge { background: rgba(88,166,255,0.12); color: var(--accent-blue); }
.qa-diff-badge { background: rgba(210,153,34,0.12); color: var(--accent-orange); }
.qa-count { text-align: center; padding: 8px; font-size: 13px; color: var(--text-muted); }
.qa-empty { text-align: center; padding: 40px; color: var(--text-muted); font-size: 14px; }

/* === Scrollbar === */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* === vis.js overrides === */
.vis-navigation { display: none !important; }
</style>
</head>
<body>
<div class="header">
  <h1><span>Cisco</span> 网络技术知识库</h1>
  <div class="header-stats" id="headerStats"></div>
</div>
<div class="tab-bar">
  <button class="tab-btn active" data-tab="graph">知识图谱</button>
  <button class="tab-btn" data-tab="kb">知识库</button>
  <button class="tab-btn" data-tab="qa">问答系统</button>
</div>

<!-- 知识图谱 -->
<div class="tab-content active" id="tab-graph">
  <div class="graph-panel">
    <div class="graph-sidebar">
      <input class="graph-search" id="graphSearch" placeholder="搜索节点..." />
      <h3>领域过滤</h3>
      <div class="domain-filter" id="domainFilters"></div>
      <div class="graph-legend">
        <h4>图例</h4>
        <div class="legend-item"><div class="legend-dot" style="background:#4a9eff"></div> 领域</div>
        <div class="legend-item"><div class="legend-dot" style="background:#bc8cff"></div> 主题</div>
        <div class="legend-item"><div class="legend-dot" style="background:#3fb950"></div> 协议</div>
        <div class="legend-item"><div class="legend-dot" style="background:#d29922"></div> 概念</div>
        <div class="legend-item"><div class="legend-dot" style="background:#f85149"></div> 命令</div>
      </div>
    </div>
    <div class="graph-container">
      <div id="graph-network"></div>
    </div>
    <div class="graph-detail" id="graphDetail">
      <p style="color:var(--text-muted);text-align:center;margin-top:40px;">点击节点查看详情</p>
    </div>
  </div>
</div>

<!-- 知识库 -->
<div class="tab-content" id="tab-kb">
  <div class="kb-panel">
    <div class="kb-toolbar">
      <input class="kb-search" id="kbSearch" placeholder="搜索知识库..." />
      <div class="kb-filters" id="kbFilters"></div>
    </div>
    <div class="kb-grid" id="kbGrid"></div>
  </div>
</div>

<!-- 问答系统 -->
<div class="tab-content" id="tab-qa">
  <div class="qa-panel">
    <div class="qa-hero">
      <h2>网络技术问答</h2>
      <div class="qa-search-wrap">
        <input class="qa-search" id="qaSearch" placeholder="输入问题关键词，如：OSPF、VLAN配置、NAT..." />
      </div>
      <div class="qa-quick-tags" id="qaQuickTags"></div>
    </div>
    <div class="qa-results" id="qaResults"></div>
  </div>
</div>

<script>
window.__CISCO_KB_DATA__ = %%DATA_JSON%%;
</script>
<script>
(function() {
const D = window.__CISCO_KB_DATA__;
const TYPE_COLORS = {domain:'#4a9eff',topic:'#bc8cff',protocol:'#3fb950',concept:'#d29922',command_group:'#f85149'};
const TYPE_NAMES = {domain:'领域',topic:'主题',protocol:'协议',concept:'概念',command_group:'命令'};
const TYPE_BADGES = {domain:'badge-domain',topic:'badge-topic',protocol:'badge-protocol',concept:'badge-concept',command_group:'badge-command'};

// === Stats ===
document.getElementById('headerStats').innerHTML =
  `<div class="stat"><strong>${D.meta.stats.domains}</strong>领域</div>` +
  `<div class="stat"><strong>${D.meta.stats.nodes}</strong>节点</div>` +
  `<div class="stat"><strong>${D.meta.stats.knowledgeBase}</strong>知识卡片</div>` +
  `<div class="stat"><strong>${D.meta.stats.qas}</strong>问答对</div>`;

// === Tab Switching ===
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
    if (btn.dataset.tab === 'graph' && window._graphNetwork) window._graphNetwork.redraw();
  });
});

// === Knowledge Graph ===
function initGraph() {
  const domainMap = {};
  D.domains.forEach(d => domainMap[d.id] = d);
  const nodeMap = {};
  D.nodes.forEach(n => nodeMap[n.id] = n);

  // vis.js nodes
  const visNodes = D.nodes.map(n => {
    const domain = domainMap[n.domain];
    return {
      id: n.id, label: n.label,
      color: { background: TYPE_COLORS[n.type] || '#888', border: 'rgba(255,255,255,0.1)', highlight: { background: TYPE_COLORS[n.type], border: '#fff' } },
      size: n.size || 20,
      shape: n.type === 'domain' ? 'diamond' : n.type === 'command_group' ? 'triangle' : 'dot',
      font: { color: '#e0e0e0', size: n.type === 'domain' ? 16 : 13, face: 'Microsoft YaHei' },
      borderWidth: 2,
      shadow: { enabled: true, color: 'rgba(0,0,0,0.3)', size: 5 },
      _data: n
    };
  });

  // vis.js edges
  const visEdges = D.edges.map((e, i) => ({
    id: 'e' + i, from: e.s, to: e.t,
    arrows: e.type === 'related_to' ? {} : { to: { enabled: true, scaleFactor: 0.4 } },
    dashes: e.type === 'uses' || e.type === 'configures',
    color: { color: e.type === 'belongs_to' ? '#333' : e.type === 'uses' ? '#2ecc71' : e.type === 'configures' ? '#e74c3c' : e.type === 'related_to' ? '#555' : '#f39c12', opacity: e.type === 'belongs_to' ? 0.4 : 0.6 },
    width: e.type === 'belongs_to' ? 1 : 1.5,
    smooth: { type: 'continuous' },
    title: e.label
  }));

  const container = document.getElementById('graph-network');
  const data = { nodes: new vis.DataSet(visNodes), edges: new vis.DataSet(visEdges) };
  const options = {
    physics: {
      solver: 'forceAtlas2Based',
      forceAtlas2Based: { gravitationalConstant: -60, centralGravity: 0.005, springLength: 120, springConstant: 0.04, damping: 0.4 },
      stabilization: { iterations: 200, fit: true }
    },
    interaction: { hover: true, tooltipDelay: 200, navigationButtons: false, keyboard: { enabled: true } },
    edges: { smooth: { type: 'continuous' } }
  };
  const network = new vis.Network(container, data, options);
  window._graphNetwork = network;

  // Domain filters
  const filterDiv = document.getElementById('domainFilters');
  D.domains.forEach(d => {
    const label = document.createElement('label');
    label.innerHTML = `<input type="checkbox" checked data-domain="${d.id}"><span class="domain-dot" style="background:${d.color}"></span>${d.name}`;
    filterDiv.appendChild(label);
  });

  function applyFilters() {
    const active = new Set();
    filterDiv.querySelectorAll('input:checked').forEach(cb => active.add(cb.dataset.domain));
    const searchTerm = document.getElementById('graphSearch').value.toLowerCase();

    const visibleNodes = D.nodes.filter(n => {
      if (!active.has(n.domain)) return false;
      if (searchTerm && !n.label.toLowerCase().includes(searchTerm) && !n.desc.toLowerCase().includes(searchTerm)) return false;
      return true;
    }).map(n => n.id);

    const visibleSet = new Set(visibleNodes);
    // Also include connected nodes
    const edgeVisible = D.edges.filter(e => visibleSet.has(e.s) || visibleSet.has(e.t));
    edgeVisible.forEach(e => { visibleSet.add(e.s); visibleSet.add(e.t); });

    data.nodes.forEach(n => {
      data.nodes.update({ id: n.id, hidden: !visibleSet.has(n.id) });
    });
    data.edges.forEach(e => {
      data.edges.update({ id: e.id, hidden: !(visibleSet.has(e.from) && visibleSet.has(e.to)) });
    });
  }

  filterDiv.addEventListener('change', applyFilters);
  document.getElementById('graphSearch').addEventListener('input', applyFilters);

  // Node click -> detail
  network.on('click', params => {
    if (params.nodes.length === 0) return;
    const nodeId = params.nodes[0];
    const node = nodeMap[nodeId];
    if (!node) return;
    const domain = domainMap[node.domain];

    // Find related nodes
    const related = [];
    D.edges.forEach(e => {
      if (e.s === nodeId && nodeMap[e.t]) related.push({ node: nodeMap[e.t], label: e.label, dir: '→' });
      if (e.t === nodeId && nodeMap[e.s]) related.push({ node: nodeMap[e.s], label: e.label, dir: '←' });
    });

    const detailDiv = document.getElementById('graphDetail');
    detailDiv.innerHTML = `
      <h3>${node.label}</h3>
      <span class="badge ${TYPE_BADGES[node.type]}">${TYPE_NAMES[node.type]}</span>
      <span class="badge badge-domain" style="margin-left:4px">${domain ? domain.icon + ' ' + domain.name : ''}</span>
      <p style="margin-top:12px">${node.desc}</p>
      ${related.length ? '<h4 style="font-size:13px;color:var(--text-muted);margin:12px 0 6px">关联节点 (' + related.length + ')</h4><ul class="related-list">' +
        related.slice(0, 15).map(r => `<li data-id="${r.node.id}">${r.dir} ${r.node.label} <span style="color:var(--text-muted);font-size:11px">${r.label}</span></li>`).join('') + '</ul>' : ''}
    `;
    detailDiv.querySelectorAll('.related-list li').forEach(li => {
      li.addEventListener('click', () => {
        network.focus(li.dataset.id, { scale: 1.2, animation: { duration: 500 } });
        network.selectNode(li.dataset.id);
        network.body.emitter.emit('click', { nodes: [li.dataset.id] });
      });
    });
  });
}

// === Knowledge Base ===
function initKB() {
  const grid = document.getElementById('kbGrid');
  const cats = [...new Set(D.knowledgeBase.map(k => k.category))];
  const filtersDiv = document.getElementById('kbFilters');

  // All filter
  const allBtn = document.createElement('button');
  allBtn.className = 'kb-filter-btn active';
  allBtn.textContent = '全部';
  allBtn.dataset.cat = '';
  filtersDiv.appendChild(allBtn);

  cats.forEach(c => {
    const btn = document.createElement('button');
    btn.className = 'kb-filter-btn';
    btn.textContent = c;
    btn.dataset.cat = c;
    filtersDiv.appendChild(btn);
  });

  let activeCat = '';

  function renderKB() {
    const search = document.getElementById('kbSearch').value.toLowerCase();
    const filtered = D.knowledgeBase.filter(kb => {
      if (activeCat && kb.category !== activeCat) return false;
      if (search) {
        const haystack = (kb.title + ' ' + kb.tags.join(' ') + ' ' + kb.theory).toLowerCase();
        return haystack.includes(search);
      }
      return true;
    });

    grid.innerHTML = filtered.map(kb => `
      <div class="kb-card" data-id="${kb.id}">
        <h4>${kb.title} <span class="card-cat">${kb.category}</span></h4>
        <div class="card-tags">${kb.tags.map(t => `<span class="tag">${t}</span>`).join('')}</div>
        <div class="card-theory">${kb.theory}</div>
        ${kb.commands && kb.commands.length ? `<div class="card-cmds">${kb.commands.map(c => `<div class="cmd-item"><span class="cmd-code">${c.cmd}</span><span class="cmd-desc">${c.desc}</span><button class="copy-btn" data-cmd="${c.cmd}">复制</button></div>`).join('')}</div>` : ''}
        ${kb.configExample ? `<div class="card-config">${kb.configExample}</div>` : ''}
        <div class="expand-hint">${kb.configExample ? '点击展开/收起配置示例' : ''}</div>
      </div>
    `).join('');

    // Card click expand
    grid.querySelectorAll('.kb-card').forEach(card => {
      card.addEventListener('click', e => {
        if (e.target.classList.contains('copy-btn')) {
          navigator.clipboard.writeText(e.target.dataset.cmd).then(() => {
            e.target.textContent = '已复制';
            setTimeout(() => e.target.textContent = '复制', 1500);
          });
          return;
        }
        card.classList.toggle('expanded');
      });
    });
  }

  filtersDiv.addEventListener('click', e => {
    if (!e.target.classList.contains('kb-filter-btn')) return;
    filtersDiv.querySelectorAll('.kb-filter-btn').forEach(b => b.classList.remove('active'));
    e.target.classList.add('active');
    activeCat = e.target.dataset.cat;
    renderKB();
  });

  document.getElementById('kbSearch').addEventListener('input', renderKB);
  renderKB();
}

// === Q&A System ===
function initQA() {
  const resultsDiv = document.getElementById('qaResults');
  const searchInput = document.getElementById('qaSearch');
  const tagsDiv = document.getElementById('qaQuickTags');

  // Extract top tags
  const tagCount = {};
  D.qas.forEach(qa => (qa.kw || []).forEach(k => { tagCount[k] = (tagCount[k] || 0) + 1; }));
  const topTags = Object.entries(tagCount).sort((a, b) => b[1] - a[1]).slice(0, 15);
  tagsDiv.innerHTML = topTags.map(([t]) => `<button class="qa-tag">${t}</button>`).join('');

  tagsDiv.addEventListener('click', e => {
    if (e.target.classList.contains('qa-tag')) {
      searchInput.value = e.target.textContent;
      searchInput.dispatchEvent(new Event('input'));
    }
  });

  function bigrams(str) {
    const s = str.toLowerCase();
    const result = new Set();
    for (let i = 0; i < s.length - 1; i++) result.add(s.substring(i, i + 2));
    return result;
  }
  function dice(a, b) {
    const ba = bigrams(a), bb = bigrams(b);
    if (ba.size === 0 && bb.size === 0) return 0;
    let overlap = 0;
    ba.forEach(g => { if (bb.has(g)) overlap++; });
    return (2 * overlap) / (ba.size + bb.size);
  }

  function searchQA(query) {
    if (!query.trim()) return showRandom();
    const tokens = query.toLowerCase().split(/[\s,，。、？?！!]+/).filter(t => t.length > 0);

    const scored = D.qas.map(qa => {
      let score = 0;
      const kwLower = (qa.kw || []).map(k => k.toLowerCase());
      const qLower = qa.q.toLowerCase();
      const aLower = qa.a.toLowerCase();

      // Keyword exact match (40%)
      let kwMatch = 0;
      tokens.forEach(t => { kwLower.forEach(k => { if (k.includes(t) || t.includes(k)) kwMatch++; }); });
      score += 0.4 * Math.min(kwMatch / Math.max(tokens.length, 1), 1);

      // Tag/category match (25%)
      let tagMatch = 0;
      tokens.forEach(t => { if ((qa.cat || '').toLowerCase().includes(t)) tagMatch++; });
      score += 0.25 * Math.min(tagMatch / Math.max(tokens.length, 1), 1);

      // Fuzzy match (20%)
      let fuzzyMatch = 0;
      tokens.forEach(t => { kwLower.forEach(k => { if (dice(t, k) > 0.4) fuzzyMatch++; }); });
      score += 0.2 * Math.min(fuzzyMatch / Math.max(tokens.length, 1), 1);

      // Question text similarity (15%)
      let qMatch = 0;
      tokens.forEach(t => { if (qLower.includes(t)) qMatch++; });
      score += 0.15 * Math.min(qMatch / Math.max(tokens.length, 1), 1);

      // Bonus: answer contains query
      tokens.forEach(t => { if (aLower.includes(t)) score += 0.05; });

      return { qa, score };
    }).filter(s => s.score > 0.05).sort((a, b) => b.score - a.score);

    if (scored.length === 0) {
      resultsDiv.innerHTML = '<div class="qa-empty">未找到相关结果，试试其他关键词</div>';
      return;
    }

    const top = scored.slice(0, 20);
    resultsDiv.innerHTML = `<div class="qa-count">找到 ${scored.length} 个相关结果，显示前 ${top.length} 个</div>` +
      top.map(({ qa }) => {
        const highlightedA = highlightText(qa.a, tokens);
        const highlightedQ = highlightText(qa.q, tokens);
        return `<div class="qa-result-card">
          <div class="qa-question">${highlightedQ}</div>
          <div class="qa-answer">${highlightedA}</div>
          <div class="qa-meta"><span class="qa-cat-badge">${qa.cat}</span><span class="qa-diff-badge">${qa.diff}</span></div>
        </div>`;
      }).join('');
  }

  function highlightText(text, tokens) {
    let result = text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
    tokens.forEach(t => {
      if (t.length < 2) return;
      const regex = new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
      result = result.replace(regex, '<mark>$1</mark>');
    });
    return result;
  }

  function showRandom() {
    const shuffled = [...D.qas].sort(() => Math.random() - 0.5).slice(0, 8);
    resultsDiv.innerHTML = '<div class="qa-count">推荐问题</div>' +
      shuffled.map(qa => `<div class="qa-result-card">
        <div class="qa-question">${qa.q}</div>
        <div class="qa-answer">${qa.a.replace(/</g, '&lt;').replace(/>/g, '&gt;').substring(0, 200)}${qa.a.length > 200 ? '...' : ''}</div>
        <div class="qa-meta"><span class="qa-cat-badge">${qa.cat}</span><span class="qa-diff-badge">${qa.diff}</span></div>
      </div>`).join('');
  }

  let debounceTimer;
  searchInput.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => searchQA(searchInput.value), 200);
  });

  showRandom();
}

// === Init ===
initGraph();
initKB();
initQA();
})();
</script>
</body>
</html>"""

# ============================================================
# Main
# ============================================================

def main():
    md_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "network_notes.md")
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cisco_knowledge_app.html")

    print(f"[INFO] 解析 Markdown: {md_path}")
    md_text = parse_markdown(md_path)
    print(f"[INFO] Markdown 长度: {len(md_text)} 字符")

    print("[INFO] 组装数据...")
    data_json = build_data_json()
    print(f"[INFO] JSON 数据大小: {len(data_json)} 字节")

    print("[INFO] 生成 HTML...")
    html = build_html(data_json)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"[OK] 生成完成: {out_path}")
    print(f"[OK] 文件大小: {size_kb:.1f} KB")
    print(f"[OK] 统计: {len(DOMAINS)} 领域, {len(NODES)} 节点, {len(EDGES)} 边, {len(KNOWLEDGE_BASE)} 知识卡片, {len(ALL_QAS)} 问答对")

if __name__ == "__main__":
    main()
