"use client";
import { usePathname } from "next/navigation";
import { Toaster } from "react-hot-toast";

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  // Define the paths where you don't want to show the Appbar
  const noAppbarPaths = ["/signup", "/signin"];

  return (
    <div>
      {children}
      <Toaster position="bottom-right" />
    </div>
  );
}