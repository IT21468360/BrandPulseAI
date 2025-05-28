"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Header from "@/app/components/Header";
import Footer from "@/app/components/Footer";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

export default function AspectClassification() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [aspects, setAspects] = useState({ English: [], Sinhala: [] });
    const [brandInfo, setBrandInfo] = useState({ brand: "", keywords: [], scrape_id: "" });
    const [showComments, setShowComments] = useState(false);
    const [expanded, setExpanded] = useState({});
    const [startDate, setStartDate] = useState(null);
    const [endDate, setEndDate] = useState(null);
    const [appliedKeywords, setAppliedKeywords] = useState([]);
    const [loading, setLoading] = useState(false);
    const router = useRouter();

    // 🔐 Keep login alive on refresh
    useEffect(() => {
        const token = localStorage.getItem("token");

        // ✅ Only set a demo token if it's missing
        if (!token) {
            localStorage.setItem("token", "demo-token-123");
        }

        setIsLoggedIn(true); // trust localStorage presence
    }, []);



    // ✅ Load applied keywords
    useEffect(() => {
        const stored = localStorage.getItem("applied_keywords");
        if (stored) {
            setAppliedKeywords(JSON.parse(stored));
        }
    }, []);

    // ✅ Load scraped data from localStorage
    useEffect(() => {
        const storedBrand = localStorage.getItem("brand_info");
        const storedAspects = localStorage.getItem("aspects");
        if (storedBrand && storedAspects) {
            setBrandInfo(JSON.parse(storedBrand));
            setAspects(JSON.parse(storedAspects));
            setShowComments(true);
        }
    }, []);

    const fetchAspects = async (brandName, keywordsArray, scrapeId) => {
        try {
            const token = localStorage.getItem("token");
            const res = await fetch(
                `http://localhost:8000/api/results/aspects?brand=${encodeURIComponent(brandName)}&scrape_id=${encodeURIComponent(scrapeId)}`,
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );
            const data = await res.json();

            setAspects({ English: data.English, Sinhala: data.Sinhala });
            setBrandInfo({ brand: brandName, keywords: keywordsArray, scrape_id: scrapeId });
            setShowComments(true);

            // ✅ Save to localStorage
            localStorage.setItem("brand_info", JSON.stringify({ brand: brandName, keywords: keywordsArray, scrape_id: scrapeId }));
            localStorage.setItem("aspects", JSON.stringify({ English: data.English, Sinhala: data.Sinhala }));

            setTimeout(() => window.scrollTo({ top: 700, behavior: "smooth" }), 300);
        } catch (error) {
            console.error("❌ Error fetching aspects:", error);
            alert("❌ Failed to load comments.");
        } finally {
            setLoading(false);
        }
    };

    const triggerScraping = async () => {
        if (!startDate || !endDate) {
            alert("⚠️ Please select both start and end dates.");
            return;
        }

        try {
            setLoading(true);

            // ✅ Clear previous session data
            localStorage.removeItem("brand_info");
            localStorage.removeItem("aspects");

            const res = await fetch(
                `http://localhost:8000/api/aspect/scrape?start_date=${startDate.toISOString().split("T")[0]}&end_date=${endDate.toISOString().split("T")[0]}`,
                { method: "GET" }
            );

            const data = await res.json();

            if (data.status === "success") {
                if (data.brand && data.keywords && data.scrape_id) {
                    fetchAspects(data.brand, data.keywords, data.scrape_id);
                } else {
                    alert("⚠️ Missing data in response.");
                }
            } else {
                alert("❌ Scraping failed.");
            }
        } catch (error) {
            console.error("❌ Scraping error:", error);
            alert("❌ Scraping crashed.");
        } finally {
            setLoading(false);
        }
    };

    const toggleExpand = (lang, index) => {
        setExpanded((prev) => ({
            ...prev,
            [`${lang}-${index}`]: !prev[`${lang}-${index}`],
        }));
    };

    if (!isLoggedIn) return null;

    return (
        <div className="relative bg-gray-100 min-h-screen">
            {loading && (
                <>
                    <div className="fixed top-0 left-0 right-0 z-50">
                        <div className="h-1 w-full bg-indigo-200">
                            <div className="h-1 bg-indigo-600 animate-pulse w-1/2 mx-auto rounded" />
                        </div>
                    </div>
                    <div className="fixed inset-0 bg-white bg-opacity-60 backdrop-blur-sm flex justify-center items-center z-40">
                        <div className="flex flex-col items-center">
                            <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-indigo-600 border-opacity-70" />
                            <p className="mt-4 text-indigo-700 font-semibold">Scraping in progress...</p>
                        </div>
                    </div>
                </>
            )}

            <Header />

            {/* 🌈 Hero Section */}
            <div className="relative overflow-hidden bg-gradient-to-r from-indigo-50 via-white to-indigo-50 py-14 px-6 text-center rounded-b-md shadow-sm">
                <div className="absolute top-4 left-4 text-[80px] text-yellow-400 opacity-10 animate-bounce">🧠</div>
                <div className="absolute bottom-4 right-6 text-[80px] text-purple-400 opacity-10 animate-pulse">📊</div>
                <h1 className="text-3xl md:text-4xl font-extrabold text-[#0B1F3F] relative z-10">
                    🔍 Analyze Customer Feedback Like a Pro
                </h1>
                <p className="mt-3 text-gray-700 text-md md:text-lg max-w-2xl mx-auto relative z-10">
                    Scrape, classify, and explore YouTube comments with powerful aspect-based sentiment insights.
                    Gain clarity and confidence in your brand analysis in just a few clicks!
                </p>
            </div>

            <div className="max-w-6xl mx-auto py-10 px-6">
                {/* 📅 Date Pickers */}
                <div className="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center space-y-6">
                    <div className="flex flex-wrap justify-center gap-10">
                        <div className="flex flex-col items-start">
                            <label className="text-sm text-gray-700 font-semibold mb-1">Start Date:</label>
                            <DatePicker
                                selected={startDate}
                                onChange={(date) => setStartDate(date)}
                                dateFormat="yyyy-MM-dd"
                                placeholderText="Select start date"
                                className="border px-3 py-2 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                maxDate={new Date()}
                                showMonthDropdown
                                showYearDropdown
                                dropdownMode="select"
                            />
                        </div>
                        <div className="flex flex-col items-start">
                            <label className="text-sm text-gray-700 font-semibold mb-1">End Date:</label>
                            <DatePicker
                                selected={endDate}
                                onChange={(date) => setEndDate(date)}
                                dateFormat="yyyy-MM-dd"
                                placeholderText="Select end date"
                                className="border px-3 py-2 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                maxDate={new Date()}
                                showMonthDropdown
                                showYearDropdown
                                dropdownMode="select"
                            />
                        </div>
                    </div>

                    <button
                        onClick={triggerScraping}
                        className="bg-green-600 text-white px-10 py-3 rounded-md shadow-md hover:bg-green-700 transition flex items-center space-x-2"
                    >
                        <span>🔄</span> <span>Scrape & Classify YouTube Comments</span>
                    </button>
                </div>

                {/* 🔑 Applied Keywords */}
                {appliedKeywords.length > 0 && (
                    <div className="mt-4 mb-4 p-4 bg-indigo-100 border-l-4 border-indigo-500 text-indigo-900 rounded-md">
                        <strong>Applied Keywords:</strong>{" "}
                        {appliedKeywords.map((kw, i) => (
                            <span
                                key={i}
                                className="inline-block bg-indigo-200 text-indigo-800 px-3 py-1 rounded-full text-sm mr-2 mb-1"
                            >
                                {kw}
                            </span>
                        ))}
                    </div>
                )}

                {/* 🏷️ Brand Info Card */}
                {brandInfo.brand && (
                    <>
                        <div className="relative bg-white border border-yellow-300 shadow-md p-6 mt-10 max-w-3xl mx-auto rounded-lg text-sm">
                            <div className="absolute top-2 right-3 text-3xl opacity-10">📁</div>
                            <div className="space-y-3 text-gray-800">
                                <div className="flex items-center gap-2">
                                    <span className="text-yellow-600">🏢</span>
                                    <strong>Brand:</strong> {brandInfo.brand}
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className="text-yellow-600">🔑</span>
                                    <strong>Keywords:</strong> {brandInfo.keywords.join(", ")}
                                </div>
                                {startDate && endDate && (
                                    <div className="flex items-center gap-2">
                                        <span className="text-yellow-600">📅</span>
                                        <strong>Date Range:</strong>{" "}
                                        {startDate.toISOString().split("T")[0]} to {endDate.toISOString().split("T")[0]}
                                    </div>
                                )}
                                <div className="flex items-center gap-2">
                                    <span className="text-yellow-600">🆔</span>
                                    <strong>Scrape ID:</strong> {brandInfo.scrape_id}
                                </div>
                            </div>
                        </div>

                        {/* 🚀 Sentiment Analysis Button */}
                        <div className="text-center mt-6">
                            <a
                                href="/sentimentanalysis"
                                className="inline-block bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-3 rounded-lg shadow transition"
                            >
                                📊 Go to Sentiment Analysis Dashboard
                            </a>
                        </div>
                    </>
                )}

                {/* 💬 Comment Tables */}
                {showComments && (
                    <div className="mt-8">
                        {["English", "Sinhala"].map((lang) => (
                            <div key={lang} className="mb-10">
                                <h2 className="text-xl font-bold text-[#0B1F3F] mb-4">
                                    {lang} Aspect Classification
                                </h2>

                                {aspects[lang].length === 0 ? (
                                    <p className="text-gray-500">No {lang.toLowerCase()} comments found.</p>
                                ) : (
                                    aspects[lang].map((aspect, index) => (
                                        <div
                                            key={`${lang}-${index}`}
                                            className="mb-4 border rounded-lg bg-white shadow-sm overflow-hidden"
                                        >
                                            <button
                                                onClick={() => toggleExpand(lang, index)}
                                                className="w-full text-left p-4 bg-[#0B1F3F] text-white font-semibold hover:bg-[#092043] transition flex justify-between"
                                            >
                                                <span>{aspect._id}</span>
                                                <span className="ml-4 inline-block text-sm bg-yellow-200 text-yellow-800 px-2 py-0.5 rounded-full">
                                                    💬 {aspect.comments.length} comments
                                                </span>
                                            </button>

                                            {expanded[`${lang}-${index}`] && (
                                                <div className="p-4">
                                                    <div className="max-h-[300px] overflow-y-auto">
                                                        <table className="min-w-full text-sm">
                                                            <thead>
                                                                <tr className="bg-gray-50 text-left text-gray-700 font-semibold">
                                                                    <th className="p-2">🔢 #</th>
                                                                    <th className="p-2">💬 Comment</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody>
                                                                {aspect.comments.map((comment, idx) => (
                                                                    <tr key={idx} className="border-b">
                                                                        <td className="p-2 text-gray-600">{idx + 1}</td>
                                                                        <td className="p-2 text-gray-800">{comment}</td>
                                                                    </tr>
                                                                ))}
                                                            </tbody>
                                                        </table>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    ))
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <Footer />
        </div>
    );
}
