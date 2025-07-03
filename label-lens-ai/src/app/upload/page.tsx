import FileUpload from "@/app/components/FileUpload";

export default function UploadPage(){
    return (
        <div className="min-h-screen p-8">
            <h1 className="text-3xl font-bold mb-4">Upload File</h1>
            <FileUpload />
        </div>
    )
}