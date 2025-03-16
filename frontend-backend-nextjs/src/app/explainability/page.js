"use client";

import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Header from "@/app/components/Header";
import Footer from "@/app/components/Footer";

export default function Explainability() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const router = useRouter();
  const pathname = usePathname(); // Get the current page URL

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/auth/signin");
    } else {
      setIsLoggedIn(true);
    }
  }, []);

  if (!isLoggedIn) return null;

  return (
    <div className="bg-gray-100 min-h-screen">
      {/* Pass the pathname to the Header */}
      <Header activeTab={pathname} showFullNav={true} />

      <div className="max-w-6xl mx-auto py-10 px-6">
        <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold">
          EXPLAINABILITY
        </div>

        <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">
            Explainability in AI
          </h3>
          <p className="text-gray-700">
            Explainability helps in understanding why an AI model made a specific decision. 
            It provides insights into sentiment predictions and enhances transparency in AI-driven analysis.
          </p>
        </div>

        <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">
            How Explainability Works
          </h3>
          <ul className="list-disc list-inside text-gray-700 space-y-2">
            <li>Uses SHAP, LIME, and other explainability techniques.</li>
            <li>Provides interpretation of sentiment analysis results.</li>
            <li>Helps in debugging and improving model accuracy.</li>
          </ul>
        </div>
      </div>

      <Footer />
    </div>
  );
}
