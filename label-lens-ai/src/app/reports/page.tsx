import Image from "next/image";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h1 className="text-3xl font-bold mb-4">Compliance Made Simple</h1>
      <Image
        src="/construction.svg"
        alt="construction"
        className="dark:invert"
        width={500}
        height={24}
        priority
      />
      <h2></h2>
    </main>
  );
}
