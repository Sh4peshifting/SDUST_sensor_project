# 山科大电科21级传感器与检测技术课程设计
>本仓库为山东科技大学电子信息科学与技术2021级课程设计，主要实现检测空气中直径小于2.5微米粒子的浓度，浓度大于某一值时报警，
>该课设使用rk3268 Linux嵌入式开发板、M701七合一气体传感器实现，网页后端使用 `flask`

1. `local_display` 包含了用于在 `Ubuntu` (一个Linux发行版)下使用终端显示空气质量信息的代码
2. `web_display` 包含了使用 `flask` 作为后端的网页实现
3. `report` 包含了使用 `LaTeX` 撰写的课程设计报告，模板基于[该仓库](https://github.com/Jiazhen-Lei/SJTU_Course_Template_Latex)
