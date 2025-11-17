"use client"

import { useState, useMemo } from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"

export function SavingsCalculator() {
  const [avgPrice, setAvgPrice] = useState(100)
  const [occupancyRate, setOccupancyRate] = useState(50)
  const [nightsPerYear, setNightsPerYear] = useState(Math.round(365 * 0.5))
  const [calculationMode, setCalculationMode] = useState<"occupancy" | "nights">("occupancy")

  const handleOccupancyChange = (value: number) => {
    setOccupancyRate(value)
    setNightsPerYear(Math.round(365 * (value / 100)))
  }

  const handleNightsChange = (value: number) => {
    setNightsPerYear(value)
    setOccupancyRate(Math.round((value / 365) * 100))
  }

  const yearlySavings = useMemo(() => {
    const savings = avgPrice * nightsPerYear * 0.15
    return savings.toLocaleString("en-MT", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    })
  }, [avgPrice, nightsPerYear])

  return (
    <Card className="max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="text-center">Every year you will save</CardTitle>
      </CardHeader>
      <CardContent className="grid md:grid-cols-2 gap-8 items-center">
        <div className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="avgPrice">Average Price per Night (€)</Label>
            <Input
              id="avgPrice"
              type="number"
              value={avgPrice}
              onChange={(e) => setAvgPrice(Number(e.target.value))}
              className="text-lg"
            />
          </div>

          <RadioGroup value={calculationMode} onValueChange={(value) => setCalculationMode(value as "occupancy" | "nights")} className="flex gap-4">
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="occupancy" id="occupancy" />
              <Label htmlFor="occupancy">Occupancy Rate</Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="nights" id="nights" />
              <Label htmlFor="nights">Nights per Year</Label>
            </div>
          </RadioGroup>

          {calculationMode === 'occupancy' ? (
            <div className="space-y-2">
              <div className="flex justify-between">
                <Label htmlFor="occupancyRate">Occupancy Rate (%)</Label>
                <span className="font-semibold">{occupancyRate}%</span>
              </div>
              <Slider
                id="occupancyRate"
                min={0}
                max={100}
                step={1}
                value={[occupancyRate]}
                onValueChange={(value) => handleOccupancyChange(value[0])}
              />
            </div>
          ) : (
            <div className="space-y-2">
              <Label htmlFor="nightsPerYear">Number of Nights per Year</Label>
              <Input
                id="nightsPerYear"
                type="number"
                value={nightsPerYear}
                onChange={(e) => handleNightsChange(Number(e.target.value))}
                className="text-lg"
              />
            </div>
          )}
        </div>
        <div className="flex flex-col items-center justify-center p-8 bg-primary/5 rounded-lg">
          <p className="text-lg text-muted-foreground mb-2">You Save Up To</p>
          <Badge className="text-4xl font-bold px-6 py-3 bg-accent text-accent-foreground">
            {yearlySavings}
          </Badge>
          <p className="text-sm text-muted-foreground mt-2">per year</p>
        </div>
      </CardContent>
    </Card>
  )
}
