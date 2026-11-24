import { useEffect, useRef } from 'react';
import type { Message } from '../types';
import ChatBubble from './ChatBubble';
import styles from './ChatWindow.module.css';
import Icon from './Icon';

interface Props {
  messages: Message[];
  loading: boolean;
  onSend: (text: string) => void;
}

export default function ChatWindow({ messages, loading, onSend }: Props) {
  const windowRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (messages.length === 0 && !loading) return;
    const el = windowRef.current;
    if (!el) return;
    el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
  }, [messages, loading]);

  const lastMsg = messages[messages.length - 1];
  /**
   * Three-dot typing row only fills the "waiting for first token" gap.
   * Once the assistant bubble has any content, the in-bubble streamingCaret
   * takes over the "still working" signal — so we never end up with two
   * stacked bot bubbles for the same in-flight turn.
   */
  const showTypingIndicator = loading && !(lastMsg?.role === 'assistant' && lastMsg.content.length > 0);

  return (
    <div ref={windowRef} className={styles.window}>
      {messages.length === 0 && (
        <div className={styles.empty}>
          <div className={styles.welcomeHeading}>
            <div><p className={styles.welcomeKicker}>好奇，是一切进步的开始</p><h1>今天，想学点什么？</h1></div>
            <span className={styles.welcomeMark}><Icon name="spark" size={25} /></span>
          </div>
          <div className={styles.hero}>
            <div className={styles.heroCopy}>
              <span className={styles.eyebrow}><Icon name="spark" size={13} /> 你的 AI 学习伙伴</span>
              <h2>把想学的，<br />变成<em>真正学会的。</em></h2>
              <p>从一个好问题，到一次动手实践。<br />知序陪你，把深度学习变得有迹可循。</p>
              <button className={styles.heroAction} onClick={() => onSend('我想开始学习深度学习，请先了解我的基础、目标和每天可用的时间，再帮我规划学习路线。')} disabled={loading}>开启一段新学习 <Icon name="arrow" size={16} /></button>
            </div>
            <div className={styles.heroVisual}>
              <img src="/assets/study-notebook-pexels-6192754.jpg" alt="蓝色桌面上打开的方格笔记本、铅笔与橡皮" />
              <span className={styles.imageLabel}><Icon name="book" size={15} /> 留一点时间，给新的可能</span>
              <a className={styles.photoCredit} href="https://www.pexels.com/photo/a-notebook-on-a-blue-surface-6192754/" target="_blank" rel="noopener noreferrer">KATRIN BOLOVTSOVA / Pexels ↗</a>
            </div>
          </div>
          <div className={styles.sectionLabel}><div><h3>从这里开始</h3><p>选一个方向，让今天的学习更具体。</p></div><span>四种方式 · 一步向前</span></div>
          <div className={styles.cards}>
            {([
              ['path', '规划学习路线', '从已有基础出发，找到适合你的学习顺序。', '我是零基础，请给我一份深度学习学习路线。', '7 个学习阶段'],
              ['calendar', '安排每日计划', '把一个大目标，拆成每天能完成的小行动。', '我有 Python 基础，请按入门水平制定14天深度学习计划，每天60分钟。', '按你的时间安排'],
              ['quiz', '检验知识掌握', '来一组随堂测验，看看哪些知识还不够扎实。', '出3道深度学习综合选择题，先不要告诉我答案。', '6 个测验主题'],
              ['check', '巩固薄弱环节', '从 CNN 专项练习开始，在反馈中逐步进步。', '出2道CNN选择题，先不要告诉我答案。', '练习 → 批改 → 复盘'],
            ] as const).map(([icon, title, description, prompt, meta]) => <button className={styles.card} key={title} onClick={() => onSend(prompt)} disabled={loading}>
              <div className={styles.cardTop}><span className={styles.cardIcon}><Icon name={icon} size={21} /></span><span className={styles.cardArrow}><Icon name="arrow" size={17} /></span></div>
              <strong>{title}</strong><p>{description}</p><span className={styles.cardMeta}>{meta}</span>
            </button>)}
          </div>
          <p className={styles.emptyNote}><span /> 不用一次学完所有，只要比昨天多懂一点。</p>
        </div>
      )}

      {messages.map(msg => (
        <ChatBubble key={msg.id} message={msg} />
      ))}

      {showTypingIndicator && (
        <div className={styles.typingRow}>
          <div className={styles.avatar}><img src="/assets/zhixu-logo.svg" alt="知序" width={28} height={28} /></div>
          <div className={styles.typing}>
            <span />
            <span />
            <span />
          </div>
        </div>
      )}
    </div>
  );
}
