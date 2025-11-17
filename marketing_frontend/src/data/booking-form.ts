export type HostingPlan = "self" | "1year" | "3years" | "";
export type PackagePlan = "builder" | "custom" | "";

export interface FormData {
  package: PackagePlan;
  theme: string;
  colorScheme: string;
  bookingLinks: string[];
  notListed: boolean;
  domainName: string;
  skipDomain: boolean;
  hostingPlan: HostingPlan;
  liveReviews: boolean;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  microInvest: boolean;
  // Honeypot field
  confirm_email: string;
}

export const initialFormData: FormData = {
  package: "builder",
  theme: "",
  colorScheme: "",
  bookingLinks: [""],
  notListed: false,
  domainName: "",
  skipDomain: false,
  hostingPlan: "1year",
  liveReviews: false,
  firstName: "",
  lastName: "",
  email: "",
  phone: "",
  microInvest: false,
    // Honeypot field
  confirm_email: "",
};
