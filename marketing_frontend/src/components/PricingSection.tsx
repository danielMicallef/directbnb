import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Check } from "lucide-react"
import { PackagePlan } from "@/data/booking-form";

interface PricingProps {
    onPackageSelect: (packageName: PackagePlan) => void;
}

export function Pricing({ onPackageSelect }: PricingProps) {
    const pricingDetails = {
        "Premium": {
            price: "€650",
            price_description: "one-time fee",
            features: [
                "Customized Website",
                "Reservation Calendar",
                "Reservation List",
                "Guest List",
                "Reservation Export",
                "Direct Communication",
                "Flexible Pricing Options",
                "BNB Shuttle Integration",
                "Custom Domain Name",
                "No Commission Bookings*",
                "1 Year Hosting Included",
            ],
            buttonText: "Choose Premium"
        },
        "Custom": {
            price: "€3500",
            price_description: "one-time fee",
            features: [
                "All features from Premium",
                "Work with our developers to create your own unique website",
            ],
            buttonText: "Go Tailor Made"
        }
    }

    return (
        <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
                <div className="space-y-2">
                    <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">Commission-Free Bookings for Your Rental</h2>
                    <p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                        Choose the plan that's right for you. Get a stunning, commission-free booking website for your property.
                    </p>
                </div>
            </div>
            <div className="mx-auto grid max-w-sm items-stretch gap-8 sm:max-w-4xl sm:grid-cols-2 md:gap-12 lg:max-w-5xl lg:grid-cols-2 pt-12">
                {Object.entries(pricingDetails).map(([title, details]) => (
                    <Card key={title} className="flex flex-col">
                        <CardHeader className="p-6">
                            <CardTitle className="text-2xl font-bold">{title}</CardTitle>
                            <div className="flex items-baseline gap-2">
                                <span className="text-4xl font-bold tracking-tight">{details.price}</span>
                                <span className="text-sm text-muted-foreground">{details.price_description}</span>
                            </div>
                        </CardHeader>
                        <CardContent className="p-6 flex flex-col gap-4 flex-1">
                            <ul className="grid gap-2">
                                {details.features.map((feature) => (
                                    <li key={feature} className="flex items-center gap-2">
                                        <Check className="h-4 w-4 text-primary" />
                                        <span>{feature}</span>
                                    </li>
                                ))}
                            </ul>
                            <Button className="w-full mt-auto" onClick={() => onPackageSelect(title.toLowerCase() as PackagePlan)}>{details.buttonText}</Button>
                        </CardContent>
                    </Card>
                ))}
            </div>
            <div className="mt-8 text-center text-sm text-muted-foreground">
                *Card payments are subject to a processing fee of up to 3.9%, depending on your guest's currency and location.
            </div>
        </div>
    )
}
