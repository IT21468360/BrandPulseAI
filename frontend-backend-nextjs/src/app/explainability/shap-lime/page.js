"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Header from "@/app/components/Header";
import Footer from "@/app/components/Footer";
import ClientOnly from "@/app/components/ClientOnly";
import { getExcelSamplesEnglish, toUrl } from "@/controllers/xaiControllerenglish";

export default function ShapLimeExplainability() {
  const router = useRouter();
  const [samples, setSamples] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const data = await getExcelSamplesEnglish();
        setSamples(data);
      } catch (err) {
        console.error("Failed loading samples:", err);
      } finally {
        setLoading(false);
      }
    })();
  }, [router]);

  // if (!samples) {
  //   return <div className="p-6 text-center">Loading explainability samples…</div>;
  // }

if (loading) {
   return (
     <div className="flex items-center justify-center h-screen bg-gray-100">
       <svg
         className="animate-spin h-12 w-12 text-blue-600"
         xmlns="http://www.w3.org/2000/svg"
         fill="none"
         viewBox="0 0 24 24"
       >
         <circle
           className="opacity-25"
           cx="12"
           cy="12"
           r="10"
           stroke="currentColor"
           strokeWidth="4"
         />
         <path
           className="opacity-75"
           fill="currentColor"
           d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
       />
       </svg>
     </div>
   );
 }

  return (
    <div className="bg-gray-100 min-h-screen">
      <Header activeTab="/explainability/shap-lime" showFullNav />

      <main className="max-w-4xl mx-auto py-12 px-4 space-y-12">
        <h1 className="text-3xl font-bold text-center">
          Aspect-Wise Explainability Samples
        </h1>

        {samples.map(({ aspect, text, lime_html, shap_html }) => (
          <section
            key={aspect}
            className="bg-white rounded-lg shadow-md p-6 space-y-6"
          >
            <h2 className="text-2xl font-semibold">{aspect}</h2>
            <p className="italic text-gray-600">{text}</p>

            {/* SHAP */}
            <div>
              <h3 className="font-medium">SHAP Explainability</h3>
              <ClientOnly>
                <iframe
                  src={toUrl(shap_html)}
                  title={`${aspect} SHAP`}
                  className="w-full h-64 rounded-lg border"
                />
              </ClientOnly>
            </div>

            {/* LIME */}
            <div>
              <h3 className="font-medium">LIME Explainability</h3>
              <ClientOnly>
                <iframe
                  src={toUrl(lime_html)}
                  title={`${aspect} LIME`}
                  className="w-full h-64 rounded-lg border"
                />
              </ClientOnly>
            </div>
          </section>
        ))}
      </main>

      <Footer />
    </div>
  );
}

