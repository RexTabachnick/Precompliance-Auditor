import FileUpload from "@/app/components/FileUpload";
"use client";
import { useState } from "react";


export default function UploadPage(){
    const [results, setResults] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null); 

    const handleRunDemo = async () => {
  setLoading(true); // 🔁 start loading
        try {
            const res = await fetch("http://localhost:8000/demo-compliance");
            const data = await res.json();
            if (data.results && Array.isArray(data.results)) {
            setResults(data.results);
            } else {
            console.error("Unexpected response format:", data);
            setResults([]);
            }
        } catch (err) {
            console.error("Fetch failed:", err);
            setResults([]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen p-8">
            <h1 className="text-3xl font-bold mb-4">
                Upload File
            </h1>
            <button
                onClick={handleRunDemo}
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
                Run Demo
            </button>

            {loading && (
                <div className="mt-6 text-blue-600 animate-pulse flex items-center gap-2">
                    <svg className="animate-spin h-5 w-5 text-blue-600" viewBox="0 0 24 24">
                        <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                            fill="none"
                        />
                        <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8v8H4z"
                        />
                    </svg>
                    Running compliance check...
                </div>
            )}

            {error && (
                <div className="mt-6 text-red-600 font-semibold">
                ❌ {error}
                </div>
            )}

            {results.length > 0  && (
                <div>
                    {results.map((result, index) => (
                        <div>
                            <p><strong>Client Text:</strong> {result.client_chunk}</p>
                            <p><strong>Matched Law:</strong> {result.matched_law}</p>
                            <p><strong>Verdict:</strong> {result.verdict}</p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}