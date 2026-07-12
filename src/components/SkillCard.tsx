import { ChevronDown, Download, ExternalLink, Star } from 'lucide-react';
import { useState } from 'react';
import type { Skill } from '../data/types';

type Props = {
  skill: Skill;
  compact?: boolean;
};

const numberFormat = new Intl.NumberFormat('en-US');

function formatDate(value?: string) {
  if (!value) return '未知';
  return new Intl.DateTimeFormat('zh-CN', { dateStyle: 'medium' }).format(new Date(value));
}

function deltaText(value?: number | null) {
  if (value === null || value === undefined) return '首次采集';
  if (value > 0) return `+${numberFormat.format(value)}`;
  return numberFormat.format(value);
}

export default function SkillCard({ skill, compact = false }: Props) {
  const [open, setOpen] = useState(false);
  const topics = (skill.topics || []).slice(0, compact ? 2 : 4);
  const summary = skill.description_zh || skill.readme_summary || skill.description || '暂无中文简介';

  return (
    <article className="skill-card">
      <div className="skill-card__head">
        <div>
          <p className="eyebrow">{skill.skill_type || 'Skill'}</p>
          <h3>{skill.name}</h3>
        </div>
        <span className="score-pill">{skill.recommendation || '★★★☆☆'}</span>
      </div>
      <div className={`description-block ${open ? 'description-block--open' : ''}`}>
        <p className="skill-card__desc">{summary}</p>
        {open && (
          <div className="description-block__detail">
            {skill.description && <p><strong>仓库原文</strong>{skill.description}</p>}
            <p><strong>适用场景</strong>{skill.usage_scenarios || '适合 Agent / Codex 工作流使用。'}</p>
            {skill.token_saving && (
              <dl>
                <dt>如何减少 Token</dt>
                <dd>{skill.token_saving.token_reduction_method}</dd>
                <dt>使用门槛</dt>
                <dd>{skill.token_saving.adoption_threshold}</dd>
              </dl>
            )}
            {skill.office_output && (
              <dl>
                <dt>支持文件</dt>
                <dd>{skill.office_output.file_types.join('、')}</dd>
                <dt>额外依赖</dt>
                <dd>{skill.office_output.extra_dependencies}</dd>
              </dl>
            )}
            {!skill.token_saving && !skill.office_output && skill.readme_summary && (
              <p><strong>README 摘要</strong>{skill.readme_summary}</p>
            )}
          </div>
        )}
        <button className="summary-toggle" type="button" onClick={() => setOpen((value) => !value)} aria-expanded={open}>
          <ChevronDown size={15} className={open ? 'rotate' : ''} />
          {open ? '收起简介' : '展开完整简介'}
        </button>
      </div>
      <div className="tag-row">
        <span className="tag tag--strong">{skill.category || '未分类'}</span>
        {topics.map((topic) => (
          <span className="tag" key={topic}>
            {topic}
          </span>
        ))}
      </div>
      <div className="metric-grid">
        <span>
          <Star size={15} />
          {numberFormat.format(skill.stars || 0)}
        </span>
        <span>本周 {deltaText(skill.weekly_star_delta)}</span>
        <span>更新 {formatDate(skill.updated_at)}</span>
      </div>
      {!compact && <p className="scenario">{skill.usage_scenarios || '适合 Agent / Codex 工作流使用。'}</p>}
      <div className="card-actions">
        <a className="button" href={skill.repo_url} target="_blank" rel="noreferrer">
          <ExternalLink size={16} />
          仓库
        </a>
        <a className="button button--secondary" href={skill.download_url} target="_blank" rel="noreferrer">
          <Download size={16} />
          下载
        </a>
      </div>
    </article>
  );
}
