type Name = 'spark' | 'book' | 'path' | 'calendar' | 'quiz' | 'check' | 'arrow' | 'panel' | 'menu' | 'close';
const paths: Record<Name, string> = {
  spark: 'm12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3Z',
  book: 'M12 5v15M12 5C9 3 5 3 2 4v15c3-1 7-1 10 1 3-2 7-2 10-1V4c-3-1-7-1-10 1Z',
  path: 'M5 4h10a4 4 0 0 1 0 8H9a4 4 0 0 0 0 8h10M16 17l3 3-3 3',
  calendar: 'M7 3v4M17 3v4M4 10h16M5 5h14a1 1 0 0 1 1 1v14H4V6a1 1 0 0 1 1-1ZM8 14h2M14 14h2M8 17h2',
  quiz: 'M8 3h8v4H8zM8 5H5v16h14V5h-3M8 11h8M8 15h5',
  check: 'm8 12 3 3 5-6M21 12a9 9 0 1 1-9-9',
  arrow: 'M5 12h14m-6-6 6 6-6 6',
  panel: 'M3 4h18v16H3zM15 4v16',
  menu: 'M4 6h16M4 12h16M4 18h16',
  close: 'm6 6 12 12M6 18 18 6',
};
export default function Icon({ name, size = 20 }: { name: Name; size?: number }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={paths[name]} /></svg>;
}
