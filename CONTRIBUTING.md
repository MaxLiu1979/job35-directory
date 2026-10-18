# 贡献指南 / Contributing

感谢你愿意帮 35+ 求职者把这份名录做扎实。所有贡献必须遵守两条红线：

1. **只使用公开、可核查的信息**；不提交通过登录、付费墙或违反目标站点用户协议获取的内容。
2. **每条判定附证据**：来源 URL + 原文摘录 + 你的核查日期。

## 添加企业（最常见）

编辑 `data/companies.yaml`，新增条目：

```yaml
  - id: mfg-siemens-de          # 行业-名称简写-国家，全局唯一
    name: 西门子
    name_en: Siemens
    industry: manufacturing    # 行业 code 必须存在于 data/industries.yaml
    tier: top10                # top10 | top50 | top100 | candidate
    country: DE
    sources:                   # 至少一个公开来源，支持以下类型
      - type: greenhouse
        slug: siemens
      - type: lever
        slug: example
      - type: careers_page
        url: https://example.com/careers
      - type: rss
        url: https://example.com/careers.xml
    status: pending            # 新条目一律 pending，由框架跑过后更新
    note: 可选备注
```

关于 `tier`：头部榜单没有唯一权威来源，取各行业公认口径（营收/市值/雇主品牌榜均可），
在 PR 中注明所依据的榜单即可；不确定就用 `candidate`。

## 提交 35+ 友好证据

框架的关键词判定可能误伤或漏判。人工核实后，在条目中补充：

```yaml
    evidence:
      - url: https://example.com/careers/senior-engineer
        quote: "10年以上相关经验，年龄不限"
        checked_at: "2026-02-10"
```

并在 PR 描述里写清楚你是怎么核实的（截图请上传到 issue，不要提交进仓库）。

## 修正与删除

- 信息过时、企业改名/倒闭：直接改，PR 中附来源。
- 企业提出异议：新开 issue 讨论，不要直接在 PR 里删除条目。

## 代码与自动化

采集框架在 [job35-crawler](https://github.com/MaxLiu1979/job35-crawler)，
新增数据源适配器、改进词表请去那个仓库提 PR。

## 行为准则

对雇主不友好不等于对求职者有敌意。描述事实、给出证据、保持克制。
