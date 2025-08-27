// frontend/src/api/activities.ts
import { apiClient } from './client';

export interface ActivityType {
  id: number;
  name: string;
  description: string;
  icon: string;
  color: string;
  is_active: boolean;
  requires_duration: boolean;
  requires_outcome: boolean;
  created_at: string;
  updated_at: string;
}

export interface Activity {
  id: number;
  title: string;
  description: string;
  activity_type: ActivityType;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled' | 'overdue';
  priority: 'low' | 'medium' | 'high';
  scheduled_at: string;
  duration_minutes?: number;
  reminder_minutes_before?: number;
  reminder_sent: boolean;
  outcome?: 'successful' | 'unsuccessful' | 'no_answer' | 'callback_requested' | 'reschedule' | 'other';
  outcome_notes?: string;
  completed_at?: string;
  contact?: {
    id: number;
    first_name: string;
    last_name: string;
    full_name: string;
  };
  company?: {
    id: number;
    name: string;
  };
  opportunity?: {
    id: number;
    name: string;
  };
  assigned_to: {
    id: number;
    first_name: string;
    last_name: string;
    full_name: string;
  };
  created_by: {
    id: number;
    first_name: string;
    last_name: string;
  };
  is_overdue: boolean;
  estimated_end_time?: string;
  created_at: string;
  updated_at: string;
}

export interface TaskListItem {
  id: number;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high';
  due_date?: string;
  contact_name?: string;
  company_name?: string;
  opportunity_name?: string;
  assigned_to_name?: string;  // This is what your API actually returns
  is_overdue: boolean;
  created_at: string;
}

export interface Task {
  id: number;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high';
  due_date?: string;
  assigned_to: {
    id: number;
    first_name: string;
    last_name: string;
  };
  created_by: {
    id: number;
    first_name: string;
    last_name: string;
  };
  contact?: {
    id: number;
    first_name: string;
    last_name: string;
  };
  company?: {
    id: number;
    name: string;
  };
  opportunity?: {
    id: number;
    name: string;
  };
  completed_at?: string;
  completion_notes?: string;
  is_overdue: boolean;
  created_at: string;
  updated_at: string;
}

export interface InteractionLog {
  id: number;
  title: string;
  interaction_type: 'call_inbound' | 'call_outbound' | 'email_sent' | 'email_received' | 'meeting' | 'note' | 'sms' | 'other';
  notes: string;
  interaction_date: string;
  duration_minutes?: number;
  contact?: {
    id: number;
    first_name: string;
    last_name: string;
  };
  company?: {
    id: number;
    name: string;
  };
  opportunity?: {
    id: number;
    name: string;
  };
  logged_by: {
    id: number;
    first_name: string;
    last_name: string;
  };
  source_activity?: {
    id: number;
    title: string;
  };
  created_at: string;
  updated_at: string;
}

export interface FollowUpRule {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  trigger_activity_type: ActivityType;
  trigger_outcome: string;
  follow_up_activity_type: ActivityType;
  follow_up_delay_days: number;
  follow_up_title_template: string;
  follow_up_description_template: string;
  created_at: string;
  updated_at: string;
}

export interface ActivityStats {
  total_activities: number;
  completed_activities: number;
  overdue_activities: number;
  scheduled_today: number;
  scheduled_this_week: number;
  completion_rate: number;
  activities_by_type: Array<{ type: string; count: number; value: number }>;
  activities_by_status: Array<{ status: string; count: number }>;
  recent_completions: Activity[];
  upcoming_activities: Activity[];
}

export interface TaskStats {
  total_tasks: number;
  completed_tasks: number;
  overdue_tasks: number;
  due_today: number;
  due_this_week: number;
  completion_rate: number;
  tasks_by_priority: Array<{ priority: string; count: number }>;
  tasks_by_status: Array<{ status: string; count: number }>;
  recent_completions: Task[];
  upcoming_tasks: Task[];
}

export interface InteractionStats {
  total_interactions: number;
  interactions_this_week: number;
  interactions_this_month: number;
  average_duration: number;
  interactions_by_type: Array<{ type: string; count: number }>;
  daily_interactions: Array<{ date: string; count: number }>;
  recent_interactions: InteractionLog[];
}

export interface DashboardStats {
  activity_stats: ActivityStats;
  task_stats: TaskStats;
  interaction_stats: InteractionStats;
  productivity_score: number;
  weekly_activity_trend: number;
  todays_agenda: Array<{
    id: number;
    title: string;
    type: 'activity' | 'task';
    time?: string;
    priority: string;
  }>;
  overdue_items: Array<{
    id: number;
    title: string;
    type: 'activity' | 'task';
    overdue_days: number;
  }>;
}

// Form interfaces
export interface ActivityFormData {
  title: string;
  description: string;
  activity_type_id: number;
  priority: 'low' | 'medium' | 'high';
  scheduled_at: string;
  duration_minutes?: number;
  reminder_minutes_before?: number;
  contact_id?: number;
  company_id?: number;
  opportunity_id?: number;
  assigned_to_id: number;
}

export interface TaskFormData {
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high';
  due_date?: string;
  assigned_to_id: number;
  contact_id?: number;
  company_id?: number;
  opportunity_id?: number;
}

export interface InteractionLogFormData {
  title: string;
  interaction_type: 'call_inbound' | 'call_outbound' | 'email_sent' | 'email_received' | 'meeting' | 'note' | 'sms' | 'other';
  notes: string;
  interaction_date: string;
  duration_minutes?: number;
  contact_id?: number;
  company_id?: number;
  opportunity_id?: number;
}

export const activitiesApi = {
  // ACTIVITY TYPES
  getActivityTypes: async (): Promise<ActivityType[]> => {
    const response = await apiClient.get('/api/v1/activities/api/activity-types/');
    return response.data.results || response.data;
  },

  createActivityType: async (data: Partial<ActivityType>): Promise<ActivityType> => {
    const response = await apiClient.post('/api/v1/activities/api/activity-types/', data);
    return response.data;
  },

  updateActivityType: async (id: number, data: Partial<ActivityType>): Promise<ActivityType> => {
    const response = await apiClient.patch(`/api/v1/activities/api/activity-types/${id}/`, data);
    return response.data;
  },

  // ACTIVITIES
  getActivities: async (params?: Record<string, any>): Promise<{ results: Activity[]; count: number }> => {
    const response = await apiClient.get('/api/v1/activities/api/activities/', { params });
    return response.data;
  },

  getActivity: async (id: number): Promise<Activity> => {
    const response = await apiClient.get(`/api/v1/activities/api/activities/${id}/`);
    return response.data;
  },

  createActivity: async (data: ActivityFormData): Promise<Activity> => {
    const response = await apiClient.post('/api/v1/activities/api/activities/', data);
    return response.data;
  },

  updateActivity: async (id: number, data: Partial<ActivityFormData>): Promise<Activity> => {
    const response = await apiClient.patch(`/api/v1/activities/api/activities/${id}/`, data);
    return response.data;
  },

  deleteActivity: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/v1/activities/api/activities/${id}/`);
  },

  completeActivity: async (id: number, data: { outcome?: string; outcome_notes?: string }): Promise<Activity> => {
    const response = await apiClient.post(`/api/v1/activities/api/activities/${id}/complete/`, data);
    return response.data.activity;
  },

  getMyActivities: async (params?: Record<string, any>): Promise<Activity[]> => {
    const response = await apiClient.get('/api/v1/activities/api/activities/my_activities/', { params });
    return response.data;
  },

  getTodaysActivities: async (): Promise<Activity[]> => {
    const response = await apiClient.get('/api/v1/activities/api/activities/today/');
    return response.data;
  },

  getOverdueActivities: async (): Promise<{ count: number; activities: Activity[] }> => {
    const response = await apiClient.get('/api/v1/activities/api/activities/overdue/');
    return response.data;
  },

  getUpcomingActivities: async (): Promise<Activity[]> => {
    const response = await apiClient.get('/api/v1/activities/api/activities/upcoming/');
    return response.data;
  },

  // TASKS
  getTasks: async (params?: Record<string, any>): Promise<{ results: Task[]; count: number }> => {
    const response = await apiClient.get('/api/v1/activities/api/tasks/', { params });
    return response.data;
  },

  getTask: async (id: number): Promise<Task> => {
    const response = await apiClient.get(`/api/v1/activities/api/tasks/${id}/`);
    return response.data;
  },

  createTask: async (data: TaskFormData): Promise<Task> => {
    const response = await apiClient.post('/api/v1/activities/api/tasks/', data);
    return response.data;
  },

  updateTask: async (id: number, data: Partial<TaskFormData>): Promise<Task> => {
    const response = await apiClient.patch(`/api/v1/activities/api/tasks/${id}/`, data);
    return response.data;
  },

  deleteTask: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/v1/activities/api/tasks/${id}/`);
  },

  completeTask: async (id: number, data: { completion_notes?: string }): Promise<Task> => {
    const response = await apiClient.post(`/api/v1/activities/api/tasks/${id}/complete/`, data);
    return response.data.task;
  },

  getMyTasks: async (params?: Record<string, any>): Promise<Task[]> => {
    const response = await apiClient.get('/api/v1/activities/api/tasks/my_tasks/', { params });
    return response.data;
  },

  getTasksDueToday: async (): Promise<Task[]> => {
    const response = await apiClient.get('/api/v1/activities/api/tasks/due_today/');
    return response.data;
  },

  getOverdueTasks: async (): Promise<{ count: number; tasks: Task[] }> => {
    const response = await apiClient.get('/api/v1/activities/api/tasks/overdue/');
    return response.data;
  },

  // INTERACTION LOGS
  getInteractionLogs: async (params?: Record<string, any>): Promise<{ results: InteractionLog[]; count: number }> => {
    const response = await apiClient.get('/api/v1/activities/api/interactions/', { params });
    return response.data;
  },

  getInteractionLog: async (id: number): Promise<InteractionLog> => {
    const response = await apiClient.get(`/api/v1/activities/api/interactions/${id}/`);
    return response.data;
  },

  createInteractionLog: async (data: InteractionLogFormData): Promise<InteractionLog> => {
    const response = await apiClient.post('/api/v1/activities/api/interactions/', data);
    return response.data;
  },

  updateInteractionLog: async (id: number, data: Partial<InteractionLogFormData>): Promise<InteractionLog> => {
    const response = await apiClient.patch(`/api/v1/activities/api/interactions/${id}/`, data);
    return response.data;
  },

  deleteInteractionLog: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/v1/activities/api/interactions/${id}/`);
  },

  // FOLLOW-UP RULES
  getFollowUpRules: async (): Promise<FollowUpRule[]> => {
    const response = await apiClient.get('/api/v1/activities/api/follow-up-rules/');
    return response.data.results || response.data;
  },

  createFollowUpRule: async (data: Partial<FollowUpRule>): Promise<FollowUpRule> => {
    const response = await apiClient.post('/api/v1/activities/api/follow-up-rules/', data);
    return response.data;
  },

  updateFollowUpRule: async (id: number, data: Partial<FollowUpRule>): Promise<FollowUpRule> => {
    const response = await apiClient.patch(`/api/v1/activities/api/follow-up-rules/${id}/`, data);
    return response.data;
  },

  deleteFollowUpRule: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/v1/activities/api/follow-up-rules/${id}/`);
  },

  // DASHBOARD STATS
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await apiClient.get('/api/v1/activities/api/dashboard/stats/');
    return response.data;
  },

  // CONTACT-SPECIFIC ACTIVITIES
  getContactActivities: async (contactId: number): Promise<Activity[]> => {
    const response = await apiClient.get(`/api/v1/activities/api/contacts/${contactId}/activities/`);
    return response.data;
  },

  getContactInteractions: async (contactId: number): Promise<InteractionLog[]> => {
    const response = await apiClient.get(`/api/v1/activities/api/contacts/${contactId}/interactions/`);
    return response.data;
  },

  // OPPORTUNITY-SPECIFIC ACTIVITIES
  getOpportunityActivities: async (opportunityId: number): Promise<Activity[]> => {
    const response = await apiClient.get(`/api/v1/activities/api/opportunities/${opportunityId}/activities/`);
    return response.data;
  },

  getOpportunityInteractions: async (opportunityId: number): Promise<InteractionLog[]> => {
    const response = await apiClient.get(`/api/v1/activities/api/opportunities/${opportunityId}/interactions/`);
    return response.data;
  },
};