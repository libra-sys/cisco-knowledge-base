#!/usr/bin/env python3
"""
思科知识点可视化分析脚本
基于"超绝牛逼网络笔记"文档提取思科知识点, 按类别统计并生成交互式 HTML 报告
"""
import re
import json
from collections import Counter, defaultdict
from pathlib import Path

DOC_PATH = Path("E:/ciscotop/network_notes.md")
OUTPUT_PATH = Path("E:/ciscotop/cisco_analysis.html")

with open(DOC_PATH, "r", encoding="utf-8") as f:
    text = f.read()

lines = text.split("\n")

# ========== 知识分类定义 ==========
categories = {
    "OSI & TCP/IP 模型": [
        "OSI", "TCP/IP", "七层", "四层", "物理层", "数据链路层", "网络层", "传输层",
        "会话层", "表示层", "应用层", "网络接口层", "网际互连层", "封装", "解封装",
        "PDU", "Segment", "Packet", "Frame", "Bit"
    ],
    "以太网 & 局域网": [
        "以太网", "IEEE802", "CSMA/CD", "MAC地址", "MAC", "冲突域", "广播域",
        "共享介质", "总线", "VLAN", "Trunk", "802.1Q", "VTP", "生成树", "STP",
        "双绞线", "同轴电缆", "光纤", "Wi-Fi"
    ],
    "交换技术": [
        "交换机", "Switch", "电路交换", "报文交换", "分组交换", "帧交换",
        "信元交换", "端口交换", "存储转发", "直通交换", "ATM", "交换机配置",
        "switchport", "access", "trunk", "VLAN", "fa0/", "gigabitEthernet"
    ],
    "路由协议": [
        "路由器", "Router", "OSPF", "RIP", "EIGRP", "BGP", "路由", "重分布",
        "路由表", "静态路由", "动态路由", "默认路由", "ASBR", "LSA", "area",
        "redistribute", "metric", "Router-ID", "Loopback", "下一跳", "next-hop"
    ],
    "IP 地址 & 子网": [
        "IP地址", "子网掩码", "子网划分", "VLSM", "CIDR", "IPv4", "IPv6",
        "网络地址", "广播地址", "通配符掩码", "Wildcard", "10.", "172.16",
        "192.168", "NAT", "DHCP", "DNS", "公网", "私网", "255.255", "/24", "/8"
    ],
    "Cisco IOS 命令": [
        "enable", "configure terminal", "conf t", "interface", "hostname",
        "show running-config", "show vlan", "show interfaces", "show ip",
        "copy running-config", "no shutdown", "shutdown", "access-list",
        "ip address", "router ospf", "router rip", "network", "redistribute",
        "switchport mode", "spanning-tree", "write", "reload", "description",
        "speed", "duplex", "ip route", "line vty", "line console", "password",
        "secret", "banner", "service password", "logging"
    ],
    "访问控制 & 安全": [
        "ACL", "访问控制", "permit", "deny", "安全", "端口安全", "802.1X",
        "防火墙", "ASA", "加密", "认证", "AAA", "TACACS", "RADIUS",
        "implicit deny", "隐含拒绝"
    ],
    "应用层协议": [
        "HTTP", "HTTPS", "FTP", "SMTP", "POP3", "IMAP", "DNS", "DHCP",
        "Telnet", "SSH", "SNMP", "TFTP", "NTP", "RDP", "SMB", "NFS",
        "应用层协议"
    ],
    "传输层协议": [
        "TCP", "UDP", "三次握手", "端口", "可靠", "不可靠", "面向连接",
        "无连接", "流量控制", "拥塞控制", "滑动窗口", "序列号", "确认应答"
    ],
    "网络命令 & 诊断": [
        "ping", "traceroute", "tracert", "ipconfig", "nslookup", "netstat",
        "arp", "ifconfig", "show", "debug", "telnet", "ssh"
    ],
}

# ========== 统计分析 ==========
total_lines = len(lines)
total_chars = len(text)

# 按类别统计提及次数
category_counts = {}
for cat, keywords in categories.items():
    count = 0
    for kw in keywords:
        count += len(re.findall(re.escape(kw), text, re.IGNORECASE))
    category_counts[cat] = count

# 提取 Cisco IOS 命令
cisco_commands = set()
command_patterns = [
    r'\b(enable|configure\s*terminal|conf\s*t)\b',
    r'\binterface\s+(fastEthernet|gigabitEthernet|loopback|serial|vlan)\s*[\d/]+',
    r'\b(hostname|ip\s+address|ip\s+route|no\s+shutdown|shutdown)\b',
    r'\bswitchport\s+(mode|access|trunk|allowed)\b',
    r'\bshow\s+(running-config|vlan|interfaces|ip|mac|startup-config)\b',
    r'\bcopy\s+running-config\s+startup-config\b',
    r'\brouter\s+(ospf|rip|eigrp|bgp)\b',
    r'\baccess-list\s+\d+\s+(permit|deny)\b',
    r'\bnetwork\s+[\d.]+',
    r'\b(redistribute|default-information)\b',
    r'\bspanning-tree\b',
    r'\b(vlan\s+\d+|name\s+\w+)\b',
]

for pattern in command_patterns:
    matches = re.findall(pattern, text, re.IGNORECASE)
    for m in matches:
        if isinstance(m, tuple):
            cmd = " ".join(m).strip()
        else:
            cmd = m.strip()
        if cmd:
            cisco_commands.add(cmd.lower())

# 提取协议名称
protocols = {
    "TCP": "传输层",
    "UDP": "传输层", 
    "IP": "网络层",
    "ICMP": "网络层",
    "ARP": "网络层",
    "RARP": "网络层",
    "OSPF": "路由协议",
    "RIP": "路由协议",
    "EIGRP": "路由协议",
    "BGP": "路由协议",
    "HTTP": "应用层",
    "HTTPS": "应用层",
    "FTP": "应用层",
    "SMTP": "应用层",
    "POP3": "应用层",
    "IMAP": "应用层",
    "DNS": "应用层",
    "DHCP": "应用层",
    "Telnet": "应用层",
    "SSH": "应用层",
    "SNMP": "应用层",
    "TFTP": "应用层",
    "STP": "数据链路层",
    "RSTP": "数据链路层",
    "802.1Q": "数据链路层",
    "PPP": "数据链路层",
    "CSMA/CD": "数据链路层",
    "NAT": "网络层",
    "VLAN": "数据链路层",
    "VTP": "数据链路层",
}

protocol_layer_counts = defaultdict(int)
protocol_counts = {}
for proto, layer in protocols.items():
    cnt = len(re.findall(re.escape(proto), text))
    if cnt > 0:
        protocol_counts[proto] = cnt
        protocol_layer_counts[layer] += cnt

# ========== 文档结构分析 ==========
# 提取"章节"（以非缩进行开头的关键主题）
sections = []
for line in lines:
    line = line.strip()
    if line.startswith("- ") and len(line) > 5 and not line.startswith("- 0") and not line.startswith("- 1"):
        if any(kw in line for kw in ["是什么", "定义", "协议", "模型", "配置", "步骤", "命令", "技术", "原理", "总结", "区别", "分类", "功能", "应用", "概述"]):
            sections.append(line.replace("- ", "").strip())

# Top 10 高频关键词 (中文)
cn_keywords = ["交换机", "路由器", "协议", "网络", "数据", "配置", "接口", "地址", "路由", "VLAN",
               "端口", "安全", "OSPF", "RIP", "TCP", "UDP", "OSI", "以太网", "ACL", "DHCP",
               "子网", "广播", "封装", "封装", "命令", "通信", "传输", "连接"]
kw_counter = Counter()
for kw in cn_keywords:
    kw_counter[kw] = len(re.findall(kw, text))

# ========== 生成 HTML ==========
sorted_cats = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
sorted_protos = sorted(protocol_counts.items(), key=lambda x: x[1], reverse=True)[:15]
sorted_kw = kw_counter.most_common(20)

cat_labels = json.dumps([x[0] for x in sorted_cats])
cat_values = json.dumps([x[1] for x in sorted_cats])
cat_colors = json.dumps([
    "#4361EE", "#3A0CA3", "#7209B7", "#F72585", "#4CC9F0",
    "#4895EF", "#560BAD", "#B5179E", "#3F37C9", "#4895EF"
])

proto_labels = json.dumps([x[0] for x in sorted_protos])
proto_values = json.dumps([x[1] for x in sorted_protos])

kw_labels = json.dumps([x[0] for x in sorted_kw])
kw_values = json.dumps([x[1] for x in sorted_kw])

layer_labels = json.dumps([k for k, v in protocol_layer_counts.items()])
layer_values = json.dumps([v for k, v in protocol_layer_counts.items()])

cmd_count = len(cisco_commands)
section_count = len(sections)
proto_count = len([p for p, v in protocol_counts.items() if v > 0])

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>思科知识点可视化分析 — 超绝牛逼网络笔记</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; background: #0f1923; color: #e0e0e0; min-height: 100vh; }}
.hero {{ background: linear-gradient(135deg, #0f1923 0%, #162230 40%, #1b2a3a 100%); padding: 48px 32px; text-align: center; border-bottom: 1px solid #2a3a4a; }}
.hero h1 {{ font-size: 2.5rem; background: linear-gradient(135deg, #4CC9F0, #4361EE, #7209B7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 12px; }}
.hero p {{ color: #8899aa; font-size: 1.1rem; }}
.hero .source {{ margin-top: 8px; font-size: 0.85rem; color: #667788; }}

.stats-bar {{ display: flex; justify-content: center; gap: 24px; padding: 24px 32px; flex-wrap: wrap; }}
.stat-card {{ background: #1a2a3a; border: 1px solid #2a3a4a; border-radius: 12px; padding: 20px 32px; text-align: center; min-width: 140px; transition: transform 0.2s; }}
.stat-card:hover {{ transform: translateY(-2px); border-color: #4361EE; }}
.stat-card .num {{ font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #4CC9F0, #4361EE); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.stat-card .label {{ font-size: 0.85rem; color: #8899aa; margin-top: 4px; }}

.grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 20px 32px; max-width: 1400px; margin: 0 auto; }}
@media (max-width: 900px) {{ .grid {{ grid-template-columns: 1fr; }} }}
.chart-container {{ background: #1a2a3a; border: 1px solid #2a3a4a; border-radius: 12px; padding: 20px; }}
.chart-container h3 {{ color: #ccd6e0; font-size: 1rem; margin-bottom: 16px; }}
.chart-container.full {{ grid-column: 1 / -1; }}
canvas {{ max-height: 350px; }}

.cmd-section {{ padding: 20px 32px; max-width: 1400px; margin: 0 auto; }}
.cmd-section h3 {{ color: #ccd6e0; font-size: 1.1rem; margin-bottom: 16px; }}
.cmd-grid {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.cmd-tag {{ background: #1a2a3a; border: 1px solid #3a4a5a; border-radius: 6px; padding: 6px 14px; font-family: "Cascadia Code", "Fira Code", "Consolas", monospace; font-size: 0.8rem; color: #4CC9F0; transition: all 0.2s; }}
.cmd-tag:hover {{ background: #243044; border-color: #4361EE; }}

.topics {{ padding: 20px 32px; max-width: 1400px; margin: 0 auto; }}
.topics h3 {{ color: #ccd6e0; font-size: 1.1rem; margin-bottom: 16px; }}
.topics-list {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 8px; }}
.topic-item {{ background: #1a2a3a; border: 1px solid #2a3a4a; border-radius: 8px; padding: 10px 16px; font-size: 0.85rem; color: #99aabb; transition: all 0.2s; }}
.topic-item:hover {{ border-color: #4361EE; color: #ccd6e0; }}
.topic-item::before {{ content: "▸ "; color: #4361EE; }}

.summary {{ padding: 20px 32px 40px; max-width: 1400px; margin: 0 auto; }}
.summary h3 {{ color: #ccd6e0; font-size: 1.1rem; margin-bottom: 16px; }}
.summary-text {{ background: #1a2a3a; border: 1px solid #2a3a4a; border-radius: 12px; padding: 20px; line-height: 1.8; color: #99aabb; }}

footer {{ text-align: center; padding: 24px; color: #556677; font-size: 0.8rem; border-top: 1px solid #1a2a3a; }}
strong {{ color: #4CC9F0; }}
</style>
</head>
<body>

<div class="hero">
  <h1>思科/Cisco 知识点可视化分析</h1>
  <p>数据来源：超绝牛逼网络笔记 (超绝牛逼网络笔记.docx)</p>
  <p class="source">分析日期：2026年5月28日 &nbsp;|&nbsp; 文档规模：{total_chars:,} 字符 / {total_lines:,} 行</p>
</div>

<div class="stats-bar">
  <div class="stat-card"><div class="num">{len(sorted_cats)}</div><div class="label">知识分类</div></div>
  <div class="stat-card"><div class="num">{proto_count}</div><div class="label">网络协议</div></div>
  <div class="stat-card"><div class="num">{cmd_count}</div><div class="label">Cisco IOS 命令</div></div>
  <div class="stat-card"><div class="num">{section_count}</div><div class="label">知识主题</div></div>
  <div class="stat-card"><div class="num">{total_lines:,}</div><div class="label">文档总行数</div></div>
</div>

<div class="grid">
  <div class="chart-container">
    <h3>📊 知识点分类分布（按关键词提及频率）</h3>
    <canvas id="catBar"></canvas>
  </div>
  <div class="chart-container">
    <h3>🎯 热点关键词 Top 20</h3>
    <canvas id="kwBar"></canvas>
  </div>
  <div class="chart-container">
    <h3>📡 网络协议提及频次 Top 15</h3>
    <canvas id="protoBar"></canvas>
  </div>
  <div class="chart-container">
    <h3>🏗️ 协议层级分布</h3>
    <canvas id="layerPie"></canvas>
  </div>
</div>

<div class="cmd-section">
  <h3>⌨️ 思科 IOS 命令集（文档中出现的 {cmd_count} 条典型命令）</h3>
  <div class="cmd-grid">
'''

# 添加命令标签
for cmd in sorted(cisco_commands)[:80]:
    display = cmd.replace("fastethernet", "fa").replace("gigabitethernet", "gi")
    if len(display) > 45:
        display = display[:42] + "..."
    html += f'    <span class="cmd-tag">{display}</span>\n'

html += '''  </div>
</div>

<div class="topics">
  <h3>📋 文档主要知识主题</h3>
  <div class="topics-list">
'''

# 添加主题列表
for s in sections[:30]:
    display = s if len(s) < 60 else s[:57] + "..."
    html += f'    <div class="topic-item">{display}</div>\n'

html += f'''  </div>
</div>

<div class="summary">
  <h3>📝 分析总结</h3>
  <div class="summary-text">
    <p>本笔记覆盖了<strong>计算机网络核心知识</strong>的多个层次，从<strong>OSI 七层模型</strong>到<strong>TCP/IP 协议栈</strong>，从<strong>以太网底层原理</strong>到<strong>应用层协议</strong>。</p>
    <br>
    <p><strong>重点领域：</strong>交换技术与 VLAN 配置、路由协议（OSPF/RIP）、Cisco IOS 命令行操作、访问控制列表（ACL）、IP 地址规划与子网划分。</p>
    <br>
    <p>文档中包含<strong>大量实战配置示例</strong>，包括跨交换机 VLAN 划分、RIP/OSPF 重分布、边界路由器配置等，实战性极强。</p>
    <br>
    <p>按 <strong>Cisco CCNA/CCNP 认证</strong> 知识体系来看，本笔记覆盖了：</p>
    <ul style="margin-left: 20px; margin-top: 8px;">
      <li>Network Fundamentals（网络基础）✅</li>
      <li>Network Access（网络接入/VLAN/Trunk）✅</li>
      <li>IP Connectivity（路由协议）✅</li>
      <li>IP Services（DHCP/DNS/NAT）✅</li>
      <li>Security Fundamentals（ACL/安全基础）✅</li>
      <li>Automation & Programmability 部分覆盖</li>
    </ul>
  </div>
</div>

<footer>
  思科知识点可视化分析 &copy; 2026 | 基于"超绝牛逼网络笔记"文档自动生成
</footer>

<script>
// 知识点分类
new Chart(document.getElementById('catBar'), {{
  type: 'bar',
  data: {{
    labels: {cat_labels},
    datasets: [{{
      label: '提及次数',
      data: {cat_values},
      backgroundColor: {cat_colors},
      borderRadius: 4,
      borderWidth: 0
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ ticks: {{ color: '#8899aa' }}, grid: {{ color: '#1a2a3a' }} }},
      y: {{ ticks: {{ color: '#ccd6e0', font: {{ size: 11 }} }}, grid: {{ color: '#1a2a3a' }} }}
    }}
  }}
}});

// 关键词
new Chart(document.getElementById('kwBar'), {{
  type: 'bar',
  data: {{
    labels: {kw_labels},
    datasets: [{{
      label: '出现次数',
      data: {kw_values},
      backgroundColor: '#4361EE',
      borderRadius: 4,
      borderWidth: 0
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ ticks: {{ color: '#8899aa' }}, grid: {{ color: '#1a2a3a' }} }},
      y: {{ ticks: {{ color: '#ccd6e0', font: {{ size: 11 }} }}, grid: {{ color: '#1a2a3a' }} }}
    }}
  }}
}});

// 协议
new Chart(document.getElementById('protoBar'), {{
  type: 'bar',
  data: {{
    labels: {proto_labels},
    datasets: [{{
      label: '提及次数',
      data: {proto_values},
      backgroundColor: '#7209B7',
      borderRadius: 4,
      borderWidth: 0
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ ticks: {{ color: '#8899aa' }}, grid: {{ color: '#1a2a3a' }} }},
      y: {{ ticks: {{ color: '#ccd6e0', font: {{ size: 11 }} }}, grid: {{ color: '#1a2a3a' }} }}
    }}
  }}
}});

// 协议层级分布
new Chart(document.getElementById('layerPie'), {{
  type: 'doughnut',
  data: {{
    labels: {layer_labels},
    datasets: [{{
      data: {layer_values},
      backgroundColor: ['#4361EE', '#7209B7', '#F72585', '#4CC9F0', '#4895EF', '#3A0CA3'],
      borderWidth: 0
    }}]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{ position: 'right', labels: {{ color: '#ccd6e0', font: {{ size: 11 }}, padding: 16 }} }}
    }}
  }}
}});
</script>
</body>
</html>'''

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print(f"OK: Report written to {OUTPUT_PATH} ({len(html):,} chars)")
print(f"Categories: {len(sorted_cats)}, Protocols: {proto_count}, Commands: {cmd_count}, Topics: {section_count}")
