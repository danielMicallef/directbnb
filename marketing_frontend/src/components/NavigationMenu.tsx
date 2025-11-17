"use client"

import * as React from "react"
import { Link } from "react-router-dom"

import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu"

export function SiteNavigationMenu() {
  return (
    <NavigationMenu>
      <NavigationMenuList>
        <NavigationMenuItem>
          <NavigationMenuLink asChild className={`${navigationMenuTriggerStyle()} bg-transparent`}>
            <a href="/#pricing">Pricing</a>
          </NavigationMenuLink>
        </NavigationMenuItem>
        <NavigationMenuItem>
          <NavigationMenuLink asChild className={`${navigationMenuTriggerStyle()} bg-transparent`}>
            <a href="/#how-it-works">How it works</a>
          </NavigationMenuLink>
        </NavigationMenuItem>
        <NavigationMenuItem>
          <NavigationMenuLink asChild className={`${navigationMenuTriggerStyle()} bg-transparent`}>
            <a href="/#savings-calculator">Savings Calculator</a>
          </NavigationMenuLink>
        </NavigationMenuItem>
      </NavigationMenuList>
    </NavigationMenu>
  )
}
