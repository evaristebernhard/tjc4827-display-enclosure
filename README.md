# TJC4827 便携显示器外壳：简化试装版 D

这是一个为 4.3 英寸 TJC4827 显示屏、STM32F407ZG-P1 和 ESP-01 做的可调整外壳原型。外壳由屏幕前壳和抽拉托板两件组成；板子先用胶带固定在托板上，托板沿宽松导轨滑入屏幕后方。设计刻意保持简单，方便本科项目试打后继续改尺寸。

充电宝外挂在背面，可用绑带固定；它不占用盒内厚度。当前外壳约 144 × 96 × 41 mm。打印与装配步骤、供电提示和未验证事项见[装配说明](output/screwless_simple/装配与供电说明.md)。

## 文件

- [交互式三维预览](output/screwless_simple/index.html)（浏览器需要联网加载 model-viewer）
- [完整打印与源码压缩包](output/TJC4827_screwless_simple_D.zip)
- STL：`output/screwless_simple/STL/`
- 3MF：`output/screwless_simple/3MF/`
- STEP：`output/screwless_simple/STEP/`
- 参数和 build123d 源码：`output/screwless_simple/src/`

`项目布局示意.png` 是外观摆放示意图，不是精确制造图。绿色和黄色板卡空间是预留包络，不代表实物颜色。

## 原型限制

已检查导轨滑动位置和板卡预留包络的几何干涉，并检查导出的网格封闭性。尚未进行实体打印或实物装配；屏幕耳位高度、插头与线缆弯曲空间、绑带固定、打印间隙及充电宝供电稳定性都需要按手头零件验证。ESP-01 需要稳定的 3.3 V 供电，不能直接接充电宝的 5 V。
