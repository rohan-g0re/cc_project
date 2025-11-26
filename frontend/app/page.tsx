"use client";

import Link from "next/link";
import UploadCard from "../components/UploadCard";
import SearchCard from "../components/SearchCard";

export default function HomePage() {
  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-800/80 bg-slate-900/80 p-6 shadow-soft">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-white">Hands-on search workspace</h2>
            <p className="text-sm text-slate-400">
              Upload PDFs to S3, explore Semantic Scholar + arXiv, and keep the same clean typography we started with.
            </p>
          </div>
          <Link
            href="/start"
            className="inline-flex items-center justify-center rounded-full bg-brand-500 px-4 py-2 text-xs font-semibold text-white shadow-brand-500/30 transition hover:bg-brand-600"
          >
            Start study session →
          </Link>
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)]">
        <UploadCard />
        <SearchCard />
      </div>
    </div>
  );
}
