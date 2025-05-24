"use client";

import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Header from "@/app/components/Header";
import Footer from "@/app/components/Footer";

export default function KeywordManagement() {
  const router = useRouter();
  const pathname = usePathname();

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [brands, setBrands] = useState([]);
  const [selectedBrand, setSelectedBrand] = useState("");
  const [selectedUrl, setSelectedUrl] = useState("");
  const [availableUrls, setAvailableUrls] = useState([]);
  const [dateRange, setDateRange] = useState({ start: "", end: "" });

  const [keywords, setKeywords] = useState([]);
  const [savedCombination, setSavedCombination] = useState([]);
  const [savedToDb, setSavedToDb] = useState(false);
  const [allSavedCombinations, setAllSavedCombinations] = useState([]);

  const [customKeyword, setCustomKeyword] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [editIndex, setEditIndex] = useState(null);
  const [appliedCombinationIndex, setAppliedCombinationIndex] = useState(null);
  const [progress, setProgress] = useState(0); // new state for progress

  useEffect(() => {
    const token = localStorage.getItem("token");
    const storedUser = JSON.parse(localStorage.getItem("user"));

    if (!token || !storedUser) {
      router.push("/auth/signin");
    } else {
      setIsLoggedIn(true);
      setUser(storedUser);
      fetchBrands(storedUser.id);
      fetchCombinations(storedUser.id);

      const savedState = JSON.parse(localStorage.getItem("keyword_state"));
      if (savedState) {
        setSelectedBrand(savedState.brand || "");
        setSelectedUrl(savedState.url || "");
        setDateRange(savedState.dateRange || { start: "", end: "" });
        setKeywords(savedState.keywords || []);
        setSavedCombination(savedState.savedCombination || []);
      }
    }
  }, []);

  useEffect(() => {
    const stateToPersist = {
      brand: selectedBrand,
      url: selectedUrl,
      dateRange,
      keywords,
      savedCombination,
    };
    localStorage.setItem("keyword_state", JSON.stringify(stateToPersist));
  }, [selectedBrand, selectedUrl, dateRange, keywords, savedCombination]);

  useEffect(() => {
    const brand = brands.find((b) => b.brand_name === selectedBrand);
    setAvailableUrls(brand?.websites || []);
  }, [selectedBrand, brands]);

  const fetchBrands = async (userId) => {
    const res = await fetch(`/api/brand/${userId}`);
    const data = await res.json();
    setBrands(data.brands || []);
  };

  const fetchCombinations = async (userId) => {
    const res = await fetch(`/api/keywords/get-combinations?user_id=${userId}`);
    const data = await res.json();
    if (data.success) setAllSavedCombinations(data.combinations || []);
  };

  const fetchStoredKeywords = async (language) => {
    if (!selectedBrand || !selectedUrl || !dateRange.start || !dateRange.end) {
      alert("Please fill all fields");
      return;
    }

    try {
      setLoading(true);
      setLoadingMessage(`Generating ${language.toUpperCase()} keywords...`);
      setProgress(10); // Start at 10%

      const res = await fetch(`/api/keywords/extract/${language}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: user.id, brand: selectedBrand, url: selectedUrl, language, dateRange }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message || "Failed extraction");

      if (Array.isArray(data.statusMessages)) {
        const totalSteps = data.statusMessages.length;
        for (let i = 0; i < totalSteps; i++) {
          setLoadingMessage(data.statusMessages[i]);
          setProgress(Math.floor(((i + 1) / totalSteps) * 100));
          await new Promise((res) => setTimeout(res, 700));  // animate step-by-step
        }
      }

      setKeywords(data.keywords?.slice(0, 20) || []);
      setLoadingMessage("Finalizing...");
      setProgress(100); // Done
      await new Promise((r) => setTimeout(r, 500));
    } catch (e) {
      console.error(e);
      setLoadingMessage("Error generating keywords.");
      setProgress(0);
    } finally {
      setLoading(false);
      setLoadingMessage("");
      setProgress(0); // reset
    }
  };

  const toggleKeyword = (kw) => {
    if (editIndex !== null) return;
    setSavedCombination((prev) => (prev.includes(kw) ? prev.filter((k) => k !== kw) : [...prev, kw]));
  };

  const removeKeyword = (kw) => {
    setKeywords((prev) => prev.filter((k) => k !== kw));
    setSavedCombination((prev) => prev.filter((k) => k !== kw));
  };

  const handleEditKeyword = (index) => {
    setEditIndex(index);
    setCustomKeyword(savedCombination[index]);
  };

  const saveEditedKeyword = () => {
    const updated = [...savedCombination];
    updated[editIndex] = customKeyword;
    setSavedCombination(updated);
    setEditIndex(null);
    setCustomKeyword("");
  };

  const handleAddCustom = () => {
    if (customKeyword.trim()) {
      setSavedCombination((prev) => [...prev, customKeyword.trim()]);
      setCustomKeyword("");
    }
  };

  const saveCombinationToDb = async () => {
    try {
      const payload = {
        user_id: user.id,
        brand: selectedBrand,
        url: selectedUrl,
        keywords: savedCombination,
        date: new Date().toISOString(),
      };

      const res = await fetch("/api/keywords/save-combination", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const result = await res.json();
      if (result.success) {
        setSavedToDb(true);
        fetchCombinations(user.id);
        setSavedCombination([]);
      }
    } catch (e) {
      console.error("Save failed:", e);
    }
  };

  const deleteCombination = async (id) => {
    const res = await fetch(`/api/keywords/delete-combination?id=${id}`, { method: "DELETE" });
    const data = await res.json();
    if (data.success) fetchCombinations(user.id);
  };

  const applyCombination = (keywords, index) => {
    localStorage.setItem("applied_keywords", JSON.stringify(keywords));
    setAppliedCombinationIndex(index);
    setSavedToDb(false);
  };

  if (!isLoggedIn) return null;

  return (
    <div className="bg-gray-100 min-h-screen">
          <Header activeTab={pathname} showFullNav={true} />
          <div className="max-w-6xl mx-auto py-10 px-6">
            {/* 🔷 Title */}
            <div className="bg-[#0B1F3F] text-white text-1xl font-bold p-4 rounded shadow-sm mb-6 text-left tracking-wide">
              KEYWORD MANAGEMENT
            </div>

            {/* 🔷 Top Description Section */}
            <div className="flex items-start bg-white p-6 shadow rounded-lg mb-6 border border-gray-200">
              <img
                src="/images/concept-keyword.jpg"
                alt="Keyword Management Illustration"
                className="w-60 h-60 object-contain mr-6"
              />

              <div className="bg-[#0B1F3F] border border-[#0B1F3F] text-white rounded-md p-6 flex-1 text-sm leading-relaxed font-sans">
                <p className="text-md">
                  This tool helps to <span className="font-semibold"> extract and organize meaningful keywords from customer content. </span>
                  Select, edit, remove and save keyword combinations to gain insights into brand sentiment, customer concerns, and trending topics — all in one place.
  
                </p>

                <div className="mt-4">
                  <h3 className="text-lg font-semibold mb-1">🧩 How to Use:</h3>
                  <ul className="list-decimal ml-5 space-y-1">
                    <li>Select your brand, website, and time period</li>
                    <li>Click <span className="italic">"Generate Sinhala"</span> or <span className="italic">"Generate English"</span> to extract keywords</li>
                    <li>Choose the keywords you want to save as a group <span className="text-sm italic">(you can also edit or add your own!)</span></li>
                    <li>Save your keyword group and use it for sentiment analysis</li>
                  </ul>
                </div>
              </div>
            </div>

        {/* 🔹 Input Form */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <label className="block font-semibold">Select Brand</label>
          <select value={selectedBrand} onChange={(e) => setSelectedBrand(e.target.value)} className="w-full border p-3 rounded-md shadow-sm">
            <option value="">Choose a Brand</option>
            {brands.map((b, idx) => <option key={idx} value={b.brand_name}>{b.brand_name}</option>)}
          </select>

          <label className="block mt-4 font-semibold">Website URL</label>
          <select value={selectedUrl} onChange={(e) => setSelectedUrl(e.target.value)} className="w-full border p-3 rounded-md shadow-sm">
            <option value="">Select a Website</option>
            {availableUrls.map((url, idx) => <option key={idx} value={url}>{url}</option>)}
          </select>

          <label className="block mt-4 font-semibold">Start Date</label>
          <input type="date" className="w-full border p-3 rounded-md" onChange={(e) => setDateRange((prev) => ({ ...prev, start: e.target.value }))} />

          <label className="block mt-4 font-semibold">End Date</label>
          <input type="date" className="w-full border p-3 rounded-md" onChange={(e) => setDateRange((prev) => ({ ...prev, end: e.target.value }))} />
        </div>

        {/* 🔹 Generate Buttons */}
        <div className="mt-4 flex justify-end gap-4">
          <button onClick={() => fetchStoredKeywords("sinhala")} className="bg-[#0B1F3F] text-white px-6 py-2 rounded-md">Generate Sinhala</button>
          <button onClick={() => fetchStoredKeywords("english")} className="bg-[#0B1F3F] text-white px-6 py-2 rounded-md">Generate English</button>
        </div>

        {/* 🔹 Loading Spinner */}
        {loading && (
          <div className="mt-4 bg-blue-100 text-blue-900 border-l-4 border-blue-500 rounded-md p-4 shadow">
            <p className="mb-2 font-medium">{loadingMessage}</p>
            <div className="w-full bg-blue-200 rounded-full h-3">
              <div
                className="bg-blue-700 h-3 rounded-full transition-all duration-500 ease-in-out"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        )}


        {/* 🔹 Extracted Keywords */}
        <div className="mt-6">
          <div className="bg-[#0B1F3F] text-white p-4 rounded-md font-semibold shadow-md">
            Extracted Keywords
          </div>

          <div className="bg-blue-100 border border-blue-300 text-blue-800 p-3 rounded-md mt-2 text-base font-medium flex items-center gap-2">
            💡 Select the keywords you’d like to include in your keyword combination.
          </div>

          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
            <div className="flex flex-wrap gap-3">
              {keywords.map((kw, i) => {
                const isSelected = savedCombination.includes(kw);
                return (
                  <div
                    key={i}
                    className={`relative flex items-center gap-2 px-5 py-2 rounded-lg shadow cursor-pointer transition-colors ${
                      isSelected
                        ? "bg-green-600 hover:bg-green-700"
                        : "bg-[#3B82F6] hover:bg-[#2563EB]"
                    }`}
                    onClick={() => toggleKeyword(kw)}
                  >
                    <span className="text-sm font-semibold tracking-wide text-white">{kw}</span>
                    <button
                      className="text-white hover:text-red-300 text-sm font-bold"
                      onClick={(e) => {
                        e.stopPropagation();
                        removeKeyword(kw);
                      }}
                    >
                      ×
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* 🔹 Saved Combination Section */}
        {/* 🔹 Saved Combination Title */}
        <div className="mt-6 bg-[#0B1F3F] text-white p-4 rounded-md font-semibold shadow-md">
          Saved Combination
        </div>

        {/* 🔹 Instruction Note */}
        <div className="bg-green-50 border border-green-300 text-green-800 p-3 rounded-md mt-2 text-base font-semibold">
          📝 Click a keyword to edit it. You can also add your own using the field below.
        </div>

        {/* 🔹 Saved Keywords List */}
        <div className="mt-4 flex flex-wrap gap-2">
          {savedCombination.map((kw, idx) => (
            <div
              key={idx}
              className="bg-green-600 text-white px-4 py-2 rounded shadow-md cursor-pointer"
            >
              {editIndex === idx ? (
                <>
                  <input
                    value={customKeyword}
                    onChange={(e) => setCustomKeyword(e.target.value)}
                    className="text-black rounded px-1"
                  />
                  <button onClick={saveEditedKeyword} className="ml-1 text-sm">
                    💾
                  </button>
                </>
              ) : (
                <span onClick={() => handleEditKeyword(idx)}>{kw}</span>
              )}
            </div>
          ))}
        </div>

        {/* 🔹 Custom Keyword Input */}
        <div className="mt-4 flex gap-2">
          <input
            type="text"
            value={customKeyword}
            onChange={(e) => setCustomKeyword(e.target.value)}
            placeholder="Add custom keyword"
            className="border p-2 rounded w-full"
          />
          <button
            onClick={handleAddCustom}
            className="bg-[#0B1F3F] text-white px-4 rounded"
          >
            Add
          </button>
        </div>

        {/* 🔹 Save Button with Animated State */}
        <div className="mt-4 flex justify-end gap-4">
          <button
            onClick={() => {
              saveCombinationToDb(); // ✅ your function
              setSavedToDb(true);     // ✅ trigger feedback
              setTimeout(() => setSavedToDb(false), 2000); // revert after 2s
            }}
            className={`px-6 py-3 rounded-md font-semibold transition-all duration-300 ease-in-out ${
              savedToDb
                ? "bg-green-500 text-white shadow-md"
                : "bg-[#0B1F3F] text-white hover:bg-[#1E3A8A]"
            }`}
          >
            {savedToDb ? "✅ Saved" : "💾 Save Combination"}
          </button>
        </div>

        {/* 🔹 All Saved Combinations */}
        <div className="mt-6 bg-[#0B1F3F] text-white p-4 rounded-md font-semibold shadow-md">All Saved Combinations</div>

        <div className="mt-4 space-y-4">
          {allSavedCombinations.map((combo, idx) => (
            <div
              key={idx}
              className={`bg-white rounded-md p-4 shadow-sm flex flex-wrap items-center gap-2 ${
                appliedCombinationIndex === idx ? "ring-2 ring-[#0B1F3F]" : ""
              }`}
            >
              {/* 🔹 Keyword tags */}
              {combo.keywords.map((word, i) => (
                <span
                  key={i}
                  className="bg-indigo-100 text-indigo-800 font-medium px-3 py-1 rounded-md text-sm shadow-sm"
                >
                  {word}
                </span>
              ))}

              {/* ✅ Apply Button */}
              <button
                onClick={() => {
                  localStorage.setItem("applied_keywords", JSON.stringify(combo.keywords));
                  setAppliedCombinationIndex(idx);
                  router.push("/aspectclassification");
                }}
                className={`ml-auto px-4 py-1 rounded font-medium shadow-sm ${
                  appliedCombinationIndex === idx
                    ? "bg-green-700 text-white"
                    : "bg-[#0B1F3F] text-white hover:bg-[#1c2e50]"
                } transition`}
              >
                {appliedCombinationIndex === idx ? "Applied" : "Apply"}
              </button>

              {/* 🗑️ Delete Button */}
              <button
                onClick={async () => {
                  const confirmed = confirm("Are you sure you want to delete this keyword group?");
                  if (!confirmed) return;

                  try {
                    const res = await fetch(`/api/keywords/save-combination?id=${combo._id}`, {
                      method: "DELETE",
                    });
                    const data = await res.json();

                    if (data.success) {
                      setAllSavedCombinations((prev) => prev.filter((_, i) => i !== idx));
                    } else {
                      alert("❌ Failed to delete combination.");
                    }
                  } catch (err) {
                    console.error("Delete error:", err);
                    alert("❌ An error occurred while deleting.");
                  }
                }}
                className="text-red-600 text-lg px-2 hover:text-red-800 transition"
                title="Delete Combination"
              >
                🗑️
              </button>
            </div>
          ))}
        </div>


      </div>
      <Footer />
    </div>
  );
}
