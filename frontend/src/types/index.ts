export interface Detection {
  id?: string;
  user_id?: string;
  detection_type: string;
  content_path?: string;
  threat_score: number;
  confidence_score: number;
  threat_category: string;
  analysis_results: {
    details: string;
    indicators: string[];
  };
  remediation_suggestions: {
    actions: string[];
    priority: string;
  };
  created_at?: string;
  updated_at?: string;
}

export interface User {
  id: string;
  email: string;
  username?: string;
  full_name?: string;
  department?: string;
  role?: string;
  created_at?: string;
  updated_at?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface DashboardStats {
  total_detections: number;
  recent_threats: {
    critical: number;
    high: number;
    moderate: number;
    low: number;
  };
  threat_categories: {
    phishing: number;
    malware: number;
    spam: number;
    suspicious: number;
  };
  detection_history: Array<{
    date: string;
    count: number;
  }>;
} 