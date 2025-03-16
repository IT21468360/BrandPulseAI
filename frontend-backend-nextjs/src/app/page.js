"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Header from "./components/Header";
import Footer from "./components/Footer";

export default function LandingPage() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      setIsLoggedIn(true);
    }
  }, []);

  const handleGetStarted = () => {
    if (isLoggedIn) {
      router.push("/brandregistration"); // Redirect to Brand Registration if logged in
    } else {
      router.push("/auth/signin"); // Redirect to Sign In if not logged in
    }
  };

  return (
    <div className="bg-white">
      <Header />
      <div className="relative isolate px-6 lg:px-8 mt-6">
        <div className="mx-auto max-w-7xl py-10 sm:py-14 lg:py-18 grid md:grid-cols-2 gap-6 items-center">
          <div className="text-left">
            <h2 className="text-blue-900 text-sm font-semibold uppercase">
              MASTER KEYWORDS, UNDERSTAND SENTIMENTS, DELIVER TRANSPARENCY
            </h2>
            <h1 className="mt-2 text-5xl font-extrabold tracking-tight text-gray-900 sm:text-6xl">
              Empower Your Brand, Shape Your Reputation
            </h1>
            <p className="mt-3 text-lg text-gray-700">
              Harness the power of cutting-edge Brand Reputation Management. We
              specialize in Keywords Analysis, Sentiment Analysis, and
              Explainability to ensure transparency and trust in decision-making.
            </p>
            <p className="mt-2 text-lg text-gray-700">
              Our expertise spans English, Sinhala, and Sinhala-English mixed
              content, providing insights from social media, websites, and more.
            </p>
            <button
              onClick={handleGetStarted}
              className="mt-5 bg-[#0B1F3F] hover:bg-[#09172E] px-8 py-4 text-white font-semibold text-xl rounded-md shadow-md"
            >
              Get Started
            </button>
          </div>
          <div className="relative flex justify-center">
            <img
              src="/images/landingPg.png"
              alt="SentimentIQ Dashboard"
              className="w-full max-w-4xl"
            />
          </div>
        </div>
      </div>
      <Footer className="mt-0" />
    </div>
  );
}
