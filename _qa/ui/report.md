# Visual QA

## Evidence

- `slice/`：首轮垂直切片；发现并重做了首段视频中的误生成人手。
- `recheck/platform-layout-entry-390x844.png`：中文主入口。
- `recheck/platform-layout-video-*.png`：五条支线运行态。
- `recheck/platform-layout-climax-ready-390x844.png`、`platform-layout-climax-video-390x844.png`：高潮入口与播放态。
- `recheck/platform-layout-result-390x844.png`：结尾页淡入完成态。
- `recheck/platform-layout-entry-en-320x568.png`：英文窄屏。
- `recheck/external-guest-entry-390x844.png`：访客栏可见的外部访问检查。
- `clip_*-contact.jpg`：六段视频逐秒接触表。
- `poster-160.png`：列表缩略图。

## Findings and fixes

- P1 / 首段视频：中间帧误生成一只人手。修正视频提示并重生，复验接触表中只剩兔子、炮筒与 MelonMick。
- P1 / 果泥猪尾帧：模型生成假 `UME` 布牌。改为单一无字奶油色绑带并重生。
- P1 / 结尾：杯身多次生成标签或数字。改为奶茶内部微距，最终帧无可读文字。
- P1 / 海报：无参考的方形生成把官方角色画成普通兔子。改用已通过身份检查的 Aigram 高潮栅格裁切，准确排版标题。
- P2 / QA 截图：结果页首次截图发生在 420 ms 淡入中。等待 650 ms 后同状态复验。

## Recheck

- 390 × 844 与 320 × 568：无横向或纵向溢出。
- 触控目标：声音 48 × 48 px；五个热点最小边均大于 73 px。
- 控制台与页面错误：0。
- 外部访客栏：存在且游戏仍可操作；平台主构图未为访客栏下移。
- 视频：六个 SHA-256 均唯一，H.264 768 × 1024，约 5.04 秒。
- 评分：层级 5、连贯性 4、可读性 5、手感 4、资产质量 4、响应式 5、完成度 4；平均 4.43，无低于 3 的项目。
