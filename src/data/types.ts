export type Skill = {
  name: string;
  owner: string;
  full_name?: string;
  repo_url: string;
  description?: string;
  stars: number;
  forks: number;
  topics?: string[];
  primary_language?: string | null;
  created_at?: string;
  updated_at?: string;
  pushed_at?: string;
  license?: string | null;
  readme_summary?: string;
  skill_type?: string;
  category?: string;
  download_url: string;
  weekly_star_delta?: number | null;
  previous_stars?: number | null;
  current_stars?: number;
  last_checked_at?: string;
  score?: number;
  recommendation?: string;
  usage_scenarios?: string;
  growth_rate?: number | null;
  token_saving?: {
    token_reduction_method: string;
    best_for: string;
    adoption_threshold: string;
    recommendation: string;
  };
  office_output?: {
    file_types: string[];
    content_fit: string;
    extra_dependencies: string;
    recommendation: string;
  };
};

export type SkillsData = {
  generated_at: string | null;
  last_checked_at: string | null;
  snapshot_date: string | null;
  is_first_run: boolean;
  warnings: string[];
  stats: {
    total_skills: number;
    total_stars: number;
    token_saving_count: number;
    office_count: number;
    radar_category_count: number;
  };
  featured_token_saving: Skill[];
  featured_office: Skill[];
  top_stars: Skill[];
  top_growth: Skill[];
  radar: Record<string, Skill[]>;
  skills: Skill[];
};
