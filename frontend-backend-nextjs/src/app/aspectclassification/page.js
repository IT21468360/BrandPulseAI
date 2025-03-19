"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Header from "@/app/components/Header";
import Footer from "@/app/components/Footer";

export default function AspectClassification() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [aspects, setAspects] = useState([]);
    const [showComments, setShowComments] = useState(false); // Controls visibility of comments
    const router = useRouter();

    // Check for authentication on page load
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            router.push("/auth/signin"); // Redirect to sign-in page if not logged in
        } else {
            setIsLoggedIn(true);
        }
    }, []);

    // Fetch aspect classification data
    const fetchAspects = async () => {
        try {
            const res = await fetch("/api/aspects");
            const data = await res.json();
            setAspects(data);
            setShowComments(true); // Show comments only after button click
        } catch (error) {
            console.error("Error fetching aspects:", error);
        }
    };

    if (!isLoggedIn) return null;

    return (
        <div className="bg-gray-100 min-h-screen">
            <Header />

            {/* Page Content */}
            <div className="max-w-6xl mx-auto py-10 px-6">
                {/* Title Section */}
                <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold shadow-md">
                    ASPECT-BASED SENTIMENT ANALYSIS
                </div>

                {/* Generate Comments Button */}
                <div className="mt-6 bg-white p-6 rounded-lg shadow-lg flex justify-center">
                    <button 
                        onClick={fetchAspects}
                        className="bg-[#0B1F3F] text-white px-10 py-3 rounded-md shadow-md hover:bg-[#092043] transition"
                    >
                        Generate English Comments
                    </button>
                </div>

                {/* Comments by Aspect (Only Visible After Button Click) */}
                {showComments && (
                    <div className="mt-6 bg-white p-6 rounded-lg shadow-lg">
                        <h2 className="text-lg font-semibold mb-4 text-[#0B1F3F]">Aspect-wise Comments</h2>
                        {aspects.length === 0 ? (
                            <p className="text-gray-500">Loading comments...</p>
                        ) : (
                            aspects.map(aspect => (
                                <div key={aspect._id} className="mb-6 p-4 border rounded-lg bg-gray-50 shadow-md">
                                    <h3 className="text-lg font-semibold text-[#0B1F3F] mb-2">{aspect._id}</h3>
                                    <ul className="list-disc pl-6 space-y-2">
                                        {aspect.comments.map((comment, index) => (
                                            <li key={index} className="bg-white px-4 py-2 rounded-lg shadow-sm border text-gray-700">
                                                {comment}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>

            <Footer />
        </div>
    );
}
