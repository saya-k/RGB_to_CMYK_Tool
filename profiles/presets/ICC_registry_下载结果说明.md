# ICC Registry 下载结果说明

来源：

```text
https://registry.color.org/profile-registry/
```

本次已从 ICC Profile Registry 批量下载 `.icc` 文件到本文件夹。

## 下载结果

- 扫描 Profile 详情页：31 个
- 找到 ICC 下载链接：31 个
- 成功下载：31 个
- 下载失败：0 个

详细机器报告：

- `icc_registry_scan_report.csv`
- `icc_registry_download_report.csv`

## 已下载 ICC

```text
APTEC_CMYKOGV_Coated_LinearCTV_2025.icc
APTEC_Flexo_Coated_LinearCTV_2025.icc
APTEC_Flexo_Label_LinearCTV_2025.icc
APTEC_Flexo_PVC_LinearCTV_2025.icc
APTEC_Offset_Coated_LinearCTV_2025.icc
APTEC_Offset_Uncoated_LinearCTV_2025.icc
APTEC_PC10_CardBoard_2023_v1.icc
APTEC_PC11_CCNB_2023_v1.icc
CGATS21_CRPC1.icc
CGATS21_CRPC2.icc
CGATS21_CRPC3.icc
CGATS21_CRPC4.icc
CGATS21_CRPC5.icc
CGATS21_CRPC6.icc
CGATS21_CRPC7.icc
Coated_Fogra39L_VIGC_260.icc
Coated_Fogra39L_VIGC_300.icc
GRACoL2006_Coated1v2.icc
GRACoL2013_CRPC6.icc
GRACoL2013UNC_CRPC3.icc
JapanColor2011Coated.icc
PSOcoated_v3.icc
PSOsc-b_paper_v3_FOGRA54.icc
PSOuncoated_v3_FOGRA52.icc
SC_paper_eci.icc
SNAP2007.icc
SWOP2006_Coated3v2.icc
SWOP2006_Coated5v2.icc
SWOP2013C3_CRPC5.icc
Uncoated_Fogra47L_VIGC_260.icc
Uncoated_Fogra47L_VIGC_300.icc
```

## 未找到同名文件

以下是之前参考网页常见预设中出现过、但本次 ICC registry 没有找到完全同名 `.icc` 的项目。工具没有伪造这些文件，而是改用 registry 中最接近或实际存在的文件：

```text
ISO_Coated_v2.icc
ISO_Coated_v2_300.icc
ISO_Uncoated_Yellowish.icc
ISO_Newspaper_26v4.icc
PSO_SC_Paper_v3.icc
SWOP2013_CRPC5.icc
Japan_Color_2011_Coated.icc
```

对应关系：

```text
Coated Fogra39L_300% -> Coated_Fogra39L_VIGC_300.icc
Uncoated Fogra47L_300% -> Uncoated_Fogra47L_VIGC_300.icc
PSO Coated v3 -> PSOcoated_v3.icc
PSO Uncoated v3 -> PSOuncoated_v3_FOGRA52.icc
PSO SC Paper v3 -> PSOsc-b_paper_v3_FOGRA54.icc 或 SC_paper_eci.icc
SWOP2013 CRPC5 -> SWOP2013C3_CRPC5.icc 或 CGATS21_CRPC5.icc
Japan Color 2011 Coated -> JapanColor2011Coated.icc
```
