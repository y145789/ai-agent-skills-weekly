import { Download, ExternalLink } from 'lucide-react';
import type { Skill } from '../data/types';

type Props = {
  title: string;
  items: Skill[];
  mode: 'stars' | 'growth';
  emptyText?: string;
};

const numberFormat = new Intl.NumberFormat('en-US');
const percentFormat = new Intl.NumberFormat('zh-CN', {
  style: 'percent',
  maximumFractionDigits: 1
});

function dateText(value?: string) {
  if (!value) return '未知';
  return new Intl.DateTimeFormat('zh-CN', { month: 'short', day: 'numeric' }).format(new Date(value));
}

export default function LeaderboardTable({ title, items, mode, emptyText }: Props) {
  return (
    <section className="section">
      <div className="section-title">
        <p className="eyebrow">Leaderboard</p>
        <h2>{title}</h2>
      </div>
      {items.length === 0 ? (
        <div className="empty-state">{emptyText || '暂无数据'}</div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              {mode === 'stars' ? (
                <tr>
                  <th>排名</th>
                  <th>名称</th>
                  <th>简介</th>
                  <th>Stars</th>
                  <th>Forks</th>
                  <th>最近更新</th>
                  <th>分类</th>
                  <th>链接</th>
                </tr>
              ) : (
                <tr>
                  <th>排名</th>
                  <th>名称</th>
                  <th>本周新增</th>
                  <th>当前</th>
                  <th>上周</th>
                  <th>增长率</th>
                  <th>简介</th>
                  <th>链接</th>
                </tr>
              )}
            </thead>
            <tbody>
              {items.map((skill, index) =>
                mode === 'stars' ? (
                  <tr key={`${skill.owner}/${skill.name}`}>
                    <td>{index + 1}</td>
                    <td className="name-cell">{skill.name}</td>
                    <td>{skill.description || skill.readme_summary}</td>
                    <td>{numberFormat.format(skill.stars || 0)}</td>
                    <td>{numberFormat.format(skill.forks || 0)}</td>
                    <td>{dateText(skill.updated_at)}</td>
                    <td>{skill.category}</td>
                    <td>
                      <div className="link-pair">
                        <a href={skill.repo_url} target="_blank" rel="noreferrer" aria-label={`${skill.name} 仓库`}>
                          <ExternalLink size={16} />
                        </a>
                        <a href={skill.download_url} target="_blank" rel="noreferrer" aria-label={`${skill.name} 下载`}>
                          <Download size={16} />
                        </a>
                      </div>
                    </td>
                  </tr>
                ) : (
                  <tr key={`${skill.owner}/${skill.name}`}>
                    <td>{index + 1}</td>
                    <td className="name-cell">{skill.name}</td>
                    <td className="growth-cell">+{numberFormat.format(skill.weekly_star_delta || 0)}</td>
                    <td>{numberFormat.format(skill.current_stars || skill.stars || 0)}</td>
                    <td>{skill.previous_stars === null || skill.previous_stars === undefined ? '无' : numberFormat.format(skill.previous_stars)}</td>
                    <td>{skill.growth_rate ? percentFormat.format(skill.growth_rate) : '无'}</td>
                    <td>{skill.description || skill.readme_summary}</td>
                    <td>
                      <div className="link-pair">
                        <a href={skill.repo_url} target="_blank" rel="noreferrer" aria-label={`${skill.name} 仓库`}>
                          <ExternalLink size={16} />
                        </a>
                        <a href={skill.download_url} target="_blank" rel="noreferrer" aria-label={`${skill.name} 下载`}>
                          <Download size={16} />
                        </a>
                      </div>
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
