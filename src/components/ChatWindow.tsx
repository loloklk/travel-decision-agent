import { useEffect, useRef } from 'react';
import type { Message } from '../types';
import { useT } from '../i18n';
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
  const { lang } = useT();

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
          <div className={styles.hero}>
            <div className={styles.heroCopy}>
              <span className={styles.eyebrow}>MAKE ROOM TO GROW</span>
              <h2>{lang === 'zh' ? <>每一次学习，<br />都在<em>向前一步。</em></> : <>Small steps.<br /><em>Deeper learning.</em></>}</h2>
              <p>{lang === 'zh' ? '我是你的深度学习伙伴。一起把好奇心，变成看得见的进步。' : 'Your companion for deep learning. Turn curiosity into steady progress.'}</p>
            </div>
            <img src="/assets/study-notebook-pexels-6192754.jpg" alt="蓝色桌面上的打开的方格笔记本、铅笔和橡皮实拍照片" />
          </div>
          <p className={styles.photoCredit}><a href="https://www.pexels.com/photo/a-notebook-on-a-blue-surface-6192754/" target="_blank" rel="noopener noreferrer">Photo: KATRIN BOLOVTSOVA / Pexels ↗</a></p>
          <p className={styles.sectionLabel}>从这里，开始今天的学习<small>CHOOSE YOUR NEXT STEP</small></p>
          <div className={styles.cards}>
            {([
              ['path', '规划学习路线', '找到适合你的起点与方向', '我是零基础，请给我一份深度学习学习路线。'],
              ['calendar', '制定每日计划', '把大目标，拆成每日小行动', '我有 Python 基础，请按入门水平制定14天深度学习计划，每天60分钟。'],
              ['quiz', '来一组小测验', '用几道题，检验你的理解', '出3道深度学习综合选择题，先不要告诉我答案。'],
              ['check', '专项巩固练习', '从 CNN 开始，练透一个主题', '出2道CNN选择题，先不要告诉我答案。'],
            ] as const).map(([icon, title, description, prompt]) => <button className={styles.card} key={title} onClick={() => onSend(prompt)} disabled={loading}>
              <span className={styles.cardIcon}><Icon name={icon} size={18} /></span><div><strong>{title}</strong><p>{description}</p></div><span className={styles.cardArrow}><Icon name="arrow" size={13} /></span>
            </button>)}
          </div>
          <p className={styles.emptyNote}>不急于学完所有，只专注今天的一点进步。</p>
        </div>
      )}

      {messages.map(msg => (
        <ChatBubble key={msg.id} message={msg} />
      ))}

      {showTypingIndicator && (
        <div className={styles.typingRow}>
          <div className={styles.avatar}><Icon name="spark" size={16} /></div>
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
