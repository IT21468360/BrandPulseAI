"use client";

import Sidebar from "../components/dashboard/Sidebar";
import Header from "../components/Header";
import Footer from "../components/Footer";

export default function DashboardLayout({children}) {
  return (
    <div className="flex flex-col min-h-screen">
      {/* <Header /> */}

      <div className="flex flex-1">
        {/* Sidebar */}
        <Sidebar />

        {/* Main Content */}
        <main className="flex-1 bg-gray-100">{children}</main>
      </div>

      <Footer />
    </div>
  );
}
