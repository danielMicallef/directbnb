import { apiClient } from '../api-client';
import type {
  ColorSchemeChoices,
  ThemeChoices,
  Website,
  WebsiteCreateUpdateRequest,
  PaginatedResponse,
  LeadRegistrationData,
  LeadRegistrationResponse,
  PricingData,
  RegistrationOption,
  LeadRegistrationUpdateRequest,
} from '@/types/api';

export const builderApi = {
  // Color Schemes
  async getColorSchemes(page?: number): Promise<PaginatedResponse<ColorSchemeChoices>> {
    const endpoint = page ? `/builder/color-schemes/?page=${page}` : '/builder/color-schemes/';
    return apiClient.get<PaginatedResponse<ColorSchemeChoices>>(endpoint);
  },

  async getColorScheme(id: number): Promise<ColorSchemeChoices> {
    return apiClient.get<ColorSchemeChoices>(`/builder/color-schemes/${id}/`);
  },

  async createColorScheme(data: Omit<ColorSchemeChoices, 'id' | 'created_at' | 'updated_at'>): Promise<ColorSchemeChoices> {
    return apiClient.post<ColorSchemeChoices>('/builder/color-schemes/', data);
  },

  async updateColorScheme(id: number, data: Partial<Omit<ColorSchemeChoices, 'id' | 'created_at' | 'updated_at'>>): Promise<ColorSchemeChoices> {
    return apiClient.patch<ColorSchemeChoices>(`/builder/color-schemes/${id}/`, data);
  },

  async deleteColorScheme(id: number): Promise<void> {
    return apiClient.delete<void>(`/builder/color-schemes/${id}/`);
  },

  // Themes
  async getThemes(page?: number): Promise<PaginatedResponse<ThemeChoices>> {
    const endpoint = page ? `/builder/themes/?page=${page}` : '/builder/themes/';
    return apiClient.get<PaginatedResponse<ThemeChoices>>(endpoint);
  },

  async getTheme(id: number): Promise<ThemeChoices> {
    return apiClient.get<ThemeChoices>(`/builder/themes/${id}/`);
  },

  async createTheme(data: Omit<ThemeChoices, 'id' | 'created_at' | 'updated_at' | 'preview_link'>): Promise<ThemeChoices> {
    return apiClient.post<ThemeChoices>('/builder/themes/', data);
  },

  async updateTheme(id: number, data: Partial<Omit<ThemeChoices, 'id' | 'created_at' | 'updated_at' | 'preview_link'>>): Promise<ThemeChoices> {
    return apiClient.patch<ThemeChoices>(`/builder/themes/${id}/`, data);
  },

  async deleteTheme(id: number): Promise<void> {
    return apiClient.delete<void>(`/builder/themes/${id}/`);
  },

  // Websites
  async getWebsites(page?: number): Promise<PaginatedResponse<Website>> {
    const endpoint = page ? `/builder/websites/?page=${page}` : '/builder/websites/';
    return apiClient.get<PaginatedResponse<Website>>(endpoint);
  },

  async getWebsite(id: number): Promise<Website> {
    return apiClient.get<Website>(`/builder/websites/${id}/`);
  },

  async createWebsite(data: WebsiteCreateUpdateRequest): Promise<Website> {
    return apiClient.post<Website>('/builder/websites/', data);
  },

  async updateWebsite(id: number, data: Partial<WebsiteCreateUpdateRequest>): Promise<Website> {
    return apiClient.patch<Website>(`/builder/websites/${id}/`, data);
  },

  async deleteWebsite(id: number): Promise<void> {
    return apiClient.delete<void>(`/builder/websites/${id}/`);
  },

  async getWebsiteConfiguration(id: number): Promise<Website> {
    return apiClient.get<Website>(`/builder/websites/${id}/configuration/`);
  },

  async scrapeAirbnb(id: number, url: string): Promise<Website> {
    return apiClient.post<Website>(`/builder/websites/${id}/scrape_airbnb/`, { url });
  },

  async scrapeBooking(id: number, url: string): Promise<Website> {
    return apiClient.post<Website>(`/builder/websites/${id}/scrape_booking/`, { url });
  },

  // Lead Registrations
  async createLeadRegistration(data: LeadRegistrationData): Promise<LeadRegistrationResponse> {
    return apiClient.post<LeadRegistrationResponse>('/builder/lead-registrations/', data);
  },

  async getLeadRegistrations(email: string): Promise<PaginatedResponse<LeadRegistrationResponse>> {
    return apiClient.get<PaginatedResponse<LeadRegistrationResponse>>(`/builder/lead-registrations/?email=${encodeURIComponent(email)}`);
  },

  // Packages
  async getPackages(): Promise<PricingData> {
    return apiClient.get<PricingData>('/builder/packages/');
  },

  // Registration Options
  async createRegistrationOption(data: RegistrationOption): Promise<RegistrationOption> {
    return apiClient.post<RegistrationOption>('/builder/registration-options/', data);
  },

  // Lead Registration Update
  async updateLeadRegistration(id: number, data: LeadRegistrationUpdateRequest): Promise<LeadRegistrationResponse> {
    return apiClient.patch<LeadRegistrationResponse>(`/builder/lead-registrations/${id}/`, data);
  },
};
