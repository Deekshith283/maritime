"use client";

import Link from "next/link";
import {
  Home,
  Bell,
  Ship,
  Map,
  Settings,
} from "lucide-react";

const items = [
  {
    title: "Dashboard",
    icon: Home,
    href: "/",
  },
  {
    title: "Incidents",
    icon: Bell,
    href: "/incidents",
  },
  {
    title: "Vessels",
    icon: Ship,
    href: "/vessels",
  },
  {
    title: "Map",
    icon: Map,
    href: "/map",
  },
  {
    title: "Settings",
    icon: Settings,
    href: "/settings",
  },
];

export default function Sidebar() {
  return (
    <aside className="w-64 border-r bg-background">
      <div className="p-6 text-xl font-bold">
        Maritime
      </div>

      <nav className="space-y-2 px-3">
        {items.map((item) => {
          const Icon = item.icon;

          return (
            <Link
              key={item.title}
              href={item.href}
              className="flex items-center gap-3 rounded-lg px-4 py-3 hover:bg-muted"
            >
              <Icon size={20} />

              {item.title}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}