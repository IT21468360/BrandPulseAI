"use client";

import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Dialog, DialogPanel } from "@headlessui/react";
import { Bars3Icon, XMarkIcon } from "@heroicons/react/24/outline";

const navigation = [
  { name: "Keyword Management", href: "/keywordmanagement" },
  { name: "Aspect Classification", href: "/aspectclassification" },
  { name: "Sentiment Analysis", href: "/sentimentanalysis" },
  { name: "Explainability", href: "/explainability" },
];

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const validateToken = async () => {
      const token = localStorage.getItem("token");
      if (!token) return setIsLoggedIn(false);

      try {
        const response = await fetch("/api/auth/validate", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          setIsLoggedIn(true);
        } else {
          localStorage.removeItem("token");
          setIsLoggedIn(false);
        }
      } catch {
        localStorage.removeItem("token");
        setIsLoggedIn(false);
      }
    };

    validateToken();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
    router.push("/auth/signin");
  };

  return (
    <header className="relative z-50 bg-[#0B1F3F] text-white">
      <nav className="flex items-center justify-between p-4 sm:p-6 lg:px-8">
        {/* Logo */}
        <div className="flex lg:flex-1">
          <a href="/" className="text-2xl font-bold">
            BRAND PULSE AI
          </a>
        </div>

        {/* Navigation for Logged-In Users */}
        {isLoggedIn ? (
          <div className="hidden lg:flex lg:gap-x-12">
            {navigation.map((item) => (
              <a
                key={item.name}
                href={item.href}
                className={`text-sm font-semibold ${
                  pathname === item.href ? "text-blue-300" : "text-white hover:text-blue-300"
                }`}
              >
                {item.name}
              </a>
            ))}
          </div>
        ) : null}

        {/* Mobile Menu Button */}
        <div className="flex lg:hidden">
          <button
            type="button"
            onClick={() => setMobileMenuOpen(true)}
            className="inline-flex items-center justify-center rounded-md p-2.5 text-white"
          >
            <Bars3Icon aria-hidden="true" className="h-6 w-6" />
          </button>
        </div>

        {/* Profile Dropdown for Logged-In Users */}
        {isLoggedIn ? (
          <div className="hidden lg:flex lg:flex-1 lg:justify-end relative">
            <button
              onClick={() => setUserMenuOpen((prev) => !prev)}
              className={`flex items-center justify-center w-10 h-10 rounded-full transition-colors ${
                userMenuOpen ? "bg-white" : "bg-transparent"
              }`}
            >
              <img
                alt="Profile"
                src="/person.svg"
                className="h-6 w-6 rounded-full filter invert brightness-100"
              />
            </button>

            {userMenuOpen && (
              <div className="absolute right-0 mt-4 w-48 bg-white text-gray-900 rounded shadow-md z-10">
                <a
                  href="/profile"
                  className="block px-4 py-2 text-sm hover:bg-gray-100"
                >
                  Profile
                </a>
                <a
                  href="/settings"
                  className="block px-4 py-2 text-sm hover:bg-gray-100"
                >
                  Settings
                </a>
                <button
                  onClick={handleLogout}
                  className="w-full text-left block px-4 py-2 text-sm hover:bg-gray-100"
                >
                  Log out
                </button>
              </div>
            )}
          </div>
        ) : (
          <a
            href="/auth/signin"
            className="text-sm sm:text-base font-semibold border border-white px-4 py-2 rounded-md hover:bg-white hover:text-[#0B1F3F]"
          >
            Log in →
          </a>
        )}
      </nav>

      {/* Mobile Menu */}
      <Dialog open={mobileMenuOpen} onClose={() => setMobileMenuOpen(false)} className="lg:hidden">
        <div className="fixed inset-0 z-50 bg-black/50" aria-hidden="true" />
        <DialogPanel className="fixed inset-y-0 right-0 z-50 w-full max-w-sm overflow-y-auto bg-white text-gray-900 px-6 py-6">
          <div className="flex items-center justify-between">
            <a href="/" className="text-xl font-bold">
              BRAND PULSE AI
            </a>
            <button
              type="button"
              onClick={() => setMobileMenuOpen(false)}
              className="rounded-md p-2.5 text-gray-700"
            >
              <XMarkIcon aria-hidden="true" className="h-6 w-6" />
            </button>
          </div>
          <div className="mt-6">
            <div className="space-y-4">
              {navigation.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className={`block px-3 py-2 rounded-lg text-lg font-semibold ${
                    pathname === item.href ? "text-blue-600" : "text-gray-900"
                  }`}
                >
                  {item.name}
                </a>
              ))}
            </div>
          </div>
          <div className="mt-6">
            {isLoggedIn ? (
              <button
                onClick={handleLogout}
                className="w-full text-left block px-4 py-2 text-lg text-gray-900 bg-gray-100 rounded-lg"
              >
                Log out
              </button>
            ) : (
              <a
                href="/auth/signin"
                className="block w-full text-center px-4 py-2 text-lg font-semibold text-white bg-[#0B1F3F] rounded-lg"
              >
                Log in →
              </a>
            )}
          </div>
        </DialogPanel>
      </Dialog>
    </header>
  );
}
