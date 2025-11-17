import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Building2, ChevronLeft, ChevronRight, ExternalLink, Info, PlusCircle, Trash2 } from "lucide-react";
import { Icon } from "@/components/Icon";
import { FormData } from "@/data/booking-form";
import { getCurrencySymbol } from "@/data/currencies";
import { useLocalStorage } from "@/hooks/useLocalStorage";
import { builderApi } from "@/lib/api";
import type { ColorSchemeChoices, ThemeChoices, LeadRegistrationData, PricingData, PricingPackage } from "@/types/api";

interface BookingFormWizardProps {
  formData: FormData;
  setFormData: React.Dispatch<React.SetStateAction<FormData>>;
  stepNumber: number;
  setStepNumber: React.Dispatch<React.SetStateAction<number>>;
}

export function BookingFormWizard({ formData, setFormData, stepNumber, setStepNumber }: BookingFormWizardProps) {
  const [validationError, setValidationError] = useState<string | null>(null);
  const [colorSchemes, setColorSchemes] = useState<ColorSchemeChoices[]>([]);
  const [themes, setThemes] = useState<ThemeChoices[]>([]);
  const [pricingData, setPricingData] = useState<PricingData | null>(null);
  const [leadRegistrationId, setLeadRegistrationId] = useLocalStorage<number | null>('leadRegistrationId', null, 90);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | string[] | null>(null);
  const totalSteps = 7;

  const updateFormData = (field: keyof FormData, value: string | boolean | string[]) => {
    setFormData((prev) => {
      const newState = { ...prev, [field]: value };
      if (field === 'skipDomain' && value) {
        newState.domainName = "";
      }
      if (field === 'bookingLinks') {
        setValidationError(null);
      }
      return newState;
    });
  };

  const handleBookingLinkChange = (index: number, value: string) => {
    const newBookingLinks = [...formData.bookingLinks];
    newBookingLinks[index] = value;
    updateFormData('bookingLinks', newBookingLinks);
  };

  const addBookingLink = () => {
    updateFormData('bookingLinks', [...formData.bookingLinks, ""]);
  };

  const removeBookingLink = (index: number) => {
    const newBookingLinks = formData.bookingLinks.filter((_, i) => i !== index);
    updateFormData('bookingLinks', newBookingLinks);
  };

  const validateBookingLinks = () => {
    if (formData.notListed) return true;

    for (const url of formData.bookingLinks) {
      if (!url.trim()) {
        setValidationError("Please enter a URL or select that your apartment is not listed.");
        return false;
      }
      
      let fullUrl = url.trim();
      if (!/^https?:\/\//i.test(fullUrl)) {
        fullUrl = `https://${fullUrl}`;
      }

      try {
        const { hostname } = new URL(fullUrl);
        // Updated regex to be more robust for different TLDs (e.g., .com, .co.uk)
        const validHostnameRegex = /(^|\.)(airbnb|booking)\.[a-z]+(\.[a-z]{2,3})?$/i;
        if (!validHostnameRegex.test(hostname)) {
          setValidationError("Please enter a valid Airbnb or Booking.com URL.");
          return false;
        }
      } catch (error) {
        setValidationError("Please enter a valid URL.");
        return false;
      }
    }
    setValidationError(null);
    return true;
  };

  const canSkip = () => {
    switch (stepNumber) {
      case 4:
        return true;
      default:
        return false;
    }
  }

  const canProceed = () => {
    switch (stepNumber) {
      case 1:
        return formData.theme !== "";
      case 2:
        return formData.colorScheme !== "";
      case 3:
        return formData.notListed || (formData.bookingLinks.length > 0 && formData.bookingLinks.every(link => link.trim() !== ""));
      case 4:
        return true;
      case 5:
        return (
          formData.firstName.trim() !== "" &&
          formData.lastName.trim() !== "" &&
          formData.email.trim() !== "" &&
          formData.phone.trim() !== ""
        );
      case 6:
        return (
          formData.hostingPlan.trim() !== "" &&
          formData.package.trim() !== ""
        );
      case 7:
        return true;
      default:
        return false;
    }
  };

  const getPackageById = (id: string): PricingPackage | undefined => {
    if (!pricingData) return undefined;
    const allPackages = [...pricingData.Builder, ...pricingData.Hosting, ...pricingData["Add-on"]];
    return allPackages.find(p => String(p.id) === id);
  };

  const calculatePrice = () => {
    if (!pricingData) return 0;

    const selectedPackage = pricingData.Builder.find(p => String(p.id) === formData.package);
    const selectedHosting = pricingData.Hosting.find(p => String(p.id) === formData.hostingPlan);
    const liveReviewsPackage = pricingData["Add-on"].find(p => p.name.toLowerCase().includes('live reviews'));

    const packagePrice = selectedPackage ? selectedPackage.discounted_price : 0;
    const hostingPrice = selectedHosting ? selectedHosting.discounted_price : 0;
    const reviewsPrice = formData.liveReviews && liveReviewsPackage ? liveReviewsPackage.discounted_price : 0;

    return packagePrice + hostingPrice + reviewsPrice;
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);

    try {
      let currentLeadId = leadRegistrationId;
      let currentPricingData = pricingData;

      // Fallback for pricingData
      if (!currentPricingData) {
        const fetchedPricingData = await builderApi.getPackages();
        setPricingData(fetchedPricingData);
        currentPricingData = fetchedPricingData;
      }

      // Fallback for leadRegistrationId
      if (!currentLeadId && formData.email) {
        const response = await builderApi.getLeadRegistrations(formData.email);
        if (response.results.length > 0) {
          const foundLeadId = response.results[0].id;
          setLeadRegistrationId(foundLeadId);
          currentLeadId = foundLeadId;
        } else {
          throw new Error("Could not find your registration. Please go back and complete step 5.");
        }
      }

      if (!currentLeadId || !currentPricingData) {
        throw new Error("Missing required data to complete the submission.");
      }

      // 1. Builder package chosen
      const selectedPackage = getPackageById(formData.package);
      if (selectedPackage) {
        await builderApi.createRegistrationOption({
          lead_registration: currentLeadId,
          package: selectedPackage.id,
          promotion: selectedPackage.promotions.length > 0 ? selectedPackage.promotions[0].id : undefined,
        });
      }

      // 2. Hosting Option chosen
      const selectedHosting = getPackageById(formData.hostingPlan);
      if (selectedHosting) {
        await builderApi.createRegistrationOption({
          lead_registration: currentLeadId,
          package: selectedHosting.id,
        });
      }

      // 3. A record for each Add-on chosen
      if (formData.liveReviews) {
        const liveReviewsPackage = currentPricingData["Add-on"].find(p => p.name.toLowerCase().includes('live reviews'));
        if (liveReviewsPackage) {
          await builderApi.createRegistrationOption({
            lead_registration: currentLeadId,
            package: liveReviewsPackage.id,
          });
        }
      }

      // 4. Update lead registration if microInvest is selected
      if (formData.microInvest) {
        await builderApi.updateLeadRegistration(currentLeadId, {
          extra_requirements: JSON.stringify({ microInvest: true }),
        });
      }

      const response = await builderApi.updateLeadRegistration(currentLeadId, {
        completed_at: new Date().toISOString(),
      });

      if (response.checkout_url) {
        window.location.href = response.checkout_url;
      } else {
        // TODO: Integrate with Stripe
        console.log("Form submitted:", formData);
        alert("Form submitted! Redirecting to payment...");
      }

    } catch (err: any) {
      if (err.response && err.response.data) {
        const errorData = err.response.data;
        const errorMessages = Object.keys(errorData).map(key => `${key}: ${errorData[key].join(', ')}`);
        setError(errorMessages);
      } else {
        setError(err.message || 'Failed to submit form');
      }
      console.error('Error submitting form:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLeadRegistration = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const leadData: LeadRegistrationData = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        phone_number: formData.phone,
        theme: formData.theme,
        color_scheme: formData.colorScheme,
        listing_urls: formData.notListed ? [] : formData.bookingLinks,
        domain_name: formData.domainName,
        confirm_email: formData.confirm_email,
      };
      const response = await builderApi.createLeadRegistration(leadData);
      setLeadRegistrationId(response.id);
      setStepNumber((prev) => prev + 1);
    } catch (err: any) {
      if (err.response && err.response.data) {
        const errorData = err.response.data;
        const errorMessages = Object.keys(errorData).map(key => `${key}: ${errorData[key].join(', ')}`);
        setError(errorMessages);
      } else {
        setError(err.message || 'Failed to register lead');
      }
      console.error('Error creating lead registration:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const validateStep = () => {
    switch (stepNumber) {
      case 3:
        return validateBookingLinks();
      default:
        return true;
    }
  }

  // Fetch color schemes and themes from API
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [colorSchemesResponse, themesResponse, pricingResponse] = await Promise.all([
          builderApi.getColorSchemes(),
          builderApi.getThemes(),
          builderApi.getPackages(),
        ]);
        setColorSchemes(colorSchemesResponse.results);
        setThemes(themesResponse.results);
        setPricingData(pricingResponse);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
        console.error('Error fetching data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    console.log("Form data changed:", formData);
  }, [formData]);

  const renderNextButton = useCallback(() => {
    const proceed = canProceed();
    const skip = canSkip();

    if (!proceed && skip) {
      return (
        <Button onClick={() => setStepNumber((prev) => prev + 1)}>
          Skip
          <ChevronRight className="w-4 h-4 ml-2" />
        </Button>
      );
    }

    return (
      <Button
        onClick={() => {
          if (validateStep()) {
            if (stepNumber === 5) {
              handleLeadRegistration();
            } else {
              setStepNumber((prev) => prev + 1);
            }
          }
        }}
        disabled={!proceed || isLoading}
      >
        {isLoading && stepNumber === 5 ? "Saving..." : "Next"}
        <ChevronRight className="w-4 h-4 ml-2" />
      </Button>
    );
  }, [formData, stepNumber]);

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Create Your Direct Booking Website</CardTitle>
        <CardDescription>
          Step {stepNumber} of {totalSteps}
        </CardDescription>
        <div className="w-full bg-muted rounded-full h-2 mt-4">
          <div
            className="bg-primary h-2 rounded-full transition-all duration-300"
            style={{ width: `${(stepNumber / totalSteps) * 100}%` }}
          />
        </div>
        {error && (
          <Alert variant="destructive" className="mt-4">
            <AlertDescription>
              {Array.isArray(error) ? (
                <ul className="list-disc pl-5">
                  {error.map((msg, i) => <li key={i}>{msg}</li>)}
                </ul>
              ) : (
                error
              )}
            </AlertDescription>
          </Alert>
        )}
      </CardHeader>
      <CardContent className="space-y-6">
        {stepNumber === 1 && (
          <div className="space-y-4">
            <Label className="text-lg font-semibold">Choose Your Theme</Label>
            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">Loading themes...</div>
            ) : error ? (
              <div className="text-center py-8 text-red-500">
                <p>Error loading themes: {error}</p>
                <p className="text-sm mt-2">Using fallback options</p>
              </div>
            ) : null}
            <RadioGroup
              value={formData.theme}
              onValueChange={(value) => updateFormData("theme", value)}
              className="grid grid-cols-1 md:grid-cols-3 gap-4"
            >
              {themes.length > 0 ? (
                themes.map((theme) => (
                  <Label
                    key={theme.id}
                    htmlFor={`theme-${theme.id}`}
                    className={`flex flex-col items-center justify-center p-6 border-2 rounded-lg cursor-pointer transition-all ${
                      formData.theme === String(theme.id) ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                    }`}
                  >
                    <RadioGroupItem value={String(theme.id)} id={`theme-${theme.id}`} className="sr-only" />
                    <Icon name={theme.icon_name} className="w-12 h-12 mb-3 text-primary" fallback={<Building2 className="w-12 h-12 mb-3 text-primary" />} />
                    <span className="font-semibold">{theme.name}</span>
                  </Label>
                ))
              ) : (
                // Fallback to hardcoded themes if API fails
                <>
                  <Label
                    htmlFor="city"
                    className={`flex flex-col items-center justify-center p-6 border-2 rounded-lg cursor-pointer transition-all ${
                      formData.theme === "city" ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                    }`}
                  >
                    <RadioGroupItem value="city" id="city" className="sr-only" />
                    <Building2 className="w-12 h-12 mb-3 text-primary" />
                    <span className="font-semibold">City</span>
                  </Label>

                  <Label
                    htmlFor="mountain"
                    className={`flex flex-col items-center justify-center p-6 border-2 rounded-lg cursor-pointer transition-all ${
                      formData.theme === "mountain" ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                    }`}
                  >
                    <RadioGroupItem value="mountain" id="mountain" className="sr-only" />
                    <Icon name="Mountain" className="w-12 h-12 mb-3 text-primary" />
                    <span className="font-semibold">Mountain</span>
                  </Label>

                  <Label
                    htmlFor="seaside"
                    className={`flex flex-col items-center justify-center p-6 border-2 rounded-lg cursor-pointer transition-all ${
                      formData.theme === "seaside" ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                    }`}
                  >
                    <RadioGroupItem value="seaside" id="seaside" className="sr-only" />
                    <Icon name="Waves" className="w-12 h-12 mb-3 text-primary" />
                    <span className="font-semibold">Seaside</span>
                  </Label>
                </>
              )}
            </RadioGroup>
          </div>
        )}

        {stepNumber === 2 && (
          <div className="space-y-4">
            <Label className="text-lg font-semibold">Select your Colour Preset</Label>
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                This is not final and you can always update your selection later.
              </AlertDescription>
            </Alert>
            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">Loading color schemes...</div>
            ) : error ? (
              <div className="text-center py-8 text-red-500">
                <p>Error loading color schemes: {error}</p>
                <p className="text-sm mt-2">Using fallback options</p>
              </div>
            ) : null}
            <RadioGroup
              value={formData.colorScheme}
              onValueChange={(value) => updateFormData("colorScheme", value)}
              className="grid grid-cols-1 md:grid-cols-3 gap-4"
            >
              {colorSchemes.length > 0 ? (
                colorSchemes.map((scheme) => {
                  const requiredColors = ['base', 'primary', 'secondary', 'accent', 'neutral'];
                  const paletteColors = requiredColors.map(name => {
                    const color = scheme.theme_colors.find(c => c.name === name);
                    return { name, value: color ? color.value : '#FFFFFF' };
                  });

                  return (
                    <Label
                      key={scheme.id}
                      htmlFor={`color-${scheme.id}`}
                      className={`flex flex-col items-center justify-center p-6 border-2 rounded-lg cursor-pointer transition-all ${
                        formData.colorScheme === String(scheme.id) ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                      }`}
                    >
                      <RadioGroupItem value={String(scheme.id)} id={`color-${scheme.id}`} className="sr-only" />
                      <div className="flex w-full h-8 rounded-md overflow-hidden mb-4 border">
                        {paletteColors.map(color => (
                          <div
                            key={color.name}
                            className="flex-1 h-full"
                            style={{ backgroundColor: color.value }}
                            title={color.name}
                          />
                        ))}
                      </div>
                      <span className="font-semibold">{scheme.name}</span>
                    </Label>
                  );
                })
              ) : (
                // Fallback to hardcoded color schemes if API fails
                <>
                  <Label
                    htmlFor="blue"
                    className={`flex flex-col items-center justify-center p-6 border-2 rounded-lg cursor-pointer transition-all ${
                      formData.colorScheme === "blue" ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                    }`}
                  >
                    <RadioGroupItem value="blue" id="blue" className="sr-only" />
                    <div className="w-16 h-16 rounded-full bg-blue-500 mb-3" />
                    <span className="font-semibold">Ocean Blue</span>
                  </Label>

                  <Label
                    htmlFor="green"
                    className={`flex flex-col items-center justify-center p-6 border-2 rounded-lg cursor-pointer transition-all ${
                      formData.colorScheme === "green" ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                    }`}
                  >
                    <RadioGroupItem value="green" id="green" className="sr-only" />
                    <div className="w-16 h-16 rounded-full bg-green-600 mb-3" />
                    <span className="font-semibold">Nature Green</span>
                  </Label>

                  <Label
                    htmlFor="orange"
                    className={`flex flex-col items-center justify-center p-6 border-2 rounded-lg cursor-pointer transition-all ${
                      formData.colorScheme === "orange" ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                    }`}
                  >
                    <RadioGroupItem value="orange" id="orange" className="sr-only" />
                    <div className="w-16 h-16 rounded-full bg-orange-500 mb-3" />
                    <span className="font-semibold">Sunset Orange</span>
                  </Label>
                </>
              )}
            </RadioGroup>
          </div>
        )}

        {stepNumber === 3 && (
          <div className="space-y-4">
            <Label className="text-lg font-semibold">Your Current Booking Links</Label>
            <p className="text-sm text-muted-foreground">
              Paste your Airbnb or Booking.com listing URLs to automatically import your property details.
            </p>
            {!formData.notListed && formData.bookingLinks.map((link, index) => (
              <div key={index} className="flex items-center gap-2">
                <Input
                  type="url"
                  placeholder="https://www.airbnb.com/rooms/..."
                  value={link}
                  onChange={(e) => handleBookingLinkChange(index, e.target.value)}
                  className="w-full"
                />
                {formData.bookingLinks.length > 1 && (
                  <Button variant="ghost" size="icon" onClick={() => removeBookingLink(index)}>
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
            ))}
            {!formData.notListed && (
              <Button variant="outline" size="sm" onClick={addBookingLink} className="flex items-center gap-2">
                <PlusCircle className="w-4 h-4" />
                Add another link
              </Button>
            )}
            <div className="flex items-center space-x-2 pt-4">
              <Checkbox
                id="notListed"
                checked={formData.notListed}
                onCheckedChange={(checked) => updateFormData("notListed", checked as boolean)}
              />
              <label
                htmlFor="notListed"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                My apartment is not currently listed. I will add data manually.
              </label>
            </div>
            {validationError && <p className="text-red-500 text-sm mt-2">{validationError}</p>}
          </div>
        )}

        {stepNumber === 4 && (
          <div className="space-y-4">
            <Label htmlFor="domainName" className="text-lg font-semibold">
              Add Your Domain Name
            </Label>
            <p className="text-sm text-muted-foreground">
              Pick a memorable domain for your direct booking website. We can help you register it! (Optional)
            </p>
            <Input
              id="domainName"
              type="text"
              placeholder="myamazingvilla.com"
              value={formData.domainName}
              onChange={(e) => updateFormData("domainName", e.target.value)}
              className="w-full"
              disabled={formData.skipDomain}
            />
            <div className="flex items-center space-x-2 pt-4">
              <Checkbox
                id="skipDomain"
                checked={formData.skipDomain}
                onCheckedChange={(checked) => updateFormData("skipDomain", checked as boolean)}
              />
              <label
                htmlFor="skipDomain"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                I don't have a domain name right now.
              </label>
            </div>
          </div>
        )}

        {stepNumber === 5 && (
          <div className="space-y-4">
            <Label className="text-lg font-semibold">Your Contact Details</Label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="firstName">First Name</Label>
                <Input
                  id="firstName"
                  type="text"
                  placeholder="John"
                  value={formData.firstName}
                  onChange={(e) => updateFormData("firstName", e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="lastName">Last Name</Label>
                <Input
                  id="lastName"
                  type="text"
                  placeholder="Doe"
                  value={formData.lastName}
                  onChange={(e) => updateFormData("lastName", e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="john@example.com"
                value={formData.email}
                onChange={(e) => updateFormData("email", e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">Phone Number</Label>
              <Input
                id="phone"
                type="tel"
                placeholder="+1 (555) 000-0000"
                value={formData.phone}
                onChange={(e) => updateFormData("phone", e.target.value)}
              />
            </div>
            <div className="hidden">
              <Label htmlFor="confirm_email">Confirm Email</Label>
              <Input
                id="confirm_email"
                type="email"
                placeholder="Confirm Email"
                value={formData.confirm_email}
                onChange={(e) => updateFormData("confirm_email", e.target.value)}
              />
            </div>
          </div>
        )}

        {stepNumber === 6 && pricingData && (
          <div className="space-y-6">
            <div className="space-y-4">
              <Label className="text-lg font-semibold">Package</Label>
              <RadioGroup
                value={formData.package}
                onValueChange={(value) => updateFormData("package", value)}
                className="grid grid-cols-1 md:grid-cols-2 gap-4"
              >
                {pricingData.Builder.map((pkg) => (
                  <Label
                    key={pkg.id}
                    htmlFor={`pkg-${pkg.id}`}
                    className={`flex flex-col items-center justify-center p-6 border-2 rounded-lg cursor-pointer transition-all ${
                      formData.package === String(pkg.id) ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                    }`}
                  >
                    <RadioGroupItem value={String(pkg.id)} id={`pkg-${pkg.id}`} className="sr-only" />
                  <div className="text-2xl font-bold">
                    {pkg.promotions.length > 0 && (
                      <span className="text-lg text-muted-foreground line-through">{getCurrencySymbol(pkg.currency)}{pkg.amount}</span>
                    )}{" "}
                    <span className="text-primary">{getCurrencySymbol(pkg.currency)}{pkg.discounted_price}</span>
                  </div>
                    <p className="text-sm text-muted-foreground mt-2 text-center">{pkg.description}</p>
                    {pkg.promotions.length > 0 && (
                      <div className="text-sm text-muted-foreground mt-2">
                        <span className="text-accent font-semibold">{pkg.promotions[0].discount_percentage}% OFF</span> - for the first {pkg.promotions[0].units_available} spots only!
                      </div>
                    )}
                  </Label>
                ))}
              </RadioGroup>
            </div>
            
            <div className="space-y-4">
              <Label className="text-lg font-semibold">Hosting Plan</Label>
              <RadioGroup
                value={formData.hostingPlan}
                onValueChange={(value) => updateFormData("hostingPlan", value)}
                className="space-y-3"
              >
                {pricingData.Hosting.map((plan) => (
                  <Label
                    key={plan.id}
                    htmlFor={`plan-${plan.id}`}
                    className={`flex items-start justify-between p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      formData.hostingPlan === String(plan.id) ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <RadioGroupItem value={String(plan.id)} id={`plan-${plan.id}`} className="mt-1" />
                      <div>
                        <div className="font-semibold">{plan.name}</div>
                        <p className="text-sm text-muted-foreground mt-1">
                          {plan.description} {plan.monthly_price > 0 ? ` for ${getCurrencySymbol(plan.currency)}${plan.monthly_price}/month` : ""}
                        </p>
                        {plan.extra_info && typeof plan.extra_info === 'object' && plan.extra_info['Learn more'] && (
                          <a href={(plan.extra_info['Learn more'] as { value: string }).value} className="text-sm text-primary flex items-center gap-1 mt-2">
                            Learn more <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                    </div>
                  <div className="font-semibold">
                    {plan.discounted_price > 0 ? `+${getCurrencySymbol(plan.currency)}${plan.discounted_price}` : "Free"}
                  </div>
                  </Label>
                ))}
              </RadioGroup>
            </div>

            <div className="pt-4 border-t border-border">
              <Label className="text-base font-semibold mb-3 block">Add-ons</Label>
              {pricingData["Add-on"].map((addon) => (
                <div key={addon.id} className="flex items-start gap-3 p-4 border-2 border-border rounded-lg">
                  <Checkbox
                    id={`addon-${addon.id}`}
                    checked={formData.liveReviews}
                    onCheckedChange={(checked) => updateFormData("liveReviews", checked as boolean)}
                  />
                  <div className="flex-1">
                    <Label htmlFor={`addon-${addon.id}`} className="font-semibold cursor-pointer">
                      {addon.name}
                    </Label>
                    <p className="text-sm text-muted-foreground mt-1">
                      {addon.description}
                    </p>
                  </div>
                  <div className="font-semibold">+{getCurrencySymbol(addon.currency)}{addon.discounted_price}</div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {stepNumber === 7 && pricingData && (() => {
          const selectedPackage = getPackageById(formData.package);
          const selectedHosting = getPackageById(formData.hostingPlan);
          const liveReviewsPackage = pricingData["Add-on"].find(p => p.name.toLowerCase().includes('live reviews'));

          const originalPackagePrice = selectedPackage?.promotions?.length
            ? parseFloat(selectedPackage.amount)
            : null;

          return (
            <div className="space-y-6">
              <div className="text-center py-6 border-2 border-primary/20 rounded-lg bg-primary/5">
                <div className="text-sm text-muted-foreground mb-2">Total Price</div>
                <div className="text-4xl font-bold text-foreground">{getCurrencySymbol(selectedPackage?.currency || 'USD')}{calculatePrice()}</div>
                {originalPackagePrice && selectedPackage?.promotions[0] && (
                  <div className="text-sm text-muted-foreground mt-2">
                    <span className="line-through">{getCurrencySymbol(selectedPackage.currency)}{originalPackagePrice}</span>{" "}
                    <span className="text-accent font-semibold">{selectedPackage.promotions[0].discount_percentage}% OFF</span> - First {selectedPackage.promotions[0].units_available} spots only!
                  </div>
                )}
              </div>

              <div className="space-y-4">
                <div className="p-4 bg-muted/50 rounded-lg">
                  <div className="font-semibold mb-2">Price Breakdown:</div>
                  <div className="space-y-1 text-sm">
                    {selectedPackage && (
                      <div className="flex justify-between">
                        <span>{selectedPackage.name}</span>
                        <span>{getCurrencySymbol(selectedPackage.currency)}{selectedPackage.discounted_price}</span>
                      </div>
                    )}
                    {selectedHosting && selectedHosting.discounted_price > 0 && (
                      <div className="flex justify-between">
                        <span>{selectedHosting.name}</span>
                        <span>{getCurrencySymbol(selectedHosting.currency)}{selectedHosting.discounted_price}</span>
                      </div>
                    )}
                    {formData.liveReviews && liveReviewsPackage && (
                      <div className="flex justify-between">
                        <span>{liveReviewsPackage.name}</span>
                        <span>{getCurrencySymbol(liveReviewsPackage.currency)}{liveReviewsPackage.discounted_price}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="p-4 bg-accent/10 rounded-lg text-sm">
                  <p className="text-muted-foreground">
                    <strong>Payment Note:</strong> If guests pay online, a bank processing fee of up to 3.9% (depending on booking currency and location) will apply. 
                    These are bank charges. This fee will not be charged if guests pay in person.
                  </p>
                </div>

                <div className="flex items-start gap-3 p-4 border-2 border-border rounded-lg">
                  <Checkbox
                    id="microInvest"
                    checked={formData.microInvest}
                    onCheckedChange={(checked) => updateFormData("microInvest", checked as boolean)}
                  />
                  <Label htmlFor="microInvest" className="cursor-pointer leading-relaxed">
                    Interested to apply for up to 65% refund through the micro invest scheme
                  </Label>
                </div>
              </div>
            </div>
          );
        })()}

        <div className="flex justify-between pt-6">
          <Button
            variant="outline"
            onClick={() => setStepNumber((prev) => Math.max(1, prev - 1))}
            disabled={stepNumber === 1}
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Back
          </Button>

          {stepNumber < totalSteps ? (
            renderNextButton()
          ) : (
            <Button onClick={handleSubmit} disabled={!canProceed()}>
              Complete & Pay
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
