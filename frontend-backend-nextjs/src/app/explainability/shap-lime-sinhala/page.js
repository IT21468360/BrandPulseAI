"use client"

import { useEffect, useState } from "react"
import Header from "@/app/components/Header"
import Footer from "@/app/components/Footer"
import { toUrlSinhala } from "@/controllers/xaiControllerSinhala"

export default function ShapLimeSinhala() {
  const [items, setItems] = useState([])

  useEffect(() => {
    ;(async () => {
      // ensure the reports exist
      await fetch("/api/xai/sinhala/reports/generate/all", { method: "POST" })
      // fetch shap+lime entries
      const res  = await fetch("/api/xai/sinhala/reports/shaplime")
      const data = await res.json()
      setItems(data)
    })()
  }, [])

  if (!items.length) return <div className="p-4">Loading explainability…</div>

  return (
    <div className="bg-gray-100 min-h-screen">
      <Header activeTab="/explainability/shap-lime-sinhala" showFullNav />
      <div className="max-w-4xl mx-auto py-10 space-y-12">
        {items.map(({ aspect, lime_html, shap_html, wordcloud_png }) => (
          <div key={aspect} className="bg-white p-6 rounded-lg shadow space-y-4">
            <h2 className="text-2xl font-bold">{aspect}</h2>

            <div>
              <h3 className="font-semibold">SHAP Explainability</h3>
              <iframe
                src={toUrlSinhala(shap_html)}
                width="100%"
                height="200"
                className="rounded"
              />
            </div>

            <div>
              <h3 className="font-semibold">LIME Explainability</h3>
              <iframe
                src={toUrlSinhala(lime_html)}
                width="100%"
                height="300"
                className="rounded"
              />
            </div>

            <div>
              <h3 className="font-semibold">Word Cloud</h3>
              <img
                src={toUrlSinhala(wordcloud_png)}
                alt={`Word cloud for ${aspect}`}
                className="w-full rounded"
              />
            </div>
          </div>
        ))}
      </div>
      <Footer />
    </div>
  )
}
