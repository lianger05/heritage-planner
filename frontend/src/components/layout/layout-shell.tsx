"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Map, FileText, FolderOpen, Home } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from "@/components/ui/sheet";
import { useState } from "react";

const navItems = [
  { href: "/", label: "首页", icon: Home },
  { href: "/map", label: "地图", icon: Map },
  { href: "/plan", label: "规划", icon: FileText },
  { href: "/project", label: "项目", icon: FolderOpen },
];

function PagodaIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M12 2 L15 5 L14.5 5 L17 8 L16 8 L18 11 L6 11 L8 8 L7 8 L9.5 5 L9 5 Z" />
      <rect x="10" y="11" width="4" height="5" />
      <path d="M8 16 L16 16" />
      <rect x="9" y="16" width="6" height="4" />
      <line x1="12" y1="20" x2="12" y2="22" />
    </svg>
  );
}

export function LayoutShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex min-h-screen flex-col">
      {/* Top Nav */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center px-4">
          {/* Logo */}
          <Link href="/" className="mr-6 flex items-center space-x-2 group">
            <PagodaIcon className="h-5 w-5 text-primary group-hover:scale-110 transition-transform" />
            <span className="font-medium text-lg">古建规划助手</span>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden sm:flex items-center space-x-1 text-sm">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center px-3 py-2 rounded-md transition-colors hover:bg-accent",
                  pathname === item.href
                    ? "bg-accent text-accent-foreground font-medium"
                    : "text-muted-foreground"
                )}
              >
                <item.icon className="mr-1.5 h-4 w-4" />
                {item.label}
              </Link>
            ))}
          </nav>

          {/* Mobile Menu */}
          <div className="sm:hidden ml-auto">
            <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="sm" className="px-2">☰</Button>
              </SheetTrigger>
              <SheetContent side="right" className="w-[240px] pt-12">
                <nav className="flex flex-col gap-1">
                  {navItems.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setMobileOpen(false)}
                      className={cn(
                        "flex items-center px-3 py-2.5 rounded-md text-sm transition-colors hover:bg-accent",
                        pathname === item.href
                          ? "bg-accent text-accent-foreground font-medium"
                          : "text-muted-foreground"
                      )}
                    >
                      <item.icon className="mr-2 h-4 w-4" />
                      {item.label}
                    </Link>
                  ))}
                </nav>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">{children}</main>
    </div>
  );
}
