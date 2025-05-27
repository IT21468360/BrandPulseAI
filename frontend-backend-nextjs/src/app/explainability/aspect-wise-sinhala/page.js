"use client"

import { useEffect, useState } from "react"
import Header from "@/app/components/Header"
import Footer from "@/app/components/Footer"
import { toUrlSinhala } from "@/controllers/xaiControllerSinhala"

export default function AspectWiseSinhala() {
  const [report, setReport] = useState(null)
  const [error, setError]   = useState(null)

  useEffect(() => {
    ;(async () => {
      try {
        // trigger report generation on the back end
        await fetch("/api/xai/sinhala/reports/generate/all", { method: "POST" })
        // fetch the aspect‐wise report metadata
        const res = await fetch("/api/xai/sinhala/reports/aspect")
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        setReport(await res.json())
      } catch (e) {
        console.error(e)
        setError(e.message)
      }
    })()
  }, [])

  if (error) return <div className="p-4 text-red-600">Error: {error}</div>
  if (!report) return <div className="p-4">Loading report…</div>

  return (
    <div className="bg-gray-100 min-h-screen">
      <Header activeTab="/explainability/aspect-wise-sinhala" showFullNav />
      <div className="max-w-6xl mx-auto py-10 px-6 space-y-8">
        {/* Full HTML report */}
        <iframe
          src={toUrlSinhala(report.html)}
          width="100%"
          height="700"
          className="rounded-lg shadow"
        />

        {/* Individual charts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Chart title="Aspect Distribution"             path={report.charts.aspect_dist} />
          <Chart title="Avg Likes by Sentiment"           path={report.charts.avg_likes} />
          <Chart title="Avg Likes by Aspect & Sentiment"  path={report.charts.likes_aspect} />
          <Chart title="Negative Word Cloud"              path={report.charts.neg_wc} />
          <Chart title="Positive Word Cloud"              path={report.charts.pos_wc} />
        </div>

        {/* Download button */}
        <div className="text-center">
          <a
            href={toUrlSinhala(report.html)}
            download
            className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700"
          >
            Download Full Report
          </a>
        </div>
      </div>
      <Footer />
    </div>
  )
}

function Chart({ title, path }) {
  return (
    <div>
      <h3 className="font-semibold mb-2">{title}</h3>
      <img src={toUrlSinhala(path)} alt={title} className="w-full rounded shadow" />
    </div>
  )
}
