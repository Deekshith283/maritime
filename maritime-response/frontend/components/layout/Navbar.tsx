import { Bell } from "lucide-react";

export default function Navbar() {
  return (
    <header className="flex h-16 items-center justify-between border-b px-6">
      <h2 className="text-lg font-semibold">
        Maritime Safety Dashboard
      </h2>

      <Bell className="cursor-pointer" />
    </header>
  );
}