import styles from './CodeViewer.module.css';
import Icon from './Icon';
const steps = [
  ['01', '找到你的起点', '梳理已有基础，选择适合自己的深度学习路线。'],
  ['02', '制定每日计划', '把可用时间分配给学习、动手练习与复习。'],
  ['03', '检验你的理解', '通过主题测验，发现那些“以为懂了”的知识点。'],
  ['04', '让反馈成为进步', '提交答案、查看解析，带着问题回到练习中。'],
];
export default function CodeViewer() {
  return <aside className={styles.panel}>
    <p className={styles.eyebrow}>A LITTLE, EVERY DAY</p>
    <h2 className={styles.title}>你的学习指南</h2>
    <p className={styles.intro}>不必一次学会所有。<br />从一个小目标开始，走好下一步。</p>
    <div>{steps.map(([n, title, text]) => <section className={styles.step} key={n}><span className={styles.number}>{n}</span><div><h3>{title}</h3><p>{text}</p></div></section>)}</div>
    <div className={styles.note}><span><Icon name="book" size={20} /></span><h4>学习的小建议</h4><p>每次练习后，用自己的话解释一个概念。能讲清楚，才更接近真正理解。</p></div>
    <p className={styles.footer}>7 个学习阶段 · 10 道基础测验</p>
  </aside>;
}
