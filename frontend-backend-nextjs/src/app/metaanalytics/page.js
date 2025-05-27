"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Header from "@/app/components/Header";
import Footer from "@/app/components/Footer";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  LineChart,
  Line,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

export default function MetaAnalytics() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [videoData, setVideoData] = useState([]);
  const [loading, setLoading] = useState(true);
  const brand = "BoC"; // 🔒 Static brand (or replace with dynamic logic)
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/auth/signin");
    } else {
      setIsLoggedIn(true);
      fetchMetaData();
    }
  }, []);

  const fetchMetaData = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/youtube/meta?brand=${encodeURIComponent(brand)}`);
      const data = await res.json();
      setVideoData(data);
    } catch (error) {
      console.error("❌ Error fetching video meta:", error);
    } finally {
      setLoading(false);
    }
  };

  if (!isLoggedIn) return null;

  const viewsChart = videoData.map((v) => ({
    name: v.title?.slice(0, 20) + "...",
    views: parseInt(v.views || 0),
    likes: parseInt(v.likes || 0),
  }));

  const uploadsChart = (() => {
    const byDay = {};
    videoData.forEach((v) => {
      const d = new Date(v.published_at).toLocaleDateString();
      byDay[d] = (byDay[d] || 0) + 1;
    });
    return Object.entries(byDay).map(([day, count]) => ({ day, count }));
  })();

  return (
    <div className="bg-gray-100 min-h-screen">
      <Header />

      <div className="max-w-6xl mx-auto py-10 px-6">
        <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold shadow-md">
          YOUTUBE META DATA DASHBOARD
        </div>

        {/* 🔹 Brand Info */}
        <p className="mt-6 text-gray-600">
          Showing results for: <span className="font-semibold text-black">{brand}</span>
        </p>

        {/* 🔄 Loader */}
        {loading && <div className="mt-6 text-gray-600">Loading metadata...</div>}

        {/* 📊 Charts */}
        {!loading && videoData.length > 0 && (
          <>
            {/* Views & Likes */}
            <div className="mt-10 bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-lg font-bold mb-4">Engagement by Video</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={viewsChart}>
                  <XAxis dataKey="name" hide />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="views" fill="#3182CE" />
                  <Bar dataKey="likes" fill="#38A169" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Upload Trends */}
            <div className="mt-10 bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-lg font-bold mb-4">Upload Activity Over Time</h2>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={uploadsChart}>
                  <XAxis dataKey="day" />
                  <YAxis />
                  <CartesianGrid stroke="#eee" strokeDasharray="5 5" />
                  <Tooltip />
                  <Line type="monotone" dataKey="count" stroke="#0B1F3F" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </>
        )}

        {/* 📋 Table */}
        {!loading && videoData.length > 0 && (
          <div className="mt-10 bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-lg font-bold mb-4">Video Details</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm text-left border">
                <thead className="bg-gray-100 text-gray-700 font-semibold">
                  <tr>
                    <th className="p-2">Title</th>
                    <th className="p-2">Hashtags</th>
                    <th className="p-2">Views</th>
                    <th className="p-2">Likes</th>
                    <th className="p-2">Published</th>
                  </tr>
                </thead>
                <tbody>
                  {videoData.map((v, i) => (
                    <tr key={i} className="border-b">
                      <td className="p-2">{v.title}</td>
                      <td className="p-2 text-blue-600">{v.hashtags}</td>
                      <td className="p-2">{Number(v.views || 0).toLocaleString()}</td>
                      <td className="p-2">{Number(v.likes || 0).toLocaleString()}</td>
                      <td className="p-2">{new Date(v.published_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
}
