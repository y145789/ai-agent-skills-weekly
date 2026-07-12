import type { Skill } from '../data/types';
import SkillCard from './SkillCard';

type Props = {
  radar: Record<string, Skill[]>;
};

export default function RadarSection({ radar }: Props) {
  const categories = Object.entries(radar).filter(([, items]) => items.length > 0);
  return (
    <section className="section">
      <div className="section-title">
        <p className="eyebrow">Skill Radar</p>
        <h2>实用 Skill 雷达</h2>
        <p>综合 Star、活跃度、README 质量、用途清晰度和 Agent 工作流适配度选出代表性项目。</p>
      </div>
      <div className="radar-stack">
        {categories.map(([category, items]) => (
          <div className="radar-group" key={category}>
            <div className="radar-group__title">
              <h3>{category}</h3>
              <span>{items.length} 个代表项目</span>
            </div>
            <div className="card-grid compact">
              {items.slice(0, 6).map((skill) => (
                <SkillCard skill={skill} compact key={`${category}-${skill.owner}/${skill.name}`} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
