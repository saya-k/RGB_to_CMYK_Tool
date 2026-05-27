# RGB 转 CMYK 一键工具使用说明

## 设计师怎么用

1. 双击 `打开网页转换CMYK.bat`，也可以双击 `一键转换CMYK.bat`。
2. 浏览器会自动打开本地网页。
3. 在 `ICC Profile ICC 简介` 区域选择预设 ICC，默认是 `Coated Fogra39L_300%`。
4. 在 `Source RGB Profile 源 RGB 配置文件` 区域选择源 RGB，默认是 `sRGB v4 ICC 首选项`。
5. 渲染意图默认是 `相对比色法`，默认启用抖动，输出格式默认是 `TIFF`。
6. 如果要使用印刷厂自己的 CMYK ICC，切换到 `Custom Profile 自定义配置文件` 上传 `.icc` 或 `.icm` 文件。
7. 如果要使用自己的源 RGB ICC，切换到 `Custom sRGB 自定义 sRGB` 上传 `.icc` 或 `.icm` 文件。
8. 把图片拖到上传区域，或点击上传区域选择图片。
9. 点击 `生成 CMYK`。
10. 处理完成后，工具会自动打开 `CMYK_Output` 文件夹。

## 输出结果在哪里

- `CMYK_Output`：转换后的 CMYK JPG 图片。
- `Original_Backup`：自动备份的原图。
- `Preview_Report`：RGB 与 CMYK 左右对比预览图。
- `convert_report.csv`：处理报告，可用 Excel 打开。
- `logs`：运行日志。

## 支持格式

支持 `JPG`、`JPEG`、`PNG`、`TIFF`、`TIF`、`WebP`。

输出格式可选：

- `TIFF`：默认，推荐印刷使用。
- `JPG`：文件较小，适合预览和传输。
- `PNG`：PNG 通常不保存 CMYK，本工具会输出 RGB 预览图。

## ICC 配置文件

网页里已经内置常用预设 ICC 的名称和说明，会显示：

- Standard 标准
- Region 地区
- Paper Type 纸张类型
- TAC 总墨量
- Paper Class 纸张等级

默认选择 `Coated Fogra39L_300%`。

预设说明不等于 ICC 文件本身。ICC 是专业二进制色彩配置文件，通常需要从印刷厂、官方标准机构或公司已有授权资源获取。

如果要让某个预设真正参与转换，请把对应 `.icc` 或 `.icm` 文件放进：

```text
profiles/presets/
```

默认预设 `Coated Fogra39L_300%` 对应文件名：

```text
Coated_Fogra39L_VIGC_300.icc
```

本工具已从 ICC Profile Registry 下载 31 个免费 ICC 文件到 `profiles/presets`。下载结果见：

```text
profiles/presets/ICC_registry_下载结果说明.md
profiles/presets/icc_registry_download_report.csv
```

## 源 RGB 配置文件

本工具已从 ICC 官方 sRGB 页面下载 3 个源 RGB ICC 文件到：

```text
profiles/source_rgb/presets/
```

默认使用：

```text
sRGB v4 ICC 首选项
sRGB_v4_ICC_preference.icc
```

下载结果见：

```text
profiles/source_rgb/presets/sRGB_下载结果说明.md
profiles/source_rgb/presets/srgb_download_report.csv
```

如果印刷厂提供了自定义 CMYK ICC 文件，也可以直接在网页里上传。

如果没有 ICC 文件，工具会使用通用 CMYK 转换，并在报告和日志中提示：

```text
未使用印刷厂ICC，仅为通用转换
```

## 报告怎么看

`convert_report.csv` 会记录：

- 文件名
- 原始路径
- 原始颜色模式
- 是否成功转换
- 输出路径
- 是否存在高饱和颜色风险
- 错误信息

如果“是否存在高饱和颜色风险”显示“需要人工检查”，说明图片里可能有高饱和绿色、蓝色、紫色、荧光黄或橙红色。这类颜色转 CMYK 后可能变灰、变暗或变脏，建议设计师人工确认。

## 注意事项

- 工具不会删除原图。
- 上传的图片会保存到 `RGB_Input`。
- 每次运行都会先把原图复制到 `Original_Backup`。
- 输出文件统一命名为 `原文件名_CMYK.jpg`。
- 如果某张图片出错，工具会继续处理下一张，错误会写进报告。

## 首次运行前准备

电脑需要安装 Python 3.10 或更高版本。双击 `一键转换CMYK.bat` 时，如果缺少 Pillow，工具会自动尝试安装。

如果自动安装失败，请在联网环境下打开命令提示符，进入本工具文件夹后执行：

```bat
python -m pip install -r requirements.txt
```

安装 Python 时请勾选 `Add Python to PATH`。
