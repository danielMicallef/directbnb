import { useState } from "react";
import { useLocalStorage } from "@/hooks/useLocalStorage";
import { Button } from "@/components/ui/button";
import { SiteNavigationMenu } from "@/components/NavigationMenu";
import { SavingsCalculator } from "@/components/SavingsCalculator";
import { BookingFormWizard } from "@/components/BookingFormWizard";
import { FormData, initialFormData, PackagePlan } from "@/data/booking-form";
import { Check, House, TrendingDown, Globe, DollarSign, BarChart3, ArrowRight } from "lucide-react";
import { Pricing } from "@/components/PricingSection";
import { Section } from "@/components/Section";

const Index = () => {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useLocalStorage<FormData>('formData', initialFormData, 5);
  const [stepNumber, setStepNumber] = useLocalStorage<number>('stepNumber', 1, 5);

  const handlePackageSelect = (packageName: PackagePlan) => {
    setFormData(prev => ({ ...prev, package: packageName }));
    setShowForm(true);
  };

  if (showForm) {
    return (
      <div className="min-h-screen bg-background py-12 px-4">
        <div className="container mx-auto">
          <Button variant="outline" className="mb-2" onClick={() => setShowForm(false)}><House />Home</Button>
          <BookingFormWizard formData={formData} setFormData={setFormData} stepNumber={stepNumber} setStepNumber={setStepNumber} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-primary/5 to-background">
        <div className="flex justify-center pt-4">
          <SiteNavigationMenu />
        </div>
        <div className="container mx-auto px-4 py-20 md:py-32">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent/10 text-accent font-medium text-sm mb-6">
              <TrendingDown className="w-4 h-4" />
              Stop Paying 15-20% Commission
            </div>
            <h1 className="text-4xl md:text-6xl font-bold mb-6 text-balance">
              Get Direct Bookings. <span className="text-primary">Zero Commission.</span>
            </h1>
            <p className="text-xl text-muted-foreground mb-8 text-pretty max-w-2xl mx-auto">
              Create your own professional booking website in minutes. Import your Airbnb or Booking.com listing
              automatically and start accepting commission-free reservations.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" onClick={() => setShowForm(true)} className="text-lg">
                Get Started Now
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
              <Button size="lg" variant="outline" onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })} className="text-lg">
                See How It Works
              </Button>
            </div>
            <p className="text-sm text-muted-foreground mt-6">
              Setup takes less than 5 minutes • No technical skills required
            </p>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <Section title="Why Hosts Choose Direct Booking" className="bg-muted/30">
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <div className="bg-card p-8 rounded-lg shadow-sm border border-border">
              <div className="w-12 h-12 bg-accent/20 rounded-lg flex items-center justify-center mb-4">
                <DollarSign className="w-6 h-6 text-accent" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-card-foreground">Save 15-20% Commission</h3>
              <p className="text-muted-foreground">
                Keep every dollar you earn. On a $150/night booking, you save $30 per night - that's $900/month on just one property!
              </p>
            </div>

            <div className="bg-card p-8 rounded-lg shadow-sm border border-border">
              <div className="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center mb-4">
                <Globe className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-card-foreground">Your Brand, Your Rules</h3>
              <p className="text-muted-foreground">
                Build direct relationships with guests. No platform restrictions, no competing listings, just your property showcase.
              </p>
            </div>

            <div className="bg-card p-8 rounded-lg shadow-sm border border-border">
              <div className="w-12 h-12 bg-accent/20 rounded-lg flex items-center justify-center mb-4">
                <BarChart3 className="w-6 h-6 text-accent" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-card-foreground">Guest Data Is Yours</h3>
              <p className="text-muted-foreground">
                Own your guest relationships. Send personalized offers, build loyalty, and increase repeat bookings by 40%.
              </p>
            </div>
          </div>
      </Section>

      {/* How It Works */}
      <Section id="how-it-works" title="Launch Your Website in 3 Simple Steps">
          <p className="text-center text-muted-foreground mb-12 text-lg">
            No coding. No design skills. Just a few clicks.
          </p>
          <div className="max-w-4xl mx-auto space-y-8">
            <div className="flex gap-6 items-start">
              <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center text-primary-foreground font-bold text-xl flex-shrink-0">
                1
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2 text-foreground">Choose Your Style</h3>
                <p className="text-muted-foreground">
                  Pick from City, Mountain, or Seaside themes. Select your color scheme. We'll import your property details automatically from your current listings.
                </p>
              </div>
            </div>

            <div className="flex gap-6 items-start">
              <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center text-primary-foreground font-bold text-xl flex-shrink-0">
                2
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2 text-foreground">Get Your Domain</h3>
                <p className="text-muted-foreground">
                  Choose a memorable domain name for your property. We'll help you register it and handle all the technical setup.
                </p>
              </div>
            </div>

            <div className="flex gap-6 items-start">
              <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center text-primary-foreground font-bold text-xl flex-shrink-0">
                3
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2 text-foreground">Start Getting Direct Bookings</h3>
                <p className="text-muted-foreground">
                  Your website goes live instantly. We'll share proven strategies to drive traffic and turn visitors into guests.
                </p>
              </div>
            </div>
          </div>
      </Section>


      {/* Calculate Savings Section */}
      <Section id="savings-calculator" title="Calculate Yearly Savings" className="bg-muted/30">
          <SavingsCalculator />
      </Section>

      {/* Social Proof - Websites Built */}
      <Section title="Websites We've Built" className="py-16 bg-background">
          <div className="relative overflow-x-auto">
            <div className="flex gap-6">
              {[
                { name: "MountainView Chalet", url: "mountainviewchalet.com", imageUrl: "https://images.unsplash.com/photo-1542662565-7e4b66bae529?q=80&w=400&h=300&auto=format&fit=crop" },
                { name: "Seaside View Apartment", url: "seaviewapartmentxlendi.com", imageUrl: "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=400&h=300&auto=format&fit=crop" },
                { name: "Urban Loft Downtown", url: "urbanloftdowntown.com", imageUrl: "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?q=80&w=400&h=300&auto=format&fit=crop" },
                { name: "Cozy Cabin Escape", url: "cozycabinescape.com", imageUrl: "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?q=80&w=400&h=300&auto=format&fit=crop" },
                { name: "Beachfront Paradise", url: "beachfrontparadise.com", imageUrl: "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?q=80&w=400&h=300&auto=format&fit=crop" },
                { name: "City Center Apartment", url: "citycenterapt.com", imageUrl: "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?q=80&w=400&h=300&auto=format&fit=crop" },
              ].map((site, idx) => (
                <a
                  key={idx}
                  href={`https://${site.url}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-shrink-0 w-64 p-6 bg-card rounded-lg border border-border shadow-sm hover:shadow-lg transition-shadow cursor-pointer"
                >
                  <img
                    src={site.imageUrl}
                    alt={`Preview of ${site.name}`}
                    className="w-full h-32 object-cover bg-muted rounded-md mb-4"
                  />
                  <h3 className="font-semibold text-card-foreground mb-1">{site.name}</h3>
                  <p className="text-sm text-muted-foreground">{site.url}</p>
                </a>
              ))}
            </div>
          </div>
      </Section>

      {/* Features Grid */}
      <Section title="Everything You Need to Succeed" className="bg-muted/30">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {[
              "Mobile-optimized booking experience",
              "Automatic calendar sync",
              "Secure payment processing",
              "SEO optimization included",
              "Professional property photos",
              "Guest review management",
              "Email marketing tools",
              "Analytics & insights dashboard",
              "24/7 customer support",
            ].map((feature, idx) => (
              <div key={idx} className="flex items-start gap-3 bg-card p-4 rounded-lg border border-border">
                <Check className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                <span className="text-card-foreground">{feature}</span>
              </div>
            ))}
          </div>
      </Section>

      {/* Pricing Section */}
      <section id="pricing" className="w-full py-12 md:py-24 lg:py-32">
        <Pricing onPackageSelect={handlePackageSelect} />
      </section>


      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-primary to-accent">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center space-y-6">
            <h2 className="text-3xl md:text-5xl font-bold text-primary-foreground">
              Ready to Keep 100% of Your Earnings?
            </h2>
            <p className="text-xl text-primary-foreground/90">
              Join hundreds of hosts who've already ditched commission fees and increased their profits.
            </p>
            <Button
              size="lg"
              variant="secondary"
              onClick={() => setShowForm(true)}
              className="text-lg px-8 py-6"
            >
              Get Started - It's Free to Try
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-border">
        <div className="container mx-auto px-4 text-center text-muted-foreground">
          <p>&copy; {new Date().getFullYear()} DirectBooking. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
