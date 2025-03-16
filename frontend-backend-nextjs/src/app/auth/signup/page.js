"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/app/context/AuthContext";

export default function Signup() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    username: "",
    password: "",
    role: "user",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const router = useRouter();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess(false);

    try {
      const response = await fetch("/api/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const { error } = await response.json();
        throw new Error(error || "Failed to sign up");
      }

      setSuccess(true);
      setTimeout(() => router.push("/auth/signin"), 2000);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-white dark:bg-gray-900 px-4 sm:px-6 lg:px-8">
      <div className="flex w-full max-w-4xl  bg-white shadow-2xl text-[#0B1F3F] dark:bg-white dark:text-gray-900 rounded-lg shadow-lg overflow-hidden">
        <div className="hidden md:flex md:w-1/2 items-center justify-center p-8">
          <img src="/images/signup.png" alt="Sign Up" className="w-160 h-160" />
        </div>
        <div className="w-full md:w-1/2 p-10 space-y-6">
          <h2 className="text-center text-3xl font-bold">Create your account</h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && <div className="text-red-500 text-sm text-center">{error}</div>}
            {success && <div className="text-green-500 text-sm text-center">Account created successfully! Redirecting...</div>}
            <div>
              <label htmlFor="name" className="block text-sm font-medium">Full Name</label>
              <input
                id="name"
                name="name"
                type="text"
                required
                value={formData.name}
                onChange={handleChange}
                className="mt-2 block w-full rounded-md bg-white dark:bg-white px-3 py-2 text-gray-900 border border-gray-300 shadow-md focus:border-blue-700 focus:outline-none"
              />
            </div>
            <div>
              <label htmlFor="email" className="block text-sm font-medium">Email Address</label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="mt-2 block w-full rounded-md bg-white dark:bg-white px-3 py-2 text-gray-900 border border-gray-300 shadow-md focus:border-blue-700 focus:outline-none"
              />
            </div>
            <div>
              <label htmlFor="username" className="block text-sm font-medium">Username</label>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={formData.username}
                onChange={handleChange}
                className="mt-2 block w-full rounded-md bg-white dark:bg-white px-3 py-2 text-gray-900 border border-gray-300 shadow-md focus:border-blue-700 focus:outline-none"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleChange}
                className="mt-2 block w-full rounded-md bg-white dark:bg-white px-3 py-2 text-gray-900 border border-gray-300 shadow-md focus:border-blue-700 focus:outline-none"
              />
            </div>
            <div>
              <label htmlFor="role" className="block text-sm font-medium">Role</label>
              <select
                id="role"
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="mt-2 block w-full rounded-md bg-white dark:bg-white px-3 py-2 text-gray-900 border border-gray-300 shadow-md focus:border-blue-700 focus:outline-none"
              >
                <option value="user">User</option>
                <option value="admin">Admin</option>
                <option value="manager">Manager</option>
              </select>
            </div>
            <button
              type="submit"
              className="w-full bg-[#0B1F3F] hover:bg-[#09172E] text-white font-semibold py-4 rounded-md shadow-lg text-lg"
            >
              Sign Up
            </button>
          </form>
          <p className="text-center text-sm">
            Already have an account? <a href="/auth/signin" className="font-semibold text-[#0B1F3F] dark:text-blue-700">Sign In</a>
          </p>
        </div>
      </div>
    </div>
  );
}