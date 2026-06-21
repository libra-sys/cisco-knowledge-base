# Cisco 网络技术知识库

基于 CCNA/CCNP 学习笔记构建的交互式知识图谱 + 知识库 + 问答系统。

## 功能

- **知识图谱** — vis.js 力导向图，115个节点覆盖14个知识领域，支持拖拽、搜索、领域过滤和节点详情
- **知识库** — 30张分类卡片，包含理论说明、Cisco IOS 命令列表和完整配置示例，命令支持一键复制
- **问答系统** — 169个问答对，支持关键词搜索和模糊匹配（Dice系数），结果高亮显示

## 知识覆盖

| 领域 | 内容 |
|------|------|
| 网络基础 | 网络分类、OSI/TCP-IP模型、基础命令 |
| 以太网与封装 | IEEE802.x、CSMA/CD、数据封装/解封装 |
| 冲突域与广播域 | Hub vs Switch、CSMA/CD、共享介质 |
| 交换技术 | 电路/报文/分组交换、SDN/NFV |
| 跨交换机VLAN | Trunk、802.1Q、三层交换、SVI |
| STP与EtherChannel | PVST+、根桥选举、PortFast、链路聚合 |
| 路由协议 | 静态路由、RIP、OSPF |
| OSPF深入 | ABR、虚链路、邻居状态机、重分布、Stub |
| VRRP与DHCP | 网关冗余、DORA流程、DHCP中继 |
| ACL | 标准/扩展ACL、时间ACL、通配符掩码 |
| NAT | 静态NAT、动态NAT、PAT |
| 端口安全 | port-security、sticky MAC |

## 使用

直接双击打开 `cisco_knowledge_app.html` 即可（需联网加载 vis.js CDN）。

## 重新生成

修改知识数据后运行：

```bash
python build_cisco_kb.py
```

## 项目结构

```
├── network_notes.md              # 原始学习笔记 (Markdown)
├── 超绝牛逼网络笔记.docx          # 原始笔记 (Word)
├── build_cisco_kb.py             # 知识库生成脚本
├── cisco_knowledge_app.html      # 生成的交互式应用
├── analyze_cisco.py              # 统计分析脚本
├── cisco_analysis.html           # 统计可视化报告
├── convert_docx.py               # docx→md 转换脚本
└── check_docx.py                 # docx 结构检查脚本
```

## License

MIT
