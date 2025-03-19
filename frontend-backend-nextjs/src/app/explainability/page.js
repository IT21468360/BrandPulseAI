"use client";

import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Header from "@/app/components/Header";
import Footer from "@/app/components/Footer";
import Link from "next/link";
import Image from "next/image";

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
        {/* Title Section */}
        <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold text-center">
          EXPLAINABILITY
        </div>

        {/* Slogan Section */}
        <div className="mt-4 text-center text-xl font-semibold text-gray-700">
          Improve your business with our recommendations.
        </div>

        {/* Image Section */}
        <div className="mt-6 flex justify-center">
          <Image 
            src="/images/xai-site.png" 
            alt="Explainable AI" 
            width={800} 
            height={400} 
            className="rounded-lg shadow-md"
          />
        </div>

        {/* How Explainability Works */}
        <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">
            How Explainability Works
          </h3>
          <ul className="list-disc list-inside text-gray-700 space-y-4">
            <li>
              <strong>Uses SHAP, LIME, and other explainability techniques.</strong> 
              <br />
              These techniques help analyze model predictions by highlighting which features contributed most to the decision-making process.
            </li>
            <li>
              <strong>Provides interpretation/insights and graphs of sentiment analysis results.</strong> 
              <br />
              Visual representations such as feature importance charts, force plots, and summary plots help in understanding AI model predictions.
            </li>
            <li>
              <strong>Generates a report about explainability.</strong> 
              <br />
              A detailed report is created, summarizing key insights, graphical interpretations, and explanations for model predictions.
            </li>
          </ul>
        </div>

        {/* Buttons Section */}
        <div className="mt-6 flex flex-col sm:flex-row justify-center gap-4">
          <Link href="/explainability/shap-lime">
            <button className="bg-[#0B1F3F] text-white px-6 py-3 rounded-lg font-semibold shadow-md hover:bg-[#09203b] transition">
              SHAP and LIME Explainability
            </button>
          </Link>

          <Link href="/explainability/aspect-wise">
            <button className="bg-gray-800 text-white px-6 py-3 rounded-lg font-semibold shadow-md hover:bg-gray-900 transition">
              Aspect-wise Explainability
            </button>
          </Link>
        </div>
      </div>

      <Footer />
    </div>
  );
}
