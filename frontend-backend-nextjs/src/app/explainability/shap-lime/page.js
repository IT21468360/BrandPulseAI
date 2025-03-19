"use client";

import Header from "@/app/components/Header";
import Footer from "@/app/components/Footer";
import Image from "next/image";
import { useState } from "react";
// If you need router logic:
// import { useRouter, usePathname } from "next/navigation";

export default function ShapLimeExplainability() {
    const [analysisText, setAnalysisText] = useState("");

    return (
        <div className="bg-gray-100 min-h-screen">
            <Header activeTab="/explainability/shap-lime" showFullNav={true} />

            <div className="max-w-6xl mx-auto py-10 px-6">
                {/* Title */}
                <div className="bg-white p-6 rounded-lg shadow-md">
                    <h3 className="text-lg font-semibold mb-4">
                    <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold">
                     SHAP and LIME Explainability
                        </div>
                    </h3>
                    <p className="text-gray-700">
                        SHAP (SHapley Additive exPlanations) and LIME (Local Interpretable Model-agnostic Explanations) 
                        are powerful techniques for understanding AI predictions.  
                        SHAP provides a <strong>global view</strong> of feature importance, while LIME explains 
                        <strong> individual predictions</strong> by approximating the model locally.
                    </p>
                </div>

                {/* SHAP Section */}
                <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
                <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold">
                         SHAP Explainability
                        </div>
                    <p className="text-gray-700 mb-4">
                        SHAP explains model predictions by computing the impact of each feature on the final decision.
                    </p>
                    
                    {/* SHAP Images (Displayed One Below the Other) */}
                    <div className="flex flex-col items-center gap-6">
                        <Image 
                            src="/images/shap1.png" 
                            alt="SHAP Visualization 1" 
                            width={1500} 
                            height={1200} 
                            className="rounded-lg"  // Removed shadow-md
                        />
                    </div>
                </div>

                {/* LIME Section */}
                <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
                     <div className="bg-[#0B1F3F] text-white p-4 rounded-md text-lg font-semibold">
                         LIME Explainability
                        </div>
                    <p className="text-gray-700 mb-4">
                        LIME works by perturbing the input data and observing how predictions change, helping to explain individual instances.
                    </p>
                    
                    {/* LIME Images (Displayed One Below the Other) */}
                    <div className="flex flex-col items-center gap-6">
                        <Image 
                            src="/images/lime xai1.png" 
                            alt="LIME Visualization 1" 
                            width={700} 
                            height={400} 
                            className="rounded-lg"  // Removed shadow-md
                        />
                        <Image 
                            src="/images/lime xai2.png" 
                            alt="LIME Visualization 2" 
                            width={1000} 
                            height={800} 
                            className="rounded-lg"  // Removed shadow-md
                        />
                    </div>
                </div>

                {/* Analysis More Comments Section */}
             
            </div>

            <Footer />
        </div>
    );
}
