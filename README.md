# 文档大师 / Document Master

简体中文 | [English](README_EN.md)

为 AI Agent 提供文档整理、润色与审校流程：按用途和读者选择结构，保留事实、限定条件和作者原意，减少重复与 AI 套话。

## 使用

下载 GitHub Release 中的 `document-master-0.8.1.zip`，导入支持 Skill ZIP 的环境，或把包内 `document-master/` 放入宿主的 Skill 目录并重新加载。源码入口是 [SKILL.md](document-master/SKILL.md)。

示例请求：“用文档大师润色这份方案，保留原意，交修订稿、关键改动和待核实项。”

AgentBuddy 对应版本：`skills:skills.byted.org/default/public/document-master:0.8.1`。

## 能力与边界

支持轻量修订、结构审校、新稿整理、会议纪要、知识讲解和授权范例学习。不同文体采用不同检查视角，不强制套模板。

纯文本审校无需外部依赖；线上文档访问、写回、Office 文件生成和渲染依赖宿主工具及授权。默认交修订稿或副本，覆盖原稿、重要删除、改变结论和对外发布遵守明确授权范围。

当前为试用版。结构和打包检查不等于跨平台运行验证；新增原生文档示范已检查桌面渲染，窄屏及其他宿主尚未验证；旧示范 HTML 未做视觉验收。包中不含真实内网文档、凭据或个人语料。

## 维护

同一份 `document-master/` 是两个发布渠道的内容来源。发布流程见 [RELEASING.md](RELEASING.md)，版本记录见 [CHANGELOG.md](CHANGELOG.md)。

尚未指定开源许可证；公开可见不等于授予额外许可。
