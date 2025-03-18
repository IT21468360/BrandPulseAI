"use client";

import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Header from "@/app/components/Header";
import Footer from "@/app/components/Footer";

export default function SentimentAnalysis() {
    const [sentimentResults, setSentimentResults] = useState([]);
    const [selectedModel, setSelectedModel] = useState("english");
    const [searchQuery, setSearchQuery] = useState("");
    const [filter, setFilter] = useState("all");
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const router = useRouter();
    const pathname = usePathname();

    // ✅ Check if user is logged in
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            router.push("/auth/signin");
        } else {
            setIsLoggedIn(true);
            fetchSentimentResults(selectedModel); // Fetch sentiment data initially
        }
    }, []);

    // ✅ Fetch Sentiment Results Based on Selected Language
    const fetchSentimentResults = async (language) => {
        try {
            const response = await fetch(`/api/fetch?language=${language}`);
            const data = await response.json();
            setSentimentResults(data);
        } catch (error) {
            console.error("Error fetching sentiment results:", error);
        }
    };

    // ✅ Handle Sentiment Analysis for English & Sinhala
    const handleGenerateSentiments = async (language) => {
        const apiEndpoint = language === "english"
            ? "/api/sentiments/english"
            : "/api/sentiments/sinhala";

        const response = await fetch(apiEndpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });

        if (response.ok) {
            fetchSentimentResults(language); // ✅ Fetch results after processing
        } else {
            console.error(`Error processing ${language} sentiment analysis`);
        }
    };

    // ✅ Filter & Search Functionality
    const filteredResults = sentimentResults.filter((item) => {
        const matchesFilter =
            filter === "all" ||
            (filter === "positive" && item.sentiment_label === "Positive") ||
            (filter === "negative" && item.sentiment_label === "Negative");
        const matchesSearch = item.comment.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesFilter && matchesSearch;
    });

    if (!isLoggedIn) return null;

    return (
        <div className="bg-gray-100 min-h-screen">
            <Header activeTab={pathname} showFullNav={true} />
            <div className="max-w-6xl mx-auto py-10 px-6">
                
                {/* ✅ Page Title */}
                <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold">
                    SENTIMENT ANALYSIS
                </div>

                {/* ✅ Dropdown (Only for Display) & Generate Buttons */}
                <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
                    <div className="flex items-center space-x-4 justify-between">
                        <select
                            value={selectedModel}
                            onChange={(e) => setSelectedModel(e.target.value)}
                            className="flex-grow p-3 border rounded-md shadow-lg focus:border-blue-500 focus:outline-none"
                        >
                            <option value="english">English Model</option>
                            <option value="sinhala">Sinhala Model</option>
                        </select>
                        <button
                            onClick={() => handleGenerateSentiments("english")}
                            className="bg-[#0B1F3F] text-white px-6 py-3 rounded-md shadow-md"
                        >
                            Generate English Sentiments
                        </button>
                        <button
                            onClick={() => handleGenerateSentiments("sinhala")}
                            className="bg-[#0B1F3F] text-white px-6 py-3 rounded-md shadow-md"
                        >
                            Generate Sinhala Sentiments
                        </button>
                    </div>
                </div>

                {/* ✅ Sentiment Results Section */}
                <div className="mt-6">
                    <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold">
                        SENTIMENT RESULTS
                    </div>
                    <div className="bg-white p-6 rounded-lg shadow-md">
                        
                        {/* ✅ Search Bar & Filter */}
                        <div className="flex items-center justify-between mb-4">
                            <input 
                                type="text" 
                                placeholder="Search comments..." 
                                value={searchQuery} 
                                onChange={(e) => setSearchQuery(e.target.value)} 
                                className="p-2 border rounded-md flex-grow"
                            />
                            <select 
                                value={filter} 
                                onChange={(e) => setFilter(e.target.value)} 
                                className="ml-4 p-2 border rounded-md"
                            >
                                <option value="all">All</option>
                                <option value="positive">Positive</option>
                                <option value="negative">Negative</option>
                            </select>
                        </div>

                        {/* ✅ Sentiment Results Table */}
                        <table className="min-w-full border-collapse border border-gray-300">
                            <thead>
                                <tr className="bg-gray-200">
                                    <th className="border p-2">Comment</th>
                                    <th className="border p-2">Aspect</th>
                                    <th className="border p-2">Sentiment Score</th>
                                    <th className="border p-2">Sentiment Label</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredResults.length > 0 ? (
                                    filteredResults.map((item, index) => (
                                        <tr key={index} className="border-b">
                                            <td className="border p-2">{item.comment}</td>
                                            <td className="border p-2">{item.aspect}</td>
                                            <td className="border p-2">{item.sentiment_score.toFixed(2)}</td>
                                            <td className="border p-2">{item.sentiment_label}</td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan="4" className="p-4 text-center">No sentiment data available.</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <Footer />
        </div>
    );
}
