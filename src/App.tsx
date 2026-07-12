import { Moon, Search, SlidersHorizontal, Sun } from 'lucide-react';
import { useMemo, useState } from 'react';
import rawData from '../data/processed/skills.json';
import LeaderboardTable from './components/LeaderboardTable';
import RadarSection from './components/RadarSection';
import SkillCard from './components/SkillCard';
import type { Skill, SkillsData } from './data/types';

const data = rawData as SkillsData;
const numberFormat = new Intl.NumberFormat('en-US');

type SortKey = 'score' | 'stars' | 'growth' | 'recent';

function formatDateTime(value: string | null) {
  if (!value) return '尚未采集';
  return new Intl.DateTimeFormat('zh-CN', {
    dateStyle: 'full',
    timeStyle: 'short'
  }).format(new Date(value));
}

function getSortValue(skill: Skill, sort: SortKey) {
  if (sort === 'stars') return skill.stars || 0;
  if (sort === 'growth') return skill.weekly_star_delta ?? -1;
  if (sort === 'recent') return new Date(skill.updated_at || skill.pushed_at || 0).getTime();
  return skill.score || 0;
}

function App() {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('全部');
  const [sort, setSort] = useState<SortKey>('score');
  const [light, setLight] = useState(false);

  const categories = useMemo(() => {
    const values = new Set(data.skills.map((skill) => skill.category).filter(Boolean) as string[]);
    return ['全部', ...Array.from(values).sort((a, b) => a.localeCompare(b, 'zh-CN'))];
  }, []);

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return data.skills
      .filter((skill) => {
        const inCategory = category === '全部' || skill.category === category;
        if (!inCategory) return false;
        if (!needle) return true;
        return [
          skill.name,
          skill.owner,
          skill.description,
          skill.readme_summary,
          skill.category,
          skill.skill_type,
          ...(skill.topics || [])
        ]
          .join(' ')
          .toLowerCase()
          .includes(needle);
      })
      .sort((a, b) => getSortValue(b, sort) - getSortValue(a, sort));
  }, [category, query, sort]);

  return (
    <main className={light ? 'app light' : 'app'}>
      <header className="hero">
        <nav className="topbar">
          <span className="brand">AI Agent Skills Weekly</span>
          <button className="icon-button" type="button" onClick={() => setLight((value) => !value)} aria-label="切换亮暗模式">
            {light ? <Moon size={18} /> : <Sun size={18} />}
          </button>
        </nav>
        <div className="hero-grid">
          <div>
            <p className="eyebrow">每周自动更新</p>
            <h1>AI Agent Skills 周报</h1>
            <p className="hero-copy">
              自动收集 GitHub 上与 Agent Skill、Codex Skill、Cursor Rule、MCP、文档输出、Token 节省相关的开源项目，保留历史快照并计算 Star 增长。
            </p>
            <div className="status-row">
              <span>本周更新时间：{formatDateTime(data.last_checked_at)}</span>
              <span>{data.is_first_run ? '首次采集，暂无增长数据' : `快照日期：${data.snapshot_date}`}</span>
            </div>
          </div>
          <div className="stats-panel" aria-label="数据概览">
            <div>
              <strong>{numberFormat.format(data.stats.total_skills)}</strong>
              <span>收录项目</span>
            </div>
            <div>
              <strong>{numberFormat.format(data.stats.total_stars)}</strong>
              <span>累计 Stars</span>
            </div>
            <div>
              <strong>{data.stats.token_saving_count}</strong>
              <span>Token 节省精选</span>
            </div>
            <div>
              <strong>{data.stats.office_count}</strong>
              <span>Office 输出精选</span>
            </div>
          </div>
        </div>
        {data.warnings.length > 0 && (
          <div className="notice">
            {data.warnings.map((warning) => (
              <span key={warning}>{warning}</span>
            ))}
          </div>
        )}
      </header>

      <section className="section">
        <div className="section-title">
          <p className="eyebrow">Featured</p>
          <h2>精选：减少 Token 消耗的 Skill</h2>
          <p>关注 token reduction、context compression、prompt compression、summarization、long context management 和 prompt optimization。</p>
        </div>
        <div className="card-grid">
          {data.featured_token_saving.map((skill) => (
            <SkillCard skill={skill} key={`token-${skill.owner}/${skill.name}`} />
          ))}
        </div>
      </section>

      <section className="section">
        <div className="section-title">
          <p className="eyebrow">Featured</p>
          <h2>精选：Office / Word / PPT / PDF 输出 Skill</h2>
          <p>覆盖 DOCX、PPTX、XLSX、PDF、文档排版、报告生成、slide generation 和 office automation。</p>
        </div>
        <div className="card-grid">
          {data.featured_office.map((skill) => (
            <SkillCard skill={skill} key={`office-${skill.owner}/${skill.name}`} />
          ))}
        </div>
      </section>

      <LeaderboardTable title="总 Star 榜 Top 50" items={data.top_stars} mode="stars" />
      <LeaderboardTable
        title="Star 增长最快榜"
        items={data.top_growth}
        mode="growth"
        emptyText="首次采集，暂无增长数据。下周快照生成后会自动计算本周新增 Stars。"
      />

      <RadarSection radar={data.radar} />

      <section className="section">
        <div className="section-title">
          <p className="eyebrow">Explore</p>
          <h2>全部 Skill 搜索</h2>
        </div>
        <div className="toolbar">
          <label className="search-box">
            <Search size={18} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索名称、简介、标签、分类..." />
          </label>
          <label className="select-box">
            <SlidersHorizontal size={18} />
            <select value={category} onChange={(event) => setCategory(event.target.value)}>
              {categories.map((item) => (
                <option value={item} key={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <label className="select-box">
            <select value={sort} onChange={(event) => setSort(event.target.value as SortKey)}>
              <option value="score">按推荐分</option>
              <option value="stars">按 Stars</option>
              <option value="growth">按本周增长</option>
              <option value="recent">按最近更新</option>
            </select>
          </label>
        </div>
        <div className="result-count">当前显示 {filtered.length} / {data.skills.length}</div>
        <div className="card-grid">
          {filtered.slice(0, 80).map((skill) => (
            <SkillCard skill={skill} key={`all-${skill.owner}/${skill.name}`} />
          ))}
        </div>
      </section>
    </main>
  );
}

export default App;
