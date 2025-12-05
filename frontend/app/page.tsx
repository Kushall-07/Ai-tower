"use client";

import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();

  const goToDashboard = () => {
    router.push("/dashboard");
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
      <div className="bg-slate-800 p-8 rounded-xl shadow-lg w-full max-w-md">
        <h1 className="text-2xl font-bold mb-4 text-center">
          AI Control Tower
        </h1>
        <p className="text-sm text-slate-300 mb-6 text-center">
          Simple entry screen (auth will come later).
        </p>

        <button
          onClick={goToDashboard}
          className="w-full py-2 rounded-md bg-emerald-500 hover:bg-emerald-600 font-semibold"
        >
          Go to Dashboard
        </button>
      </div>
    </main>
  );
}
