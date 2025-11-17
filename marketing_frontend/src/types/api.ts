// API Response Types based on OpenAPI schema

// Auth Types
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string | null;
  avatar: string | null;
  is_email_confirmed: boolean;
  registered_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface RegisterRequest {
  email: string;
  password: string;
  password2: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
}

export interface RegisterResponse {
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string | null;
}

export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
  new_password2: string;
}

export interface TokenRefreshRequest {
  refresh: string;
}

export interface TokenRefreshResponse {
  access: string;
  refresh: string;
}

export interface ResendVerificationRequest {
  email: string;
}

// Website Builder Types
export interface ThemeColor {
  name: string;
  value: string;
}

export interface ColorSchemeChoices {
  id: number;
  name: string;
  theme_colors: ThemeColor[];
  created_at: string;
  updated_at: string;
}

export interface ThemeChoices {
  id: number;
  name: string;
  icon_name: string | null;
  preview_link: string | null;
  created_at: string;
  updated_at: string;
}

export interface WebsiteCreateUpdateRequest {
  theme: number;
  color_scheme: number;
  airbnb_listing_url?: string;
  booking_listing_url?: string;
  domain_name?: string;
}

export interface Website {
  id: number;
  theme: number;
  theme_detail: ThemeChoices;
  color_scheme: number;
  color_scheme_detail: ColorSchemeChoices;
  airbnb_listing_url: string | null;
  booking_listing_url: string | null;
  domain_name: string | null;
  created_at: string;
  updated_at: string;
}

// Pagination wrapper
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// API Error Response
export interface ApiError {
  detail?: string;
  [key: string]: unknown;
}

export interface LeadRegistrationData {
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  theme: string;
  color_scheme: string;
  listing_urls: string[];
  domain_name: string;
  // Honeypot field
  confirm_email: string;
}

export interface LeadRegistrationResponse {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  theme: string;
  color_scheme: string;
  listing_urls: string[];
  domain_name: string;
  checkout_url?: string;
}

export interface Promotion {
  id: number;
  discount_percentage: number;
  units_available: number;
  start_date: string;
  end_date: string;
  promotion_code: string;
}

export interface PricingPackage {
  id: number;
  name: string;
  currency: string;
  amount: string;
  monthly_price: number;
  description: string;
  frequency: number;
  frequency_display: string;
  label: string;
  label_display: string;
  extra_info: Record<string, unknown>;
  promotions: Promotion[];
  discounted_price: number;
  created_at: string;
  updated_at: string;
}

export interface PricingData {
  "Add-on": PricingPackage[];
  Builder: PricingPackage[];
  Hosting: PricingPackage[];
}

export interface RegistrationOption {
  lead_registration: number;
  promotion?: number;
  package: number;
}

export interface LeadRegistrationUpdateRequest {
  extra_requirements?: string;
  completed_at?: string;
}
