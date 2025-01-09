import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://uzgpjmvmoncwmfkbeknr.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6Z3BqbXZtb25jd21ma2Jla25yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzYzMjA1NTAsImV4cCI6MjA1MTg5NjU1MH0.UXEuxEAzbRzS3sg9F_LWhrVZNuAEpPbU4L_FgxQ90Oc';

export const supabase = createClient(supabaseUrl, supabaseKey);

interface UserData {
  username: string;
  full_name: string;
  department: string;
  role: string;
}

interface Detection {
  id: string;
  user_id: string;
  detection_type: 'image' | 'text' | 'multimodal';
  content_path: string;
  threat_score: number;
  confidence_score: number;
  analysis_results: {
    details: string;
    indicators?: string[];
    severity?: string;
  };
  threat_category: string;
  remediation_suggestions: {
    actions: string[];
    priority?: string;
    description?: string;
  };
  created_at: string;
  updated_at: string;
}

// Auth helpers
export const auth = {
  signUp: async (email: string, password: string, userData: UserData) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: userData,
      },
    });
    if (error) throw error;
    return data;
  },

  signIn: async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    if (error) throw error;
    return data;
  },

  signOut: async () => {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
  },

  getUser: async () => {
    const { data: { user }, error } = await supabase.auth.getUser();
    if (error) throw error;
    return user;
  },
};

// Detection helpers
export const detection = {
  createDetection: async (detectionData: Omit<Detection, 'id' | 'created_at' | 'updated_at'>) => {
    const { data, error } = await supabase
      .from('detections')
      .insert(detectionData)
      .select()
      .single();
    if (error) throw error;
    return data as Detection;
  },

  getHistory: async () => {
    const { data, error } = await supabase
      .from('detections')
      .select('*')
      .order('created_at', { ascending: false });
    if (error) throw error;
    return data as Detection[];
  },

  getStats: async () => {
    const { data, error } = await supabase
      .from('detections')
      .select('*');
    if (error) throw error;
    return data as Detection[];
  },
}; 