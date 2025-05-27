"use client";

import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Header from "@/app/components/Header";
import Footer from "@/app/components/Footer";

export default function SentimentAnalysis() {
    const [sentimentResults, setSentimentResults] = useState([]);
    const [aspectScores, setAspectScores] = useState({});
    const [selectedModel, setSelectedModel] = useState("english");
    const [searchQuery, setSearchQuery] = useState("");
    const [filter, setFilter] = useState("all");
    const [fromDate, setFromDate] = useState("");
    const [toDate, setToDate] = useState("");
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            router.push("/auth/signin");
        } else {
            setIsLoggedIn(true);
        }
    }, []);

    const fetchSentimentResults = async (language) => {
        try {
            const response = await fetch(`/api/fetch?language=${language}`);
            const json = await response.json();
            const data = json.data || [];
            setSentimentResults(data);
            calculateAspectScores(data);
        } catch (error) {
            console.error("Error fetching sentiment results:", error);
        }
    };

    const handleGenerateSentiments = async (language) => {
        const apiEndpoint = language === "english"
            ? "/api/sentiments/english"
            : "/api/sentiments/sinhala";

        const response = await fetch(apiEndpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });

        if (response.ok) {
            fetchSentimentResults(language);
        } else {
            console.error(`Error processing ${language} sentiment analysis`);
        }
    };

    // ✅ Fixed version with most frequent label as overall sentiment
    const calculateAspectScores = (data) => {
<<<<<<< HEAD
        if (!Array.isArray(data)) return;

        const aspectSentiments = {};
=======
        const aspectStats = {};
>>>>>>> d20d6d7450c5cdd2218a399775421983b46d0a1f

        data.forEach(({ aspect, sentiment_label, sentiment_score }) => {
            if (!aspectStats[aspect]) {
                aspectStats[aspect] = {
                    totalScore: 0,
                    count: 0,
                    labelCount: { Positive: 0, Neutral: 0, Negative: 0 }
                };
            }

            aspectStats[aspect].totalScore += sentiment_score;
            aspectStats[aspect].count += 1;
            aspectStats[aspect].labelCount[sentiment_label] += 1;
        });

<<<<<<< HEAD
        const aspectAverages = {};
        Object.keys(aspectSentiments).forEach(aspect => {
            const avgScore = (aspectSentiments[aspect].totalScore / aspectSentiments[aspect].count).toFixed(2);
            let sentimentLabel = "Neutral";
            if (avgScore >= 0.67) sentimentLabel = "Positive";
            else if (avgScore < 0.34) sentimentLabel = "Negative";

            aspectAverages[aspect] = { avgScore, sentimentLabel };
=======
        const finalAspectSummary = {};
        Object.entries(aspectStats).forEach(([aspect, stats]) => {
            const avgScore = (stats.totalScore / stats.count).toFixed(2);
            const mostFrequentLabel = Object.entries(stats.labelCount).reduce(
                (a, b) => (a[1] >= b[1] ? a : b)
            )[0];

            finalAspectSummary[aspect] = {
                avgScore,
                sentimentLabel: mostFrequentLabel
            };
>>>>>>> d20d6d7450c5cdd2218a399775421983b46d0a1f
        });

        setAspectScores(finalAspectSummary);
    };

<<<<<<< HEAD
    const filteredResults = Array.isArray(sentimentResults)
        ? sentimentResults.filter((item) => {
            const matchesFilter =
                filter === "all" ||
                (filter === "positive" && item.sentiment_label === "Positive") ||
                (filter === "negative" && item.sentiment_label === "Negative") ||
                (filter === "neutral" && item.sentiment_label === "Neutral");
            const matchesSearch = item.comment.toLowerCase().includes(searchQuery.toLowerCase());
            return matchesFilter && matchesSearch;
        })
        : [];
=======
    const filteredResults = sentimentResults.filter((item) => {
        const matchesFilter =
            filter === "all" ||
            (filter === "positive" && item.sentiment_label === "Positive") ||
            (filter === "negative" && item.sentiment_label === "Negative") ||
            (filter === "neutral" && item.sentiment_label === "Neutral");

        const matchesSearch = item.comment.toLowerCase().includes(searchQuery.toLowerCase());

        let matchesDate = true;
        if (fromDate) {
            matchesDate = matchesDate && new Date(item.date) >= new Date(fromDate);
        }
        if (toDate) {
            matchesDate = matchesDate && new Date(item.date) <= new Date(toDate);
        }

        return matchesFilter && matchesSearch && matchesDate;
    });
>>>>>>> d20d6d7450c5cdd2218a399775421983b46d0a1f

    if (!isLoggedIn) return null;

    return (
        <div className="bg-gray-100 min-h-screen">
            <Header activeTab={pathname} showFullNav={true} />
            <div className="max-w-6xl mx-auto py-10 px-6">
<<<<<<< HEAD
                
=======

                {/* CARD 1: Generate Sentiments */}
>>>>>>> d20d6d7450c5cdd2218a399775421983b46d0a1f
                <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold">
                    SENTIMENT ANALYSIS
                </div>
                <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
                    <div className="flex items-center space-x-4 justify-between">
                        <select
                            value={selectedModel}
                            onChange={(e) => setSelectedModel(e.target.value)}
                            className="flex-grow p-3 border rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 bg-white text-gray-800 cursor-pointer transition"
                            style={{ width: "250px" }}
                        >
                            <option value="english">English Model</option>
                            <option value="sinhala">Sinhala Model</option>
                        </select>
                        <button
                            onClick={() => handleGenerateSentiments("english")}
                            className="bg-[#0B1F3F] text-white px-6 py-3 rounded-md shadow-md hover:bg-[#092c66] transition duration-200"
                        >
                            Generate English Sentiments
                        </button>
                        <button
                            onClick={() => handleGenerateSentiments("sinhala")}
                            className="bg-[#0B1F3F] text-white px-6 py-3 rounded-md shadow-md hover:bg-[#092c66] transition duration-200"
                        >
                            Generate Sinhala Sentiments
                        </button>
                    </div>
                </div>

<<<<<<< HEAD
=======
                {/* CARD 2: Sentiment Results */}
>>>>>>> d20d6d7450c5cdd2218a399775421983b46d0a1f
                <div className="mt-4">
                    <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold">
                        SENTIMENT RESULTS
                    </div>

<<<<<<< HEAD
                    <div className="mt-6 mb-4 flex justify-between">
                        <input 
                            type="text" 
                            placeholder="Search comments..." 
                            value={searchQuery} 
                            onChange={(e) => setSearchQuery(e.target.value)} 
                            className="p-2 border rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 w-1/3"
                        />
                        <select 
                            value={filter} 
                            onChange={(e) => setFilter(e.target.value)} 
=======
                    {/* Filters */}
                    <div className="mt-6 mb-4 flex flex-wrap gap-4 justify-between">
                        <input
                            type="text"
                            placeholder="Search comments..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="p-2 border rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 w-1/3"
                        />
                        <select
                            value={filter}
                            onChange={(e) => setFilter(e.target.value)}
>>>>>>> d20d6d7450c5cdd2218a399775421983b46d0a1f
                            className="p-2 border rounded-lg shadow-sm bg-white text-gray-800 cursor-pointer transition w-1/3"
                        >
                            <option value="all">All Sentiments</option>
                            <option value="positive">Positive</option>
                            <option value="negative">Negative</option>
                            <option value="neutral">Neutral</option>
                        </select>
<<<<<<< HEAD
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow-md overflow-x-auto">
                        <div className="overflow-y-auto max-h-[400px] border border-gray-300 rounded-lg">
                            <table className="min-w-full border-collapse">
                                <thead>
                                    <tr className="bg-gray-200 text-left">
                                        <th className="border p-3">Comment</th>
                                        <th className="border p-3">Aspect</th>
                                        <th className="border p-3">Sentiment Label</th>
                                        <th className="border p-3">Sentiment Score</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredResults.map((item, index) => {
                                        const percentage = Math.round(item.sentiment_score * 100);
                                        return (
                                            <tr key={index} className="border-b hover:bg-gray-100 transition duration-200">
                                                <td className="border p-3">{item.comment}</td>
                                                <td className="border p-3">{item.aspect}</td>
                                                <td className={`border p-3 font-semibold ${
                                                    item.sentiment_label === "Positive" ? "text-red-500" :
                                                    item.sentiment_label === "Negative" ? "text-green-500" :
                                                    "text-gray-500"
                                                }`}>
                                                    {item.sentiment_label}
                                                </td>
                                                <td className="border p-3">
                                                    <div className="mb-1 font-semibold">
                                                        {item.sentiment_score.toFixed(2)} ({percentage}%)
                                                    </div>
                                                    <div className="h-5 bg-gray-300 rounded-md">
                                                        <div className={`h-5 rounded-md ${
                                                            item.sentiment_label === "Positive" ? "bg-red-500" :
                                                            item.sentiment_label === "Negative" ? "bg-green-500" :
                                                            "bg-gray-500"
                                                        }`} style={{ width: `${percentage}%` }}></div>
                                                    </div>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div className="mt-6">
                    <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold">
                        ASPECT DESCRIPTION
                    </div>
                    <div className="bg-white p-6 rounded-lg shadow-md">
                        <table className="min-w-full border border-gray-300 rounded-lg overflow-hidden">
                            <thead>
                                <tr className="bg-gray-200">
                                    <th className="border p-3 text-left">Aspect</th>
                                    <th className="border p-3 text-left">Overall Sentiment</th>
                                    <th className="border p-3 text-left">Avg Sentiment Score</th>
                                </tr>
                            </thead>
                            <tbody>
                                {Object.entries(aspectScores).map(([aspect, { avgScore, sentimentLabel }]) => {
                                    const sentimentColor = sentimentLabel === "Positive"
                                        ? "text-red-600 font-semibold"
                                        : sentimentLabel === "Negative"
                                        ? "text-green-600 font-semibold"
                                        : "text-gray-600 font-semibold";

                                    return (
                                        <tr key={aspect} className="border-b hover:bg-gray-100 transition duration-200">
                                            <td className="border p-3 font-semibold">{aspect}</td>
                                            <td className={`border p-3 ${sentimentColor}`}>
                                                {sentimentLabel}
                                            </td>
                                            <td className="border p-3 font-semibold">
                                                {avgScore}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
=======

                        <div className="flex gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">From</label>
                                <input
                                    type="date"
                                    value={fromDate}
                                    onChange={(e) => setFromDate(e.target.value)}
                                    className="p-2 border rounded-md shadow-sm"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">To</label>
                                <input
                                    type="date"
                                    value={toDate}
                                    onChange={(e) => setToDate(e.target.value)}
                                    className="p-2 border rounded-md shadow-sm"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Table */}
                    <div className="bg-white p-6 rounded-lg shadow-md overflow-x-auto">
                        <div className="overflow-y-auto max-h-[400px] border border-gray-300 rounded-lg">
                            <table className="min-w-full border-collapse">
                                <thead>
                                    <tr className="bg-gray-200 text-left">
                                        <th className="border p-3">Comment</th>
                                        <th className="border p-3">Aspect</th>
                                        <th className="border p-3">Sentiment Label</th>
                                        <th className="border p-3">Sentiment Score</th>
                                        <th className="border p-3">Date</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredResults.map((item, index) => {
                                        const percentage = Math.round(item.sentiment_score * 100);
                                        return (
                                            <tr key={index} className="border-b hover:bg-gray-100 transition duration-200">
                                                <td className="border p-3">{item.comment}</td>
                                                <td className="border p-3">{item.aspect}</td>
                                                <td className={`border p-3 font-semibold ${
                                                    item.sentiment_label === "Positive" ? "text-red-500" :
                                                    item.sentiment_label === "Negative" ? "text-green-500" :
                                                    "text-gray-500"
                                                }`}>
                                                    {item.sentiment_label}
                                                </td>
                                                <td className="border p-3">
                                                    <div className="mb-1 font-semibold">
                                                        {item.sentiment_score.toFixed(2)} ({percentage}%)
                                                    </div>
                                                    <div className="h-5 bg-gray-300 rounded-md">
                                                        <div className={`h-5 rounded-md ${
                                                            item.sentiment_label === "Positive" ? "bg-red-500" :
                                                            item.sentiment_label === "Negative" ? "bg-green-500" :
                                                            "bg-gray-500"
                                                        }`} style={{ width: `${percentage}%` }}></div>
                                                    </div>
                                                </td>
                                                <td className="border p-3">
                                                    {item.date ? new Date(item.date).toLocaleDateString("en-GB") : "N/A"}
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                {/* CARD 3: Aspect Summary */}
                <div className="mt-6">
                    <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold">
                        ASPECT DESCRIPTION
                    </div>
                    <div className="bg-white p-6 rounded-lg shadow-md">
                        <table className="min-w-full border border-gray-300 rounded-lg overflow-hidden">
                            <thead>
                                <tr className="bg-gray-200">
                                    <th className="border p-3 text-left">Aspect</th>
                                    <th className="border p-3 text-left">Overall Sentiment</th>
                                    <th className="border p-3 text-left">Avg Sentiment Score</th>
                                </tr>
                            </thead>
                            <tbody>
                                {Object.entries(aspectScores).map(([aspect, { avgScore, sentimentLabel }]) => {
                                    const sentimentColor = sentimentLabel === "Positive"
                                        ? "text-red-600 font-semibold"
                                        : sentimentLabel === "Negative"
                                        ? "text-green-600 font-semibold"
                                        : "text-gray-600 font-semibold";
>>>>>>> d20d6d7450c5cdd2218a399775421983b46d0a1f

                                    return (
                                        <tr key={aspect} className="border-b hover:bg-gray-100 transition duration-200">
                                            <td className="border p-3 font-semibold">{aspect}</td>
                                            <td className={`border p-3 ${sentimentColor}`}>
                                                {sentimentLabel}
                                            </td>
                                            <td className="border p-3 font-semibold">
                                                {avgScore}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <Footer />
        </div>
    );
}
