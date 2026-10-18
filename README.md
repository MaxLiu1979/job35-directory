# job35-directory

专门收录**对 35+ 求职者友好**（一线员工与中高管均覆盖）、且**近半年招聘仍然活跃**的全球企业与招聘渠道。

**在线浏览：<https://maxliu1979.github.io/job35-directory/>**

名录数据全部来自公开可核查的信息，任何人都可以验证、纠错、补充。
采集与判定由配套框架自动完成：[job35-crawler](https://github.com/MaxLiu1979/job35-crawler)。

> English version: [README.en.md](README.en.md)

## 如何使用本名录

按行业浏览 `data/companies.yaml`，关注两个维度：

- **活跃度**：近 180 天是否有公开招聘信号（企业官网招聘页 / Greenhouse / Lever 公开接口 / 官方招聘 RSS）
- **35+ 友好度**：`explicit`（明确欢迎资深人才）> `likely`（长期经验岗等间接信号）> `unknown`（暂无信号）> `risky`（出现明确年龄上限）

判定方法与证据规则见 [docs/methodology.md](docs/methodology.md)。

## 行业覆盖与迭代路线

行业目录见 `data/industries.yaml`，以 GICS 全球行业分类为骨架，目前覆盖：

教育 · 医疗健康 · 制造业 · 能源 · 金融 · 互联网 · 信息技术 · 通信服务 · 原材料 · 非必需消费 · 必需消费 · 公用事业 · 房地产 · 交通物流 · 农业 · 公共部门与外企驻华

名单按层级**渐进式迭代**，每一步都可独立交付价值：

1. **第一阶段（top10）**：每个行业先收录公认的头部 10 家，跑通采集与校验
2. **第二阶段（top50）**：扩展到各行业前 50，引入社区贡献
3. **第三阶段（top100）**：覆盖各行业前 100，并下沉到国家级/区域级名单
4. **长期**：持续监控活跃度，自动降级 180 天无信号的企业

## 数据文件

| 文件 | 说明 |
|---|---|
| `data/industries.yaml` | 行业目录（中英双语） |
| `data/companies.yaml` | 企业名录：来源、层级、状态 |
| `data/signals/` | 框架自动生成的采集结果（JSON + 汇总报告） |

## 自动化

[job35-crawler](https://github.com/MaxLiu1979/job35-crawler) 每周定时运行，结果以 PR 形式提回本仓库；合并前请人工抽查证据。
本仓库的 `validate.yml` 会对每次提交做数据格式校验。

## 重要声明

- 本名录只做**公开信息的聚合与标注**，不构成任何求职建议或对企业雇佣政策的完整描述。
- 收录 ≠ 背书，未收录 ≠ 不友好。
- 所有条目必须附公开证据。若信息有误，请提 issue 并附证据，核实后立即更正。

## License

数据与文档：CC0-1.0（见 LICENSE）。代码（脚本与 workflow）：MIT。
