"use client";

import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "@/app/context/AuthContext";
import Header from "@/app/components/Header";
import Footer from "@/app/components/Footer";

export default function BrandRegistration() {
  const { user, token } = useAuth(); // Get user data from context
  const router = useRouter();
  const pathname = usePathname();

  const [formData, setFormData] = useState({
    brand_name: "",
    industry: "",
    website: "",
    address: "",
    phone: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Check login status
  useEffect(() => {
    if (!token || !user) {
      router.push("/auth/signin"); // Redirect if not logged in
    }
  }, [token, user]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleRegisterBrand = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (!user?.id) {
      setError("User ID is missing. Please log in again.");
      setLoading(false);
      return;
    }

    const requestData = {
      user_id: user.id, // Correctly retrieve user_id
      ...formData,
    };

    console.log("📤 Sending request data:", requestData);

    const res = await fetch("/api/brand/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestData),
    });

    const data = await res.json();
    console.log("📥 API Response:", data);

    if (!res.ok) {
      setError(data.message);
      setLoading(false);
      return;
    }

    setSuccess(true);
    setTimeout(() => router.push("/keywordmanagement"), 2000);
  };

  const handleProceed = () => {
    router.push("/keywordmanagement");
  };

  if (!token || !user) return null;

  return (
    <div className="flex min-h-screen items-center justify-center bg-white dark:bg-gray-900 px-4 sm:px-6 lg:px-8">
      <div className="flex w-full max-w-4xl bg-white shadow-2xl text-[#0B1F3F] dark:bg-white dark:text-gray-900 rounded-lg shadow-lg overflow-hidden">
        {/* Left Side - Image & Brand Reputation Info */}
        <div className="hidden md:flex md:w-1/2 flex-col items-center justify-center p-8">
          <img
            src="/images/brandr.jpg"
            alt="Brand Registration"
            className="w-[400px] h-[350px] object-cover"
          />
          <div className="mt-6 text-center">
            <h3 className="text-xl font-semibold text-[#0B1F3F]">
              Why Brand Reputation Matters ?
            </h3>
            <p className="mt-2 text-sm text-gray-600">
              Your brand’s reputation influences trust, customer loyalty, and business growth. 
              Monitor, analyze, and enhance your brand image with AI-driven insights.
            </p>
          </div>
        </div>

        {/* Right Side - Form */}
        <div className="w-full md:w-1/2 p-10 space-y-6">
          <h2 className="text-center text-3xl font-bold">Register Your Brand</h2>
          <p className="text-center text-gray-600">
            Enter your brand details to start managing its reputation.
          </p>

          {error && <div className="text-red-500 text-sm text-center">{error}</div>}
          {success && (
            <div className="text-green-500 text-sm text-center">
              Brand registered successfully! Redirecting...
            </div>
          )}

          <form onSubmit={handleRegisterBrand} className="space-y-4">
            <div>
              <label className="block text-sm font-medium">Brand Name</label>
              <input
                type="text"
                name="brand_name"
                required
                value={formData.brand_name}
                onChange={handleChange}
                className="mt-2 block w-full rounded-md px-3 py-2 border border-gray-300 shadow-md focus:border-blue-700 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium">Industry</label>
              <input
                type="text"
                name="industry"
                required
                value={formData.industry}
                onChange={handleChange}
                className="mt-2 block w-full rounded-md px-3 py-2 border border-gray-300 shadow-md focus:border-blue-700 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium">Website URL</label>
              <input
                type="url"
                name="website"
                required
                value={formData.website}
                onChange={handleChange}
                className="mt-2 block w-full rounded-md px-3 py-2 border border-gray-300 shadow-md focus:border-blue-700 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium">Address</label>
              <input
                type="text"
                name="address"
                required
                value={formData.address}
                onChange={handleChange}
                className="mt-2 block w-full rounded-md px-3 py-2 border border-gray-300 shadow-md focus:border-blue-700 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium">Phone Number</label>
              <input
                type="text"
                name="phone"
                required
                value={formData.phone}
                onChange={handleChange}
                className="mt-2 block w-full rounded-md px-3 py-2 border border-gray-300 shadow-md focus:border-blue-700 focus:outline-none"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#0B1F3F] hover:bg-[#09172E] text-white font-semibold py-4 rounded-md shadow-lg text-lg"
            >
              {loading ? "Registering..." : "Register Brand"}
            </button>
          </form>

            {/* 🔹 Text and "Proceed" Button */}
            <div className="text-center mt-4">
              <p className="text-gray-700 font-medium">Already registered?</p>
              <button
                onClick={handleProceed}
                className="mt-2 w-full border-2 border-[#0B1F3F] text-[#0B1F3F] font-bold bg-white py-4 rounded-md shadow-lg text-lg hover:bg-gray-100"
              >
                Proceed
              </button>
          </div>
        </div>
      </div>
    </div>
  );
}
