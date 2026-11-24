import styles from './CodeViewer.module.css';
import Icon from './Icon';
const steps = [
  ['01', '找到你的起点', '梳理已有基础，明确想要解决的问题。'],
  ['02', '把目标变成行动', '给学习、动手与复习，留出各自的时间。'],
  ['03', '用练习检验理解', '通过测验，发现那些“以为懂了”的知识。'],
  ['04', '从反馈里再学一点', '查看解析，带着新问题回到实践中。'],
];
export default function CodeViewer() {
  return <aside className={styles.panel}>
    <div className={styles.guideIntro}><span className={styles.guideIcon}><Icon name="path" size={23} /></span><p className={styles.eyebrow}>LEARN AT YOUR OWN PACE</p><h2 className={styles.title}>每一步，都算数。</h2><p className={styles.intro}>不用急着抵达终点，<br />先找到适合自己的节奏。</p></div>
    <p className={styles.listLabel}>一条简单的学习路径</p>
    <div>{steps.map(([n, title, text]) => <section className={styles.step} key={n}><span className={styles.number}>{n}</span><div><h3>{title}</h3><p>{text}</p></div></section>)}</div>
    <div className={styles.note}><span><Icon name="spark" size={17} /> 给今天的小建议</span><h4>试着把它讲给别人听。</h4><p>练习后，用自己的话解释一个概念。讲清楚的过程，也是重新理解的过程。</p><div className={styles.noteBottom}><span /> 学一点，做一点，再进一步。</div></div>
    <div className={styles.footer}><span><strong>07</strong>学习阶段</span><i /><span><strong>10</strong>基础测验</span></div>
  </aside>;
}
