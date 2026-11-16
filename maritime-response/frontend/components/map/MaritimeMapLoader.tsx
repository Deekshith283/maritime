"use client";

import dynamic from "next/dynamic";

const MaritimeMap = dynamic(
  () => import("./MaritimeMap"),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-[650px] items-center justify-center rounded-xl bg-white text-slate-500">
        Loading maritime map...
      </div>
    ),
  }
);

export default function MaritimeMapLoader() {
  return <MaritimeMap />;
}
