// frontend/src/api/pipeline.ts (Updated with clean URLs)
import { apiClient } from './client';

export interface OpportunityFormData {
  name: string;
  description: string;
  value: number;
  probability: number;
  stage_id: number;
  contact_id: number;
  company_id?: number;
  owner_id: number;
  expected_close_date: string;
  priority: 'low' | 'medium' | 'high';
}

export interface SalesStage {
  id: number;
  name: string;
  description: string;
  order: number;
  probability: number;
  is_closed_won: boolean;
  is_closed_lost: boolean;
  is_active: boolean;
  color: string;
  created_at: string;
  updated_at: string;
}

export interface Opportunity {
  id: number;
  name: string;
  description: string;
  value: number;
  probability: number;
  stage: SalesStage;
  contact: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    phone: string;
  };
  company: {
    id: number;
    name: string;
  } | null;
  owner: {
    id: number;
    first_name: string;
    last_name: string;
  };
  expected_close_date: string;
  actual_close_date: string | null;
  priority: 'low' | 'medium' | 'high';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PipelineData {
  stage: SalesStage;
  opportunities: Opportunity[];
  summary: {
    count: number;
    total_value: number;
    weighted_value: number;
  };
}

export interface PipelineResponse {
  pipeline: PipelineData[];
  total_opportunities: number;
  total_pipeline_value: number;
  total_weighted_value: number;
}

export interface AnalyticsData {
  total_opportunities: number;
  total_value: number;
  total_weighted_value: number;
  average_deal_size: number;
  conversion_rate: number;
  average_sales_cycle: number;
  stages: Array<{
    stage_name: string;
    stage_id: number;
    count: number;
    total_value: number;
    average_value: number;
    probability: number;
  }>;
  monthly_performance: Array<{
    month: string;
    month_name: string;
    opportunities_created: number;
    opportunities_won: number;
    total_value: number;
    won_value: number;
  }>;
}

export const pipelineApi = {
  // Get pipeline with opportunities grouped by stage
  getPipeline: async (): Promise<PipelineResponse> => {
    const response = await apiClient.get('/api/v1/opportunities/opportunities/pipeline/');
    return response.data;
  },

  // Get all sales stages
  getStages: async (): Promise<SalesStage[]> => {
    const response = await apiClient.get('/api/v1/opportunities/stages/');
    return response.data.results || response.data;
  },

  // Create new sales stage
  createStage: async (stageData: Partial<SalesStage>): Promise<SalesStage> => {
    const response = await apiClient.post('/api/v1/opportunities/stages/', stageData);
    return response.data;
  },

  // Update sales stage
  updateStage: async (stageId: number, stageData: Partial<SalesStage>): Promise<SalesStage> => {
    const response = await apiClient.put(`/api/v1/opportunities/stages/${stageId}/`, stageData);
    return response.data;
  },

  // Delete sales stage
  deleteStage: async (stageId: number): Promise<void> => {
    await apiClient.delete(`/api/v1/opportunities/stages/${stageId}/`);
  },

  // Create default stages for new tenant
  createDefaultStages: async (): Promise<SalesStage[]> => {
    const response = await apiClient.post('/api/v1/opportunities/stages/create_default_stages/');
    return response.data;
  },

  // Get all opportunities
  getOpportunities: async (params?: Record<string, any>): Promise<{ results: Opportunity[]; count: number }> => {
    const response = await apiClient.get('/api/v1/opportunities/opportunities/', { params });
    return response.data;
  },

  // Get single opportunity
  getOpportunity: async (opportunityId: number): Promise<Opportunity> => {
    const response = await apiClient.get(`/api/v1/opportunities/opportunities/${opportunityId}/`);
    return response.data;
  },

  // Create new opportunity
  createOpportunity: async (opportunityData: OpportunityFormData): Promise<Opportunity> => {
    const response = await apiClient.post('/api/v1/opportunities/opportunities/', opportunityData);
    return response.data;
  },

  // Update opportunity
  updateOpportunity: async (opportunityId: number, opportunityData: Partial<OpportunityFormData>): Promise<Opportunity> => {
    const response = await apiClient.put(`/api/v1/opportunities/opportunities/${opportunityId}/`, opportunityData);
    return response.data;
  },

  // Delete opportunity
  deleteOpportunity: async (opportunityId: number): Promise<void> => {
    await apiClient.delete(`/api/v1/opportunities/opportunities/${opportunityId}/`);
  },

  // Change opportunity stage
  changeOpportunityStage: async (opportunityId: number, stageId: number, notes?: string): Promise<{ message: string; opportunity: Opportunity }> => {
    const response = await apiClient.post(`/api/v1/opportunities/opportunities/${opportunityId}/change_stage/`, {
      stage_id: stageId,
      notes: notes || ''
    });
    return response.data;
  },

  // Get opportunity history
  getOpportunityHistory: async (opportunityId: number): Promise<any[]> => {
    const response = await apiClient.get(`/api/v1/opportunities/opportunities/${opportunityId}/history/`);
    return response.data;
  },

  // Get pipeline analytics
  getAnalytics: async (): Promise<AnalyticsData> => {
    const response = await apiClient.get('/api/v1/opportunities/opportunities/analytics/');
    return response.data;
  },

  // Get user's opportunities
  getMyOpportunities: async (params?: Record<string, any>): Promise<Opportunity[]> => {
    const response = await apiClient.get('/api/v1/opportunities/opportunities/my_opportunities/', { params });
    return response.data;
  },

  // Get overdue opportunities
  getOverdueOpportunities: async (): Promise<{ count: number; opportunities: Opportunity[] }> => {
    const response = await apiClient.get('/api/v1/opportunities/opportunities/overdue/');
    return response.data;
  },

  // Get opportunities closing soon
  getClosingSoonOpportunities: async (): Promise<{ count: number; opportunities: Opportunity[] }> => {
    const response = await apiClient.get('/api/v1/opportunities/opportunities/closing_soon/');
    return response.data;
  },

  // Bulk operations
  bulkUpdateStage: async (opportunityIds: number[], stageId: number): Promise<void> => {
    await apiClient.post('/api/v1/opportunities/opportunities/bulk_update_stage/', {
      opportunity_ids: opportunityIds,
      stage_id: stageId
    });
  },

  bulkUpdatePriority: async (opportunityIds: number[], priority: 'low' | 'medium' | 'high'): Promise<void> => {
    await apiClient.post('/api/v1/opportunities/opportunities/bulk_update_priority/', {
      opportunity_ids: opportunityIds,
      priority
    });
  },

  bulkDelete: async (opportunityIds: number[]): Promise<void> => {
    await apiClient.post('/api/v1/opportunities/opportunities/bulk_delete/', {
      opportunity_ids: opportunityIds
    });
  }
};