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

  // ✅ **Fetch Stored Keywords from MongoDB**
  const fetchStoredKeywords = async (language) => {
    if (!user || !selectedBrand || !inputUrl || !dateRange.start || !dateRange.end) return;

    try {
      const res = await fetch(`/api/keywords/extract/${language}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: user.id,
          brand: selectedBrand,
          url: inputUrl,
          dateRange,
          language,
          checkExisting: true, // ✅ Fetch from DB if available
        }),
      });

      const data = await res.json();
      if (data.exists && data.keywords) {
        console.log("✅ Found stored keywords in MongoDB.");
        setKeywords(Array.isArray(data.keywords) ? data.keywords : []);
      } else {
        console.warn("⚠️ No stored keywords found.");
        setKeywords([]);
      }
    } catch (error) {
      console.error("❌ Error fetching stored keywords:", error);
    }
  };

  // ✅ **Handle Keyword Extraction (English & Sinhala)**
  const handleExtractKeywords = async (language) => {
    if (!selectedBrand || !inputUrl || !dateRange.start || !dateRange.end) {
      alert("Please fill all required fields!");
      return;
    }

    setLoading(true);
    setLoadingMessage(`🔄 Extracting ${language.toUpperCase()} keywords...`);

    try {
      const res = await fetch(`/api/keywords/extract/${language}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: user.id,
          brand: selectedBrand,
          url: inputUrl,
          dateRange,
          language,
        }),
      });

      const data = await res.json();
      if (!data.keywords || data.keywords.length === 0) {
        console.warn(`⚠️ No ${language.toUpperCase()} keywords found.`);
        setKeywords([]);
      } else {
        console.log(`✅ Extracted ${language.toUpperCase()} keywords.`);
        setKeywords(data.keywords);
      }
    } catch (error) {
      console.error(`❌ Error extracting ${language} keywords:`, error);
      alert(`Failed to extract ${language} keywords. Please try again.`);
    } finally {
      setLoading(false);
      setLoadingMessage("");
    }
  };

  // ✅ **Redirect to Login if not Logged In**
  if (!isLoggedIn) return null;

  return (
    <div className="bg-gray-100 min-h-screen">
      <Header activeTab={pathname} showFullNav={true} />

      <div className="max-w-6xl mx-auto py-10 px-6">
        <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold">
          KEYWORD GENERATION
        </div>

        <div className="mt-6">
          <label className="block text-sm font-semibold mb-2">Select Brand</label>
          <select className="w-full border p-3 rounded-md" value={selectedBrand} onChange={(e) => setSelectedBrand(e.target.value)}>
            <option value="">Choose a Brand</option>
            {brands.map((brand) => (
              <option key={brand._id} value={brand.brand_name}>
                {brand.brand_name}
              </option>
            ))}
          </select>
        </div>

        <div className="mt-6 flex space-x-4">
          <input type="date" className="border p-3 rounded-md w-1/2" onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })} />
          <input type="date" className="border p-3 rounded-md w-1/2" onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })} />
        </div>

        <div className="mt-6">
          <input type="text" className="border p-3 rounded-md w-full" placeholder="Enter Website URL" value={inputUrl} onChange={(e) => setInputUrl(e.target.value)} />
        </div>

        {/* ✅ Keep Both Buttons for English & Sinhala Extraction */}
        <div className="mt-6 flex justify-end space-x-4">
          <button onClick={() => handleExtractKeywords("sinhala")} className="bg-[#0B1F3F] text-white px-6 py-3 rounded-md shadow-md">
            Generate Sinhala Keywords
          </button>
          <button onClick={() => handleExtractKeywords("english")} className="bg-[#0B1F3F] text-white px-6 py-3 rounded-md shadow-md">
            Generate English Keywords
          </button>
        </div>

        {/* 🔄 Loading Indicator */}
        {loading && <div className="mt-4 text-blue-600 text-center font-semibold">{loadingMessage} ⏳</div>}

        {/* 🔹 Extracted Keywords */}
        <div className="mt-10 bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold">
          EXTRACTED KEYWORDS
        </div>

        <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">Extracted Keywords</h3>
          <div className="flex flex-wrap gap-2">
            {(Array.isArray(keywords) ? keywords : []).map((keyword, index) => (
              <div key={index} className="bg-gray-200 px-4 py-2 rounded-md">{keyword}</div>
            ))}
          </div>
        </div>

      </div>
      <Footer />
    </div>
  );
}
