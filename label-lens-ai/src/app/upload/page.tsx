import FileUpload from "@/app/components/FileUpload";
"use client";
import { useState } from "react";


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
        <div className="min-h-screen p-8">
            <h1 className="text-3xl font-bold mb-4">
                Upload File
            </h1>
            <input
                type="file"
                accept=".pdf,.docx,image/*"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="mb-4"
            />

            <button onClick={handleFile} className="bg-blue-500 hover:bg-blue-700 text-white font-bold rounded">
                Upload & Analyze
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
                    Analyzing file...
                </div>
            )}

            {error && (
                <div className="mt-6 text-red-600 font-semibold">
                ❌ {error}
                </div>
            )}

            {data && (
                <div className="mt-8 space-y-6">
                    <h2 className="text-xl font-semibold">Document Info</h2>
                    <pre className="bg-slate-100 p-2 rounded text-sm">{JSON.stringify(data.document_info, null, 2)}</pre>

                    <h2 className="text-xl font-semibold">Claims</h2>
                    {data.claims?.length ? (
                        <ul className="list-disc pl-6">
                            {data.claims.map((claim: any, i: number) => (
                                <li key={i}>
                                    <strong>{claim.claim_text}</strong> ({claim.claim_type}, Severity: {claim.severity})
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p>No claims found.</p>
                    )}

                    <h2 className="text-xl font-semibold">Ingredients</h2>
                    {data.ingredients?.length ? (
                        <ul className="list-disc pl-6">
                            {data.ingredients.map((ing: any, i: number) => (
                                <li key = {i}>
                                    <strong>{ing.ingredient_name}</strong> - {ing.function || "Unknown Function"}
                                    {ing.is_allergen && <span className="text-red-600">Allergen !</span>}
                                </li>
                            ))}
                        </ul>
                    ): (
                        <p>No ingredients found</p>
                    )}
                </div>
            )}
            
        </div>
    );
}