"use client";

import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Header from "@/app/components/Header";
import Footer from "@/app/components/Footer";

export default function KeywordManagement() {
  const [keywords, setKeywords] = useState([]);
  const [savedCombinations, setSavedCombinations] = useState([]);
  const [inputUrl, setInputUrl] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const router = useRouter();
  const pathname = usePathname(); // Get the current page URL

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/auth/signin");
    } else {
      setIsLoggedIn(true);
      fetchKeywords();
      fetchSavedCombinations();
    }
  }, []);

  const fetchKeywords = async () => {
    const response = await fetch("/api/keywords");
    const data = await response.json();
    setKeywords(data);
  };

  const fetchSavedCombinations = async () => {
    const response = await fetch("/api/saved-keywords");
    const data = await response.json();
    setSavedCombinations(data);
  };

  if (!isLoggedIn) return null;

  return (
    <div className="bg-gray-100 min-h-screen">
      {/* Pass the pathname to the Header */}
      <Header activeTab={pathname} showFullNav={true} />
      
      <div className="max-w-6xl mx-auto py-10 px-6">
        <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold">
          KEYWORD MANAGEMENT
        </div>
        <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center space-x-4 justify-between">
            <input
              type="text"
              value={inputUrl}
              onChange={(e) => setInputUrl(e.target.value)}
              placeholder="www.example.com"
              className="flex-grow p-3 border rounded-md shadow-lg focus:border-blue-500 focus:outline-none"
            />
            <button className="bg-[#0B1F3F] text-white px-10 py-3 rounded-md shadow-md">
              GENERATE KEYWORDS
            </button>
          </div>
        </div>

        <div className="mt-6 bg-white p-6 rounded-lg shadow-md relative">
          <h3 className="text-lg font-semibold mb-4">KEYWORD RESULTS</h3>
          <div className="flex flex-wrap gap-4 p-4 bg-gray-50 rounded-lg">
            {keywords.map((keyword, index) => (
              <div key={index} className="bg-white border px-4 py-2 rounded-lg shadow-sm flex items-center space-x-2">
                <span>{keyword}</span>
                <button className="text-red-500">✖</button>
              </div>
            ))}
          </div>
          <div className="mt-6 flex justify-end space-x-4">
            <button className="px-10 py-3 border border-blue-600 text-blue-600 bg-white rounded-md shadow-lg">
              EDIT
            </button>
            <button className="px-10 py-3 bg-[#0B1F3F] text-white rounded-md shadow-md">
              ADD
            </button>
          </div>
        </div>

        <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">SAVED KEYWORD COMBINATIONS</h3>
          {savedCombinations.map((combo, index) => (
            <div key={index} className="mb-4 p-4 border rounded-lg bg-gray-50">
              <div className="flex flex-wrap gap-4 mb-2">
                {combo.keywords.map((kw, i) => (
                  <div key={i} className="bg-white border px-4 py-2 rounded-lg shadow-sm">
                    {kw}
                  </div>
                ))}
              </div>
              <div className="flex justify-end space-x-4">
                <button className="px-10 py-3 border border-blue-600 text-blue-600 bg-white rounded-md shadow-lg">
                  EDIT
                </button>
                <button className="px-10 py-3 bg-[#0B1F3F] text-white rounded-md shadow-md">
                  APPLY
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
      <Footer />
    </div>
  );
}
