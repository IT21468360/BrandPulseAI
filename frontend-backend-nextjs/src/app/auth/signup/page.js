"use client";

import {useState} from "react";
import {useRouter} from "next/navigation";

export default function Signup() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    username: "",
    password: "",
    role: "user", // Default role
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const router = useRouter();

  const handleChange = (e) => {
    const {name, value} = e.target;
    setFormData({...formData, [name]: value});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess(false);

    try {
      const response = await fetch("/api/users", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const {error} = await response.json();
        throw new Error(error || "Failed to sign up");
      }

      setSuccess(true);

      // Redirect to Signin or Dashboard
      setTimeout(() => router.push("/auth/signin"), 2000); // Redirect after 2 seconds
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8 bg-white dark:bg-gray-900">
      <div className="sm:mx-auto sm:w-full sm:max-w-sm">
        <div className="flex justify-center items-center">
          <a href="/" aria-label="Home">
            <img
              alt="Your Company"
              src="https://tailwindui.com/plus/img/logos/mark.svg?color=indigo&shade=600"
              className="mx-auto h-10 w-auto"
            />
          </a>
        </div>
        <h2 className="mt-10 text-center text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
          Create your account
        </h2>
      </div>

      <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="text-red-500 text-sm text-center">{error}</div>
          )}
          {success && (
            <div className="text-green-500 text-sm text-center">
              Account created successfully! Redirecting to Sign-In...
            </div>
          )}
          <div>
            <label
              htmlFor="name"
              className="block text-sm font-medium text-gray-900 dark:text-white"
            >
              Full Name
            </label>
            <div className="mt-2">
              <input
                id="name"
                name="name"
                type="text"
                required
                value={formData.name}
                onChange={handleChange}
                className="block w-full rounded-md bg-gray-100 dark:bg-gray-800 px-3 py-1.5 text-base text-gray-900 dark:text-gray-300 outline outline-1 outline-gray-300 placeholder-gray-400 focus:outline-indigo-600 dark:placeholder-gray-500 sm:text-sm"
              />
            </div>
          </div>

          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-900 dark:text-white"
            >
              Email Address
            </label>
            <div className="mt-2">
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="block w-full rounded-md bg-gray-100 dark:bg-gray-800 px-3 py-1.5 text-base text-gray-900 dark:text-gray-300 outline outline-1 outline-gray-300 placeholder-gray-400 focus:outline-indigo-600 dark:placeholder-gray-500 sm:text-sm"
              />
            </div>
          </div>

          <div>
            <label
              htmlFor="username"
              className="block text-sm font-medium text-gray-900 dark:text-white"
            >
              Username
            </label>
            <div className="mt-2">
              <input
                id="username"
                name="username"
                type="text"
                required
                value={formData.username}
                onChange={handleChange}
                className="block w-full rounded-md bg-gray-100 dark:bg-gray-800 px-3 py-1.5 text-base text-gray-900 dark:text-gray-300 outline outline-1 outline-gray-300 placeholder-gray-400 focus:outline-indigo-600 dark:placeholder-gray-500 sm:text-sm"
              />
            </div>
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-900 dark:text-white"
            >
              Password
            </label>
            <div className="mt-2">
              <input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleChange}
                className="block w-full rounded-md bg-gray-100 dark:bg-gray-800 px-3 py-1.5 text-base text-gray-900 dark:text-gray-300 outline outline-1 outline-gray-300 placeholder-gray-400 focus:outline-indigo-600 dark:placeholder-gray-500 sm:text-sm"
              />
            </div>
          </div>

          <div>
            <label
              htmlFor="role"
              className="block text-sm font-medium text-gray-900 dark:text-white"
            >
              Role
            </label>
            <div className="mt-2">
              <select
                id="role"
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="block w-full rounded-md bg-gray-100 dark:bg-gray-800 px-3 py-1.5 text-base text-gray-900 dark:text-gray-300 outline outline-1 outline-gray-300 placeholder-gray-400 focus:outline-indigo-600 dark:placeholder-gray-500 sm:text-sm"
              >
                <option value="user">User</option>
                <option value="admin">Admin</option>
                <option value="manager">Manager</option>
              </select>
            </div>
          </div>

          <div>
            <button
              type="submit"
              className="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            >
              Sign Up
            </button>
          </div>
        </form>

        <p className="mt-10 text-center text-sm text-gray-500 dark:text-gray-400">
          Already have an account?{" "}
          <a
            href="/auth/signin"
            className="font-semibold text-indigo-600 hover:text-indigo-500 dark:text-indigo-400"
          >
            Sign In
          </a>
        </p>
      </div>
    </div>
  );
}
