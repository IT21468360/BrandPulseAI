"use client";

import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";

import Header from "@/app/components/Header";
import Footer from "@/app/components/Footer";
import Image from "next/image";

export default function AspectWiseExplainability() {
    return (
        <div className="bg-gray-100 min-h-screen">
            <Header activeTab="/explainability/aspect-wise" showFullNav={true} />

            <div className="max-w-6xl mx-auto py-10 px-6">
                {/* Title */}
                <div className="bg-white p-6 rounded-lg shadow-md">
                <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold">
                Aspect-Based Explainability & Report
                        </div>
                    <p className="text-gray-700">
                        Aspect-Based Sentiment Analysis (ABSA) helps identify sentiment towards specific aspects of a service or product.  
                        This report presents a breakdown of sentiments across different aspects, helping to pinpoint strengths and areas needing improvement.
                    </p>
                </div>

                {/* PDF Report Display */}
                <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
                <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold">
                Aspect-Based Sentiment Report
                        </div>
                    <iframe
                        src="/reports/sentiment_analysis_report.html"
                        width="100%"
                        height="600px"
                        className="rounded-lg border shadow-md"
                    ></iframe>
                </div>

                {/* Aspect-Based Sentiment Distribution Graph */}
                <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
                <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold">
                Aspect-Based Sentiment Distribution
                        </div>
                    <p className="text-gray-700 mb-4">
                        This graph illustrates the distribution of positive, negative, and neutral sentiments across different aspects.
                        It helps to visualize which areas customers feel most positively or negatively about.
                    </p>
                    <Image
                        src="/images/aspect-sentiment-distribution.png"
                        alt="Aspect-Based Sentiment Distribution Graph"
                        width={700}
                        height={400}
                        className="rounded-lg"
                    />
                </div>

                {/* Average Likes by Aspect and Sentiment */}
                <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
                <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold">
                Average Likes by Aspect and Sentiment
                        </div>
                    <p className="text-gray-700 mb-4">
                        This graph shows the average number of likes for reviews categorized by aspect and sentiment.  
                        More likes on a particular sentiment indicate stronger public agreement with the expressed sentiment.
                    </p>
                    <Image
                        src="/images/average-likes-sentiment.png"
                        alt="Average Likes by Aspect and Sentiment Graph"
                        width={700}
                        height={400}
                        className="rounded-lg"
                    />
                </div>

                {/* Negative Word Cloud */}
                <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
                <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold">
                Negative Word Cloud
                        </div>
                    <p className="text-gray-700 mb-4">
                        The word cloud visualizes the most frequently occurring negative words in customer feedback.
                        Larger words indicate more frequently mentioned negative terms.
                    </p>
                    <Image
                        src="/images/negative-word-cloud.png"
                        alt="Negative Word Cloud"
                        width={600}
                        height={400}
                        className="rounded-lg"
                    />
                </div>

                {/* Positive Word Cloud */}
                <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
                <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold">
                Positive Word Cloud
                        </div>
                    <p className="text-gray-700 mb-4">
                        The positive word cloud represents the most commonly mentioned words in positive customer reviews.
                        It highlights the key strengths of the service based on customer feedback.
                    </p>
                    <Image
                        src="/images/positive-word-cloud.png"
                        alt="Positive Word Cloud"
                        width={600}
                        height={400}
                        className="rounded-lg"
                    />
                </div>

                {/* Download Report Button */}
                <div className="mt-6 bg-white p-6 rounded-lg shadow-md flex justify-center">
                    <a 
                        href="/reports/FULL_sentiment_analysis_report.html" 
                        download 
                        className="bg-blue-500 text-white font-semibold px-6 py-3 rounded-md shadow-md hover:bg-blue-700"
                    >
                        Download This Overall Report
                    </a>
                </div>
            </div>

            <Footer />
        </div>
    );
}
