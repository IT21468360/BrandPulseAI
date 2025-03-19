"use client";

import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Header from "@/app/components/Header";
import Footer from "@/app/components/Footer";

export default function KeywordManagement() {
  const router = useRouter();
  const pathname = usePathname();

  // 🔹 State Management
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [brands, setBrands] = useState([]);
  const [selectedBrand, setSelectedBrand] = useState("");
  const [dateRange, setDateRange] = useState({ start: "", end: "" });
  const [inputUrl, setInputUrl] = useState("");
  const [keywords, setKeywords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("");

  // ✅ **Check login status on page load**
  useEffect(() => {
    const token = localStorage.getItem("token");
    const storedUser = JSON.parse(localStorage.getItem("user"));

    if (!token || !storedUser) {
      router.push("/auth/signin");
    } else {
      setIsLoggedIn(true);
      setUser(storedUser);
      fetchBrands(storedUser.id);
    }
  }, []);

  // ✅ **Fetch Brands Linked to User**
  const fetchBrands = async (userId) => {
    try {
      const res = await fetch(`/api/brand/${userId}`);
      if (!res.ok) throw new Error(`API returned ${res.status}: ${res.statusText}`);
      const data = await res.json();
      setBrands(data.brands || []);
    } catch (error) {
      console.error("❌ Error fetching brands:", error);
    }
  };

  // ✅ **Fetch Keywords from MongoDB Based on Language**
  const fetchStoredKeywords = async (language) => {
    if (!selectedBrand || !inputUrl || !dateRange.start || !dateRange.end) {
      alert("Please enter Brand Name, Date Range, and Website URL!");
      return;
    }

    try {
      setLoading(true);
      setLoadingMessage(`🔍 Fetching stored ${language.toUpperCase()} keywords...`);

      const res = await fetch(
        `/api/keywords/extract/english?user_id=${user.id}&brand=${selectedBrand}&url=${inputUrl}&language=${language}&start=${dateRange.start}&end=${dateRange.end}`
      );

      if (!res.ok) throw new Error("Failed to fetch stored keywords.");

      const data = await res.json();
      setKeywords(data.keywords || []);
    } catch (error) {
      console.error("❌ Error fetching stored keywords:", error);
    } finally {
      setLoading(false);
      setLoadingMessage("");
    }
  };

  // ✅ **Remove a Keyword from Display**
  const removeKeyword = (keyword) => {
    setKeywords(keywords.filter((kw) => kw !== keyword));
  };

  // ✅ **Redirect to Aspect Classification Page**
  const applyKeywords = () => {
    router.push("/aspectclassification");
  };

  if (!isLoggedIn) return null;

  return (
    <div className="bg-gray-100 min-h-screen">
      <Header activeTab={pathname} showFullNav={true} />

      <div className="max-w-6xl mx-auto py-10 px-6">
        {/* 🔹 Main Title */}
        <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold shadow-md">
          KEYWORD MANAGEMENT
        </div>

        {/* 🔹 Keyword Generation Section */}
        <div className="mt-6 bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold shadow-md">
          Keyword Generation
        </div>

        <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
          <label className="block text-sm font-semibold mb-2">Select Brand</label>
          <select className="w-full border p-3 rounded-md shadow-md" value={selectedBrand} onChange={(e) => setSelectedBrand(e.target.value)}>
            <option value="">Choose a Brand</option>
            {brands.map((brand, index) => (
              <option key={brand._id || index} value={brand.brand_name}>
                {brand.brand_name}
              </option>
            ))}
          </select>

          <label className="block text-sm font-semibold mt-4">Website URL</label>
          <input type="text" className="w-full border p-3 rounded-md shadow-md" placeholder="Enter Website URL" value={inputUrl} onChange={(e) => setInputUrl(e.target.value)} />

          <label className="block text-sm font-semibold mt-4">Start Date</label>
          <input type="date" className="w-full border p-3 rounded-md shadow-md" onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })} />

          <label className="block text-sm font-semibold mt-4">End Date</label>
          <input type="date" className="w-full border p-3 rounded-md shadow-md" onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })} />
        </div>

        {/* 🔹 Generate Buttons */}
        <div className="mt-6 flex justify-end space-x-4">
          <button onClick={() => fetchStoredKeywords("sinhala")} className="bg-[#0B1F3F] text-white px-6 py-3 rounded-md shadow-lg">
            Generate Sinhala Keywords
          </button>
          <button onClick={() => fetchStoredKeywords("english")} className="bg-[#0B1F3F] text-white px-6 py-3 rounded-md shadow-lg">
            Generate English Keywords
          </button>
        </div>

        {/* 🔹 Keyword Results Section */}
        <div className="mt-6 bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold shadow-md">
          Keyword Results
        </div>

        <div className="mt-6 bg-white p-6 rounded-lg shadow-md flex flex-wrap gap-2">
          {keywords.map((keyword, index) => (
            <div key={index} className="relative bg-blue-500 text-white font-bold px-4 py-2 rounded-lg shadow-md cursor-pointer flex items-center">
              <span>{keyword}</span>
              <button
                onClick={() => removeKeyword(keyword)}
                className="absolute top-1 right-2 text-white text-sm font-bold"
              >
                ×
              </button>
            </div>
          ))}
        </div>

        {/* 🔹 Apply Button */}
        <div className="mt-6 flex justify-end">
          <button onClick={applyKeywords} className="bg-[#0B1F3F] text-white px-6 py-3 rounded-md shadow-lg">
            Apply
          </button>
        </div>
      </div>
      <Footer />
    </div>
  );
}
