// app/explainability/shap-lime/page.js
"use client";

import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Image from "next/image";
import Header from "@/app/components/Header";
import Footer from "@/app/components/Footer";
import ClientOnly from "@/app/components/ClientOnly";
import {
  explainEnglish,
  toUrl,
  getHistoryEnglish,
} from "@/controllers/xaiControllerenglish";

export default function ShapLimeExplainability() {

  
  const router = useRouter();
  const pathname = usePathname();

  // ─── form state ─────────────────────────────────────────
  const [text, setText]     = useState("");
  const [method, setMethod] = useState("lime");
  const [aspect, setAspect] = useState("");

  // ─── results ────────────────────────────────────────────
  const [html, setHtml]     = useState("");
  const [result, setResult] = useState(null);

  // ─── history + samples ──────────────────────────────────
  const [history, setHistory] = useState([]);
  const [samples, setSamples] = useState([]);

  // ─── auth guard ─────────────────────────────────────────
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) router.push("/auth/signin");
  }, [router]);

  // ─── load history + gallery samples once ────────────────
  useEffect(() => {
    getHistoryEnglish(10).then(setHistory);
    fetch("/api/xai/reports/shaplime")
      .then((r) => r.json())
      .then(setSamples)
      .catch(console.error);
  }, []);

  // ─── handle submit ──────────────────────────────────────
  async function onSubmit(e) {
    e.preventDefault();
    setHtml("");
    setResult(null);

    const res = await explainEnglish({ text, method, aspect });
    setResult(res);

    // inject HTML for LIME or SHAP if provided
    if (method === "lime" && res.lime) {
      const r = await fetch(toUrl(res.lime));
      setHtml(await r.text());
    }
    if (method === "shap" && res.shap?.endsWith(".html")) {
      const r = await fetch(toUrl(res.shap));
      setHtml(await r.text());
    }
  }

  return (
    <div className="bg-gray-100 min-h-screen">
      <Header activeTab={pathname} showFullNav />

      <div className="max-w-5xl mx-auto py-12 px-6 space-y-12">
        <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold shadow-md">
          EXPLAINABILITY AI
        </div>
        {/* ─── LANGUAGE BUTTONS ──────────────────────────────── */}
        <div className="flex flex-wrap justify-center gap-4 mt-12 mb-12">
            <button
              className="bg-blue-600 text-white px-5 py-2 rounded-md hover:bg-blue-700"
              onClick={() => router.push("/explainability/aspect-wise-sinhala")}
            >
              Aspect-Wise Analysis (සිංහල)
            </button>
            <button
              className="bg-blue-600 text-white px-5 py-2 rounded-md hover:bg-blue-700"
              onClick={() => router.push("/explainability/aspect-wise")}
            >
              Aspect-Wise Analysis (English)
            </button>
            <button
              className="bg-blue-600 text-white px-5 py-2 rounded-md hover:bg-blue-700"
              onClick={() => router.push("/explainability/shap-lime-sinhala")}
            >
              SHAP-LIME (සිංහල)
            </button>
            <button
              className="bg-blue-600 text-white px-5 py-2 rounded-md hover:bg-blue-700"
              onClick={() => router.push("/explainability/shap-lime")}
            >
              SHAP-LIME (English)
            </button>
          </div>
        {/* ─── INTRODUCTION SECTION ─────────────────────────── */}
        <section className="bg-white rounded-xl shadow-lg overflow-hidden">

          <div className="bg-blue-900 px-6 py-4">
            <h2 className="text-2xl font-bold text-white">
              WHAT IS EXPLAINABILITY AI?
            </h2>
          </div>
          <div className="p-8 text-center space-y-6">
            <p className="text-gray-800 text-lg leading-relaxed">
              Explainability AI (XAI) methods such as{" "}
              <strong>LIME</strong> and <strong>SHAP</strong> shine a light on the
              inner workings of “black-box” models by pinpointing which inputs —
              words, pixels or features — drive a prediction. With XAI you can:
            </p>
            <ul className="inline-block text-left space-y-2 text-gray-700">
              <li>• Identify the top words influencing a sentiment prediction</li>
              <li>• Detect and correct biased or spurious patterns</li>
              <li>• Improve model accuracy by debugging errors</li>
              <li>• Communicate insights clearly to stakeholders</li>
            </ul>
            <div className="mx-auto w-full max-w-md aspect-[4/3] relative">
              <Image
                src="/images/xai-site.png"
                alt="Explainable AI workflow"
                fill
                className="object-contain"
              />
            </div>
          </div>
        </section>

        {/* ─── TRY-IT-YOURSELF SECTION ───────────────────────── */}
        <section className="bg-white p-8 rounded-xl shadow-lg space-y-6">
          <h2 className="text-2xl font-semibold text-gray-800">
            Try it yourself
          </h2>

          <form onSubmit={onSubmit} className="space-y-4">
            <textarea
              rows={4}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter text to explain…"
              className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <div className="flex flex-col sm:flex-row sm:items-center gap-4">
              <label className="flex items-center gap-2">
                <span className="font-medium">Method:</span>
                <select
                  value={method}
                  onChange={(e) => setMethod(e.target.value)}
                  className="border rounded-lg p-2"
                >
                  <option value="lime">LIME</option>
                  <option value="shap">SHAP</option>
                  <option value="report">Full report</option>
                </select>
              </label>

              <label className="flex items-center gap-2 flex-1">
                <span className="font-medium">Aspect:</span>
                <input
                  value={aspect}
                  onChange={(e) => setAspect(e.target.value)}
                  placeholder="e.g. Customer Support"
                  className="border rounded-lg p-2 w-full"
                />
              </label>

              <button
                type="submit"
                className="ml-auto bg-blue-900 text-white px-6 py-2 rounded-lg hover:bg-blue-800 transition"
              >
                Explain
              </button>
            </div>
          </form>

          {/* Injected HTML (LIME/SHAP) */}
          {html && (
            <ClientOnly>
              <div
                className="mt-6 bg-gray-50 p-6 rounded-lg shadow-inner overflow-auto"
                dangerouslySetInnerHTML={{ __html: html }}
              />
            </ClientOnly>
          )}

          {/* Injected HTML (Full-Report) */}
{html && (
  <ClientOnly>
    <div
      className="mt-6 bg-gray-50 p-6 rounded-lg shadow-inner overflow-auto"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  </ClientOnly>
)}

{/* Real-time LIME */}
{method === "lime" && result && (
  <div className="mt-6 bg-gray-50 p-6 rounded-lg shadow-inner">
    <h3 className="font-semibold mb-2">LIME Explanation</h3>
    <ul className="list-disc list-inside">
      {result.map(([word, weight]) => (
        <li key={word}>
          <strong>{word}</strong>: {weight.toFixed(3)}
        </li>
      ))}
    </ul>
  </div>
)}

{/* Real-time SHAP */}
{method === "shap" && result && (
  <div className="mt-6 bg-gray-50 p-6 rounded-lg shadow-inner overflow-x-auto">
    <h3 className="font-semibold mb-2">SHAP Explanation (Positive class)</h3>
    <table className="min-w-full table-auto border-collapse">
      <thead>
        <tr className="bg-gray-100">
          <th className="px-4 py-2 border">Token</th>
          <th className="px-4 py-2 border">Contribution</th>
        </tr>
      </thead>
      <tbody>
        {result.tokens.map((tok, i) => (
          <tr key={i}>
            <td className="px-4 py-2 border">{tok}</td>
            <td className="px-4 py-2 border">
              {result.shap_values[2][i].toFixed(3)}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
)}


          {/* On-demand PNG outputs */}
          {result?.shap?.endsWith(".png") && (
            <div className="mt-6 bg-white p-6 rounded-lg shadow">
              <h3 className="font-semibold mb-2">SHAP force plot</h3>
              <img src={toUrl(result.shap)} alt="SHAP" className="w-full" />
            </div>
          )}
          {result?.wordcloud && (
            <div className="mt-6 bg-white p-6 rounded-lg shadow">
              <h3 className="font-semibold mb-2">Word cloud</h3>
              <img
                src={toUrl(result.wordcloud)}
                alt="Word Cloud"
                className="w-full"
              />
            </div>
          )}
        </section>

        {/* ─── ASPECT-WISE GALLERY ───────────────────────────── */}
        {samples.length > 0 && (
          <section className="space-y-8">
            <h2 className="text-2xl font-semibold">Aspect-Wise Samples</h2>
            {samples.map((s) => (
              <div
                key={s.aspect}
                className="bg-white p-6 rounded-xl shadow-md"
              >
                <h3 className="font-semibold mb-4">{s.aspect}</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <iframe
                    src={toUrl(s.lime_html)}
                    width="100%"
                    height={240}
                    title={`${s.aspect} LIME`}
                    className="rounded-lg border"
                  />
                  <iframe
                    src={toUrl(s.shap_html)}
                    width="100%"
                    height={240}
                    title={`${s.aspect} SHAP`}
                    className="rounded-lg border"
                  />
                  <img
                    src={toUrl(s.wordcloud_png)}
                    alt={`${s.aspect} WC`}
                    className="rounded-lg w-full"
                  />
                </div>
              </div>
            ))}
          </section>
        )}

        {/* ─── PAST EXPLANATIONS ─────────────────────────────── */}
        {history.length > 0 && (
          <section>
            <h2 className="text-2xl font-semibold">Past Explanations</h2>
            <ul className="space-y-4 mt-4">
              {history.map((h) => (
                <li
                  key={h._id}
                  className="bg-white p-4 rounded-lg shadow-md"
                >
                  <div className="text-sm text-gray-500">
                    {new Date(h.created_at).toLocaleString()}
                  </div>
                  <div className="mt-2">
                    “{h.text.slice(0, 80)}…”&nbsp;[
                    <a
                      href={toUrl(h.lime_html)}
                      target="_blank"
                      className="text-blue-600 hover:underline"
                    >
                      LIME
                    </a>
                    ,&nbsp;
                    <a
                      href={toUrl(h.shap_html)}
                      target="_blank"
                      className="text-blue-600 hover:underline"
                    >
                      SHAP
                    </a>
                    ,&nbsp;
                    <a
                      href={toUrl(h.wordcloud_png)}
                      target="_blank"
                      className="text-blue-600 hover:underline"
                    >
                      WC
                    </a>
                    ]
                  </div>
                </li>
              ))}
            </ul>
          </section>
        )}

      </div>

      <Footer />
    </div>
  );
}


