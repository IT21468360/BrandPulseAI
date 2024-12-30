"use client";

import {useState} from "react";
import {Bars3Icon, XMarkIcon} from "@heroicons/react/24/outline";
import {useRouter, usePathname} from "next/navigation";
import {menuItems} from "../../constants/SidebarMenuItems";

export default function Sidebar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  return (
    <>
      {/* Sidebar for Desktop */}
      <div className="hidden md:flex flex-col bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-white w-64 min-h-screen">
        <div className="p-4 text-lg font-bold border-b border-gray-200 dark:border-gray-700">
          My Dashboard
        </div>
        <ul className="flex flex-col gap-4 p-4">
          {menuItems.map((item) => (
            <li
              key={item.id}
              className={`cursor-pointer p-2 rounded transition-colors ${
                pathname === item.path
                  ? "bg-indigo-600 text-white"
                  : "hover:bg-indigo-100 dark:hover:bg-gray-700"
              }`}
              onClick={() => router.push(item.path)}
            >
              {item.label}
            </li>
          ))}
        </ul>
      </div>

      {/* Sidebar for Mobile */}
      <div className="md:hidden">
        <button
          className="p-2"
          onClick={() => setMobileMenuOpen((prev) => !prev)}
        >
          {mobileMenuOpen ? (
            <XMarkIcon className="h-6 w-6 text-gray-900 dark:text-gray-300" />
          ) : (
            <Bars3Icon className="h-6 w-6 text-gray-900 dark:text-gray-300" />
          )}
        </button>
        {mobileMenuOpen && (
          <div className="fixed top-0 left-0 w-64 h-full bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-white z-50 shadow-lg">
            <div className="p-4 text-lg font-bold border-b border-gray-200 dark:border-gray-700">
              My Dashboard
            </div>
            <ul className="flex flex-col gap-4 p-4">
              {menuItems.map((item) => (
                <li
                  key={item.id}
                  className={`cursor-pointer p-2 rounded transition-colors ${
                    pathname === item.path
                      ? "bg-indigo-600 text-white"
                      : "hover:bg-indigo-100 dark:hover:bg-gray-700"
                  }`}
                  onClick={() => {
                    router.push(item.path);
                    setMobileMenuOpen(false); // Close sidebar after selecting
                  }}
                >
                  {item.label}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </>
  );
}
