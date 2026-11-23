import { useState, useRef, useCallback, KeyboardEvent } from 'react';
import { useT } from '../i18n';
import styles from './ChatInput.module.css';

interface Props {
  onSend: (text: string) => void;
  onStop: () => void;
  onClear: () => void;
  disabled: boolean;
}

const PRESETS = [['规划路线', '我是零基础，请给我一份深度学习路线。'], ['14天学习计划', '我有 Python 基础，请按入门水平制定14天深度学习计划，每天60分钟。'], ['出3道题', '出3道深度学习综合选择题，先不要告诉我答案。']] as const;

export default function ChatInput({ onSend, onStop, onClear, disabled }: Props) {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { t } = useT();

  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  }, [value, disabled, onSend]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 140)}px`;
  };

  const handlePreset = (text: string) => {
    if (disabled) return;
    onSend(text);
  };

  return (
    <div className={styles.bar}>
      <div className={styles.presets}>
        {PRESETS.map(([label, prompt]) => (
          <button
            key={label}
            className={styles.presetChip}
            onClick={() => handlePreset(prompt)}
            disabled={disabled}
          >
            <span aria-hidden="true">＋</span>{label}
          </button>
        ))}
      </div>

      <div className={`${styles.inputWrap} ${disabled ? styles.inputDisabled : ''}`}>
        <textarea
          ref={textareaRef}
          className={styles.textarea}
          placeholder={t("chat.placeholder")}
          aria-label="输入学习目标或测验答案"
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          rows={1}
          disabled={disabled}
        />
        <button
          className={`${styles.sendBtn} ${(!value.trim() || disabled) ? styles.sendDisabled : ''}`}
          onClick={handleSend}
          disabled={!value.trim() || disabled}
          aria-label={t("aria.send")}
        >
          <svg viewBox="0 0 20 20" fill="none" width="16" height="16">
            <path d="M10 16V4m-5 5 5-5 5 5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
        <button
          className={styles.clearBtn}
          onClick={onClear}
          disabled={disabled}
          aria-label={t("aria.clearHistory")}
          title={t("aria.clearHistory")}
        >
          <svg viewBox="0 0 24 24" fill="none" width="16" height="16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
            <path d="M10 11v6"/>
            <path d="M14 11v6"/>
            <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
          </svg>
        </button>
        {disabled && (
          <button
            className={styles.stopBtn}
            onClick={onStop}
            aria-label={t("aria.stopGeneration")}
            title={t("aria.stopGeneration")}
          >
            <svg viewBox="0 0 20 20" fill="none" width="14" height="14">
              <rect x="4" y="4" width="12" height="12" rx="2" fill="currentColor"/>
            </svg>
          </button>
        )}
      </div>
      <p className={styles.hint}>{t("chat.hint")}</p>
    </div>
  );
}
