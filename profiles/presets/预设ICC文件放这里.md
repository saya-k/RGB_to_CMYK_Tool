# 预设 ICC 文件放这里

网页里已经内置了常用预设 ICC 的名称和说明，例如：

- `Coated Fogra39L_300%`
- `Uncoated Fogra47L_300%`
- `PSO Coated v3`
- `PSO Uncoated v3`
- `ISO Coated v2`
- `ISO Coated v2 300%`
- `GRACoL2013 CRPC6`
- `SWOP2013 CRPC5`
- `Japan Color 2011 Coated`

但 ICC 本身是色彩配置二进制文件，通常受标准机构、软件厂商或网站授权限制。请从印刷厂、官方标准机构或公司已有授权资源获取。

## 默认预设文件名

默认选择的 `Coated Fogra39L_300%`，请把对应 ICC 文件命名为：

```text
Coated_Fogra39L_VIGC_300.icc
```

本文件已从 ICC Registry 下载到本文件夹。

如果文件名不一致，网页仍会显示该预设说明，但转换时会提示未找到该预设 ICC，并使用通用 CMYK 转换。

## 常见预设建议文件名

```text
Coated_Fogra39L_VIGC_300.icc
Uncoated_Fogra47L_VIGC_300.icc
PSOcoated_v3.icc
PSOuncoated_v3_FOGRA52.icc
PSOsc-b_paper_v3_FOGRA54.icc
SC_paper_eci.icc
GRACoL2013_CRPC6.icc
SWOP2013C3_CRPC5.icc
JapanColor2011Coated.icc
```
