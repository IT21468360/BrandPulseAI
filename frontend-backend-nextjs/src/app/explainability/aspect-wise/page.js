"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Header from "@/app/components/Header";
import Footer from "@/app/components/Footer";
import { toUrl } from "@/controllers/xaiControllerenglish";

export default function AspectWiseExplainability() {
  const router = useRouter();
  const [report, setReport] = useState(null);
  const [error, setError]   = useState(null);

  useEffect(() => {
    (async () => {
      try {
        await fetch("/api/xai/reports/generate/all", { method: "POST" });
        const res = await fetch("/api/xai/reports/aspect");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        setReport(await res.json());
      } catch (e) {
        console.error(e);
        setError(e.message);
      }
    })();
  }, []);

  if (error) return <div className="p-4 text-red-600">Error: {error}</div>;
  if (!report) return <div className="p-4">Loading report…</div>;

  return (
    <div className="bg-gray-100 min-h-screen">
      <Header activeTab="/explainability/aspect-wise" showFullNav />
      <div className="max-w-5xl mx-auto py-12 px-6 space-y-8">
        {/* Page title bar */}
        <div className="bg-[#0B1F3F] text-white p-4 rounded shadow">
          EXPLAINABILITY AI
        </div>

        {/* Language buttons with inline navy styling */}
        <div className="flex flex-wrap justify-center gap-4 mt-4 mb-8">
          {[
            { label: "Aspect-Wise Analysis (සිංහල)", path: "/explainability/aspect-wise-sinhala" },
            { label: "Aspect-Wise Analysis (English)", path: "/explainability/aspect-wise" },
            { label: "SHAP-LIME (සිංහල)", path: "/explainability/shap-lime-sinhala" },
            { label: "SHAP-LIME (English)", path: "/explainability/shap-lime" },
          ].map((btn) => (
            <button
              key={btn.label}
              onClick={() => router.push(btn.path)}
              style={{
                backgroundColor: "#0B1F3F",
                color: "white",
                padding: "0.5rem 1rem",
                borderRadius: "0.375rem",
                cursor: "pointer"
              }}
            >
              {btn.label}
            </button>
          ))}
        </div>

        {/* The styled HTML report in an iframe */}
        <div className="bg-white rounded-lg shadow overflow-auto">
          <iframe
            src={toUrl(report.html)}
            width="100%"
            height="800"
            style={{ border: "none" }}
            title="Aspect Report"
          />
        </div>

        {/* The individual chart thumbnails */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Chart title="Aspect Distribution"    path={report.charts.aspect_dist} />
          <Chart title="Avg Likes by Sentiment"  path={report.charts.avg_likes} />
          <Chart title="Avg Likes by Aspect & Sentiment" path={report.charts.likes_aspect} />
          <Chart title="Negative Word Cloud"    path={report.charts.neg_wc} />
          <Chart title="Positive Word Cloud"    path={report.charts.pos_wc} />
        </div>

        {/* Download button */}
        <div className="text-center mt-8">
          <a
            href={toUrl(report.html)}
            download
            style={{
              backgroundColor: "#0B1F3F",
              color: "white",
              padding: "0.75rem 1.5rem",
              borderRadius: "0.375rem",
              textDecoration: "none",
            }}
          >
            Download Full Report
          </a>
        </div>
      </div>
      <Footer />
    </div>
  );
}

function Chart({ title, path }) {
  return (
    <div>
      <h3 className="font-semibold mb-2">{title}</h3>
      <img src={toUrl(path)} alt={title} className="w-full rounded shadow" />
    </div>
  );
}
