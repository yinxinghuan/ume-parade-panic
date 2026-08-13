export type Locale = 'zh' | 'en';

function detectLocale(): Locale {
  if (typeof window === 'undefined') return 'zh';
  try {
    const override = window.localStorage.getItem('game_locale');
    if (override === 'zh' || override === 'en') return override;
  } catch {
    // Browser language remains the fallback in restricted WebViews.
  }
  return navigator.language.toLowerCase().startsWith('zh') ? 'zh' : 'en';
}

const LOCALE = detectLocale();
const STRINGS: Record<Locale, Record<string, string>> = {
  zh: {
    'title.eyebrow': 'UMe FAMILY 夏日巡游',
    'title.main': '奶茶花车大救场',
    'hint.first': '先点西瓜彩纸炮，看看谁把它拧过头了',
    'progress': '巡游路线 {n}/5',
    'hotspot.melon': '检查西瓜彩纸炮',
    'hotspot.lemon': '转动黄色泡泡阀',
    'hotspot.guac': '摇一下绿色横幅齿轮',
    'hotspot.mango': '踩下芒果色节拍器',
    'hotspot.pearl': '碰一下顶部的珍珠气球扣',
    'sub.melon': '鼠瓜瓜只想放一张彩纸。炮筒听成了一整条彩虹。',
    'sub.lemon': '柠檬鲨把泡泡调成了“自带座舱”。',
    'sub.guac': '果泥猪卷好了横幅，横幅也顺手卷好了它。',
    'sub.mango': '芒芒鸡踩准一拍，五面小旗全抢着登场。',
    'sub.pearl': '珍珠天使抓住了气球扣，也被气球扣抓上了天。',
    'sub.climax': '巨型吸管归位，整辆花车像一杯奶茶亮了起来。',
    'climax.ready': '五个装置都已复位',
    'climax.button': '启动奶茶花车',
    'done.eyebrow': '巡游出发',
    'done.title': '这杯快乐，沿街送达',
    'done.body': '彩纸落下前，第一杯已经递到了观众手里。',
    'done.again': '再巡游一次',
    'done.time': '通关时间',
    'rank.title': '通关排行榜',
    'rank.leaders': '排行榜',
    'rank.me': '我',
    'rank.empty': '还没有通关记录，来当第一名吧！',
    'rank.loading': '正在读取通关记录…',
    'rank.openInAlterU': '在 AlterU 中打开即可查看通关排行榜。',
    'rank.getAlterU': '下载 AlterU',
    'rank.close': '关闭排行榜',
    'video.fallback': '花车卡了一下，先看事故现场',
    'sound.on': '关闭声音',
    'sound.off': '打开声音',
  },
  en: {
    'title.eyebrow': 'UMe FAMILY SUMMER PARADE',
    'title.main': 'PARADE PANIC',
    'hint.first': 'Tap the watermelon cannon. Someone over-cranked it.',
    'progress': 'Route {n}/5',
    'hotspot.melon': 'Check the watermelon confetti cannon',
    'hotspot.lemon': 'Turn the yellow bubble valve',
    'hotspot.guac': 'Turn the green banner gear',
    'hotspot.mango': 'Step on the mango beat pedal',
    'hotspot.pearl': 'Tap the pearl balloon clasp',
    'sub.melon': 'MelonMick asked for one confetti pop. The cannon heard rainbow.',
    'sub.lemon': 'LemonShark set the bubble to personal cabin.',
    'sub.guac': 'GuacPiggy rolled the banner. The banner rolled GuacPiggy.',
    'sub.mango': 'MangoChick hit one beat. Five flags demanded an encore.',
    'sub.pearl': 'BubblePearl caught the clasp. The balloons caught BubblePearl.',
    'sub.climax': 'The giant straw clicked in, and the whole float lit up like a cup.',
    'climax.ready': 'ALL FIVE FIXES READY',
    'climax.button': 'START THE FLOAT',
    'done.eyebrow': 'PARADE SAVED',
    'done.title': 'Joy, served curbside.',
    'done.body': 'The first cup reached the crowd before the confetti landed.',
    'done.again': 'PARADE AGAIN',
    'done.time': 'COMPLETION TIME',
    'rank.title': 'Completion leaderboard',
    'rank.leaders': 'LEADERS',
    'rank.me': 'me',
    'rank.empty': 'No completion times yet. Be the first!',
    'rank.loading': 'Loading completion times…',
    'rank.openInAlterU': 'Open in AlterU to view the completion leaderboard.',
    'rank.getAlterU': 'Get AlterU',
    'rank.close': 'Close leaderboard',
    'video.fallback': 'The float hiccupped. Here is the scene.',
    'sound.on': 'Mute sound',
    'sound.off': 'Turn sound on',
  },
};

export function t(key: string, vars?: { n?: number | string }): string {
  let value = STRINGS[LOCALE][key] ?? STRINGS.zh[key] ?? key;
  if (vars?.n !== undefined) value = value.replace('{n}', String(vars.n));
  return value;
}
