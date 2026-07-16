"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const ITEMS = [
  { href: "/", label: "Home", icon: "M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" },
  { href: "/analytics", label: "Analytics", icon: "M3 3v18h18M7 15l4-6 4 3 5-8" },
  { href: "/achievements", label: "Awards", icon: "M12 2l2.9 6.3 6.9.8-5 4.8 1.3 6.8L12 17.3 5.9 20.7l1.3-6.8-5-4.8 6.9-.8z" },
  { href: "/profile", label: "Profile", icon: "M12 2v0" }, // profile icon rendered separately below
];

export function Dock() {
  const pathname = usePathname();
  return (
    <div className="glass fixed bottom-4 left-1/2 z-10 w-[calc(100%-36px)] max-w-[394px] -translate-x-1/2 rounded-[24px]">
      <div className="flex justify-around px-1.5 py-2.5">
        {ITEMS.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex flex-col items-center gap-0.5 rounded-[14px] px-2.5 py-1.5 text-foam/40 ${
                active ? "bg-aqua/10 text-aqua-soft" : ""
              }`}
            >
              {item.label === "Profile" ? (
                <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="8" r="4" />
                  <path d="M4 21c0-4 4-6 8-6s8 2 8 6" />
                </svg>
              ) : (
                <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                  <path d={item.icon} />
                </svg>
              )}
              <span className="text-[9px] font-semibold">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
