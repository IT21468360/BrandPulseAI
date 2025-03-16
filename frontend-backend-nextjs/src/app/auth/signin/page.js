"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/app/context/AuthContext";

export default function Signin() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();
  const { saveUserSession } = useAuth(); // Use updated function

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch("/api/auth/signin", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to sign in");
      }

      if (!data.token || !data.user) {
        throw new Error("Invalid response from server");
      }

      // Store token & user details
      saveUserSession(data.token, data.user);
      
      console.log("User session stored:", data.user);
      
      router.push("/"); // Redirect to homepage
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-white dark:bg-gray-900 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-lg p-10 space-y-8 bg-white shadow-2xl text-[#0B1F3F] dark:bg-white dark:text-gray-900 rounded-lg shadow-lg">
        <div className="flex justify-center">
          <img src="/images/signin.jpg" alt="Sign In" className="w-25 h-25" />
        </div>
        <h2 className="text-center text-3xl font-bold">Sign in to your account</h2>
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && <div className="text-red-500 text-sm text-center">{error}</div>}
          <div>
            <label htmlFor="email" className="block text-sm font-medium">Email address</label>
            <input
              id="email"
              name="email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-2 block w-full rounded-md bg-white px-3 py-2 text-gray-900 border border-gray-300 shadow-md focus:border-blue-700 focus:outline-none"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-2 block w-full rounded-md bg-white px-3 py-2 text-gray-900 border border-gray-300 shadow-md focus:border-blue-700 focus:outline-none"
            />
          </div>
          <button
            type="submit"
            className="w-full bg-[#0B1F3F] hover:bg-[#09172E] text-white font-semibold py-4 rounded-md shadow-lg text-lg"
          >
            Sign in
          </button>
        </form>
        <p className="text-center text-sm">
          Not a member? <a href="/auth/signup" className="font-semibold text-[#0B1F3F] dark:text-blue-700">Sign Up</a>
        </p>
      </div>
    </div>
  );
}
