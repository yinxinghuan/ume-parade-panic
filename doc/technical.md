# Technical

## 1. 技术栈

- React 18 + TypeScript：实现七阶段媒体状态机、五个热点、进度、错误恢复与双语界面。
- Less：实现夏日花车视觉系统、响应式 HUD、触控状态、纸花热点与完成粒子。
- Vite 5：使用 `base: './'` 输出可部署到任意子路径的 `dist/`。
- HTML5 Video：播放 H.264/AAC、768 × 1024、约 5.04 秒的六段互动短片，使用 `playsInline` 兼容移动 WebView。
- Web Audio API：首次交互后合成点击、支线完成、全员就位与高潮和弦。
- Aigram 制作接口：图片经 transit 接口严格串行生成；视频经 2026-06-29 正式首尾帧接口按最多两任务、错峰 20 秒生成。
- Aigram Runtime Rank API：通关上传时间成绩、读取 UUID 隔离排行榜并发送 `score_beat` 通知。

## 2. 目录结构

- `src/Game/VideoQuest.tsx`：状态机、五个热点、六段视频、静态回退、高潮与结果页。
- `src/Game/VideoQuest.less`：花车主题 UI、品牌吊牌、进度、热点、字幕、粒子和响应式规则。
- `src/Game/i18n.ts`：中文与英文文案及语言检测。
- `src/Game/sounds.ts`：Web Audio 合成声效。
- `src/Game/CompletionRanking.tsx/.less`：通关计时、时间成绩编码、冠军入口、完整榜单、资料跳转与通知。
- `src/shared/runtime/`、`src/shared/leaderboard/useGameScore.ts`：平台桥接、排名读写和事件上报。
- `src/game-id.ts`：永久游戏 UUID，由平台脚本从 `games.json` 注入。
- `public/hero.png`：只包含粉色兔子的主场景首帧。
- `public/frames/end_*.png`：五名成员支线尾帧、粉兔子高潮和奶茶内部结尾。
- `public/videos/clip_01_*.mp4` 至 `clip_06_climax.mp4`：五条支线与高潮短片。
- `public/brand/ume-logo.png`：从品牌手册透明渲染的官方组合 Logo。
- `public/poster.png`：Aigram 高潮栅格图裁切并加准确标题的 1024 × 1024 海报。
- `_production/`：串行生图、正式视频与海报收尾脚本及接口结果 URL。
- `_qa/ui/`：平台布局、外部访客栏、窄屏、视频接触表与海报缩略图证据。

## 3. 核心模块

- 状态管理：`Phase` 为 `idle / playing / holding / climaxReady / climaxPlaying / revelation / done`；`seen` Set 记录五条支线首次完成。
- 视频流程：点击热点后显示对应 MP4，700 ms 后显示字幕；视频结束停留 1,500 ms，再点亮路线节点。错误时切换尾帧，3,200 ms 后走相同完成路径。
- 高潮流程：五条支线完成后延迟 500 ms 显示启动按钮；高潮在 2,800 ms 显示字幕，结束后停留 2,800 ms 进入结果。
- 屏幕适配：舞台最大宽度 480 px，高度 `100dvh`；媒体使用 `object-fit: cover` 覆盖 320 × 568 至 480 × 960。
- 输入与无障碍：游戏动作使用 `onPointerDown`，键盘 Enter/Space 有等价路径；声音使用 `onClick`；所有目标至少 44 × 44 px。
- 音频：单一 AudioContext 合成四组反馈；静音或音频失败不影响状态机。
- 国际化：`localStorage.game_locale` 可覆盖 `zh/en`，否则跟随浏览器语言。
- 外部扩展：`index.html` 仅一次加载远程 `guest-shell.js`；生产 CSS 不隐藏访客栏。
- 通关排名：首次异常启动 `performance.now()` 计时，高潮视频结束停止；上传 `max(10, 10,000,000 - round(durationMs / 10))`，榜单还原显示为 `mm:ss.t`。所有通关成绩都达到平台可配置的 10 分领券门槛；成绩上传不预判登录，外部榜单入口显示 AlterU 下载 CTA。

## 4. 扩展点

- 增加支线：修改 `VideoQuest.tsx` 的 `CLIPS`，同步增加双语文案、尾帧、视频和生成记录。
- 调整热点：修改 `CLIPS` 的百分比 `top / left / width / height`。
- 更换剧情与台词：修改 `src/Game/i18n.ts`。
- 调整视觉与反馈：修改 `VideoQuest.less` 的色彩 token、阴影、进度形状和动画。
- 调整时序：修改 `VideoQuest.tsx` 顶部的字幕、停留与错误回退常量。
- 更新素材：运行 `_production/generate_frames.py` 时图片保持严格串行；视频脚本保持最多两任务与 20 秒错峰。
- 发布：保持 `meta.json`、`games.json`、双份海报、永久 UUID 和 GitHub Pages 工作流一致。
