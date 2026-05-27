# 源 RGB / sRGB ICC 下载结果说明

来源：

```text
https://registry.color.org/rgb-registry/srgbprofiles
```

本次已下载 ICC 官方可直接获取的 sRGB 配置文件：

```text
sRGB_v4_ICC_preference.icc
sRGB_v4_ICC_preference_displayclass.icc
sRGB2014.icc
```

## Adobe RGB 配置文件

以下 RGB ICC 来自本工具目录中的 Adobe ICC Profiles CS4 Windows end-user 包，并已复制到本文件夹：

```text
AdobeRGB1998.icc
AppleRGB.icc
ColorMatchRGB.icc
PAL_SECAM.icc
SMPTE-C.icc
VideoHD.icc
VideoNTSC.icc
VideoPAL.icc
```

对应网页预设：

```text
Adobe RGB (1998)
Apple RGB
ColorMatch RGB
PAL/SECAM
SMPTE-C
HD Video (Rec. 709)
Video NTSC
Video PAL
```

默认源 RGB 配置：

```text
sRGB v4 ICC 首选项
sRGB_v4_ICC_preference.icc
```

## ECI RGB 配置文件

以下 RGB ICC 来自 ECI 官方下载包 `ecirgbv20.zip`，并已复制到本文件夹：

```text
eciRGB_v2.icc
eciRGB_v2_ICCv4.icc
```

对应网页预设：

```text
eciRGB v2
eciRGB v2 (ICC v4)
```

## 未内置的预设

目前 Source RGB Profile 列表中的预设均已配置实际 ICC 文件。

## 渲染意图

默认：

```text
相对比色法
```

可选：

```text
感知
相对比色法
饱和
绝对比色法
```

## 抖动与输出格式

默认启用抖动，用于减少照片类图像转换后的色带。

默认输出格式：

```text
TIFF
```

可选输出：

```text
TIFF
JPG
PNG
```

注意：PNG 通常不保存 CMYK 数据，本工具输出 PNG 时会保存为 RGB 预览图。
