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
  const topics = (skill.topics || []).slice(0, compact ? 3 : 6);

  return (
    <article className="skill-card">
      <div className="skill-card__head">
        <div>
          <p className="eyebrow">{skill.skill_type || 'Skill'}</p>
          <h3>{skill.name}</h3>
        </div>
        <span className="score-pill">{skill.recommendation || '★★★☆☆'}</span>
      </div>
      <p className="skill-card__desc">{skill.description || skill.readme_summary || '暂无简介'}</p>
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
        <button className="button button--ghost" type="button" onClick={() => setOpen((value) => !value)}>
          <ChevronDown size={16} className={open ? 'rotate' : ''} />
          详情
        </button>
      </div>
      {open && (
        <div className="detail-panel">
          <p>{skill.readme_summary || '暂无 README 摘要。'}</p>
          {skill.token_saving && (
            <dl>
              <dt>如何减少 token</dt>
              <dd>{skill.token_saving.token_reduction_method}</dd>
              <dt>适合场景</dt>
              <dd>{skill.token_saving.best_for}</dd>
              <dt>使用门槛</dt>
              <dd>{skill.token_saving.adoption_threshold}</dd>
            </dl>
          )}
          {skill.office_output && (
            <dl>
              <dt>文件类型</dt>
              <dd>{skill.office_output.file_types.join('、')}</dd>
              <dt>适合生成</dt>
              <dd>{skill.office_output.content_fit}</dd>
              <dt>依赖</dt>
              <dd>{skill.office_output.extra_dependencies}</dd>
            </dl>
          )}
        </div>
      )}
    </article>
  );
}
