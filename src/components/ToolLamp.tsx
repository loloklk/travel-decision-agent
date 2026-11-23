import type { ToolLampState } from '../types';
import styles from './ToolLamp.module.css';
import Icon from './Icon';
const icons = { get_learning_path: 'path', create_study_plan: 'calendar', generate_quiz: 'quiz', grade_quiz: 'check' } as const;

interface Props {
  lamp: ToolLampState;
}

export default function ToolLamp({ lamp }: Props) {
  return (
    <div className={`${styles.lamp} ${lamp.active ? styles.active : ''}`}>
      {/* key=animKey re-mounts the span on each activation so the CSS animation replays from the start. */}
      <span key={lamp.animKey} className={styles.icon}><Icon name={icons[lamp.id as keyof typeof icons] || 'spark'} size={13} /></span>
      <span className={styles.label}>{lamp.label}</span>
    </div>
  );
}
