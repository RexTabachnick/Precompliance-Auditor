import FileUpload from "@/app/components/FileUpload";
"use client";
import { useState } from "react";
import Layout from "../components/Layout";


export default function UploadPage(){
    const [file, setFile] = useState<File | null>(null);
    const [data, setData] = useState<any | null>(null);
    const [loading, setLoading] = useState(false);
    const[error, setError] = useState<string | null>(null);

    const handleFile = async () => {
        if(!file){
            setError("No File Selected!")
            return;
        }
    

        setLoading(true);
        setError(null);

        const formData = new FormData();
        if (file) {
            formData.append("file", file);
        }

        try {
            const res = await fetch("http://localhost:8000/api/extract/analyze-document", {
                method: "POST",
                body: formData,
            });

            if (!res.ok){
                throw new Error(`HTTP error ${res.status}`);
            } 
            
            const result = await res.json();
            setData(result);
        } catch(err: any){
            console.error("Upload Failed:", err)
            setError(err.message || "Upload failed.")
        } finally {
            setLoading(false);
        }
    };

    return (
        <Layout>
            <div className="min-h-screen bg-white px-6 py-8 text-slate-800">
            <h1 className="text-4xl font-bold mb-4">Generate Compliance Report</h1>

            <div className="flex flex-col lg:flex-row gap-8">
                {/* Left side: Controls and Report */}
                <div className="lg:w-2/3 space-y-8">
                <div className="border border-slate-300 p-4 rounded-md bg-slate-50 shadow-sm">
                    <div className="relative">
                        <button
                            type="button"
                            onClick={() => document.getElementById("hiddenFile")?.click()}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-semibold transition"
                        >
                            Choose File
                        </button>
                        <input
                            id="hiddenFile"
                            type="file"
                            accept=".pdf,.docx,image/*"
                            onChange={(e) => setFile(e.target.files?.[0] || null)}
                            className="absolute left-0 top-0 opacity-0 w-full h-full cursor-pointer"
                        />
                    </div>

                    {file && (
                    <div className="mt-2 text-sm text-slate-600">
                        Selected file: <span className="font-medium">{file.name}</span>
                    </div>
                    )}

                    <button
                    onClick={handleFile}
                    className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-semibold transition"
                    >
                    Upload & Analyze
                    </button>
                </div>

                {loading && (
                    <div className="text-blue-600 animate-pulse flex items-center gap-2">
                    <svg className="animate-spin h-5 w-5 text-blue-600" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                    Analyzing file...
                    </div>
                )}

                {error && (
                    <div className="text-red-600 font-semibold">❌ {error}</div>
                )}

                {data && (
                    <div className="space-y-8">
                    <section>
                        <h2 className="text-2xl font-semibold mb-2">Document Info</h2>
                        <pre className="bg-slate-100 p-4 rounded text-sm overflow-x-auto">
                        {JSON.stringify(data.document_info, null, 2)}
                        </pre>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mb-2">Claims</h2>
                        {data.claims?.length ? (
                        <ul className="space-y-2">
                            {data.claims.map((claim: any, i: number) => (
                            <li key={i} className="bg-white border border-slate-200 rounded-md p-3 shadow-sm">
                                <p className="font-medium">{claim.claim_text}</p>
                                <p className="text-sm text-slate-600 mt-1">
                                <span className="font-semibold">Type:</span> {claim.claim_type} | 
                                <span className={`ml-2 px-2 py-1 rounded text-white text-xs font-semibold ${claim.severity === 'high' ? 'bg-red-500' : claim.severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'}`}>Severity: {claim.severity}</span>
                                </p>
                            </li>
                            ))}
                        </ul>
                        ) : (
                        <p className="text-slate-600 italic">No claims found.</p>
                        )}
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mb-2">Ingredients</h2>
                        {data.ingredients?.length ? (
                        <ul className="space-y-2">
                            {data.ingredients.map((ing: any, i: number) => (
                            <li key={i} className="bg-white border border-slate-200 rounded-md p-3 shadow-sm">
                                <p className="font-medium">
                                {ing.ingredient_name}
                                {ing.is_allergen && <span className="ml-2 px-2 py-0.5 text-xs bg-red-600 text-white rounded">Allergen</span>}
                                </p>
                                <p className="text-sm text-slate-600 mt-1">{ing.function || "Unknown Function"}</p>
                            </li>
                            ))}
                        </ul>
                        ) : (
                        <p className="text-slate-600 italic">No ingredients found.</p>
                        )}
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mb-2">Compliance</h2>
                        {Array.isArray(data.compliance_analysis) && data.compliance_analysis.length > 0 ? (
                            <ul className="space-y-4">
                                {data.compliance_analysis.map((result: any, i: number) => (
                                    <li key={i} className={`p-4 rounded border-l-4 shadow-sm ${
                                        result.confidence >= 0.8 ? 'border-green-600 bg-green-50' :
                                        result.confidence >= 0.5 ? 'border-yellow-600 bg-yellow-50' :
                                        'border-red-600 bg-red-50'
                                    }`}>
                                        <h3 className="font-bold text-lg">{result.law}</h3>
                                        <p className="text-sm">
                                            <strong>Confidence:</strong> {(result.confidence * 100).toFixed(1)}%<br/>
                                            <strong>Reason:</strong> {result.reason}
                                        </p>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <p className="text-slate-600 italic">No compliance issues detected.</p>
                        )}
                    </section>
                    </div>
                )}
                </div>

                {/* Right side: File preview */}
                <div className="lg:w-1/3">
                {file && (
                    <div className="border border-slate-300 rounded-md p-2 bg-slate-50 shadow-sm">
                    <h3 className="text-lg font-semibold mb-2">Preview</h3>
                    <img
                        src={URL.createObjectURL(file)}
                        alt="Uploaded Preview"
                        className="w-full h-auto object-contain rounded"
                    />
                    </div>
                )}
                </div>
            </div>
            </div>
        </Layout>
    );
}