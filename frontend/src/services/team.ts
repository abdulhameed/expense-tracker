import apiClient from './api';
import {
  Project,
  ProjectMember,
  Invitation,
  CreateProjectMemberRequest,
  UpdateProjectMemberRequest,
  ProjectListResponse,
} from '@/types/api';

/**
 * Team Collaboration API Service
 */
export const teamService = {
  /**
   * Get list of projects for current user
   */
  async getProjects(filters?: {
    project_type?: string;
    is_active?: boolean;
    search?: string;
    page?: number;
    page_size?: number;
  }): Promise<ProjectListResponse> {
    const params = new URLSearchParams();

    if (filters) {
      if (filters.project_type) params.append('project_type', filters.project_type);
      if (filters.is_active !== undefined) params.append('is_active', String(filters.is_active));
      if (filters.search) params.append('search', filters.search);
      if (filters.page) params.append('page', String(filters.page));
      if (filters.page_size) params.append('page_size', String(filters.page_size));
    }

    const response = await apiClient.get<ProjectListResponse>(
      `/projects/?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Get a single project by ID
   */
  async getProject(projectId: string): Promise<Project> {
    const response = await apiClient.get<Project>(`/projects/${projectId}/`);
    return response.data;
  },

  /**
   * Create a new project
   */
  async createProject(data: {
    name: string;
    description?: string;
    project_type: 'personal' | 'business' | 'team';
    currency?: string;
    budget?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<Project> {
    const response = await apiClient.post<Project>('/projects/', data);
    return response.data;
  },

  /**
   * Update a project
   */
  async updateProject(
    projectId: string,
    data: Partial<{
      name: string;
      description: string;
      budget: number;
      start_date: string;
      end_date: string;
      is_active: boolean;
    }>
  ): Promise<Project> {
    const response = await apiClient.patch<Project>(`/projects/${projectId}/`, data);
    return response.data;
  },

  /**
   * Delete a project
   */
  async deleteProject(projectId: string): Promise<void> {
    await apiClient.delete(`/projects/${projectId}/`);
  },

  /**
   * Archive a project
   */
  async archiveProject(projectId: string): Promise<Project> {
    const response = await apiClient.post<Project>(`/projects/${projectId}/archive/`, {});
    return response.data;
  },

  /**
   * Get project statistics
   */
  async getProjectStats(
    projectId: string
  ): Promise<{ project_id: string; member_count: number; is_archived: boolean; is_active: boolean }> {
    const response = await apiClient.get<any>(`/projects/${projectId}/stats/`);
    return response.data;
  },

  /**
   * Get project members
   */
  async getProjectMembers(projectId: string): Promise<ProjectMember[]> {
    const response = await apiClient.get<ProjectMember[]>(`/projects/${projectId}/members/`);
    return response.data;
  },

  /**
   * Update a project member (change role, permissions)
   */
  async updateProjectMember(
    projectId: string,
    memberId: string,
    data: UpdateProjectMemberRequest
  ): Promise<ProjectMember> {
    const response = await apiClient.patch<ProjectMember>(
      `/projects/${projectId}/members/${memberId}/`,
      data
    );
    return response.data;
  },

  /**
   * Remove a member from a project
   */
  async removeProjectMember(projectId: string, memberId: string): Promise<void> {
    await apiClient.delete(`/projects/${projectId}/members/${memberId}/`);
  },

  /**
   * Leave a project
   */
  async leaveProject(projectId: string): Promise<{ detail: string }> {
    const response = await apiClient.post<{ detail: string }>(
      `/projects/${projectId}/leave/`,
      {}
    );
    return response.data;
  },

  /**
   * Invite a member to a project
   */
  async inviteMember(
    projectId: string,
    data: CreateProjectMemberRequest
  ): Promise<Invitation> {
    const response = await apiClient.post<Invitation>(
      `/projects/${projectId}/invite-member/`,
      data
    );
    return response.data;
  },

  /**
   * Get pending invitations for current user
   */
  async getPendingInvitations(): Promise<Invitation[]> {
    const response = await apiClient.get<Invitation[]>('/invitations/');
    return response.data;
  },

  /**
   * Accept an invitation
   */
  async acceptInvitation(token: string): Promise<{ detail: string }> {
    const response = await apiClient.post<{ detail: string }>(
      `/invitations/${token}/accept/`,
      {}
    );
    return response.data;
  },

  /**
   * Decline an invitation
   */
  async declineInvitation(token: string): Promise<{ detail: string }> {
    const response = await apiClient.post<{ detail: string }>(
      `/invitations/${token}/decline/`,
      {}
    );
    return response.data;
  },
};
