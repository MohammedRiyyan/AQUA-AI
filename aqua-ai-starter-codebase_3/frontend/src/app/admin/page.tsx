"use client";

import { useState } from "react";

interface DocRow {
  id: string;
  title: string;
  status: "uploaded" | "chunking" | "embedding" | "indexed" | "failed";
  source_type: string;
}

const DEMO_DOCS: DocRow[] = [
  { id: "1", title: "WHO Hydration Guidelines 2023", status: "indexed", source_type: "pdf" },
  { id: "2", title: "CDC Water Intake Recommendations", status: "indexed", source_type: "pdf" },
  { id: "3", title: "Sports Science Fluid Replacement Study", status: "embedding", source_type: "pdf" },
];

const STATUS_COLOR: Record<DocRow["status"], string> = {
  uploaded: "text-foam/50",
  chunking: "text-yellow-300",
  embedding: "text-yellow-300",
  indexed: "text-aqua-soft",
  failed: "text-red-400",
};

export default function AdminTrainingPage() {
  const [docs, setDocs] = useState<DocRow[]>(DEMO_DOCS);
  const [title, setTitle] = useState("");
  const [sourceType, setSourceType] = useState("pdf");
  const [file, setFile] = useState<File | null>(null);

  async function handleUpload() {
    if (!file || !title) return;
    // Real implementation: POST multipart/form-data to
    // /api/v1/admin/documents (see backend/app/api/routers/admin_training.py)
    const form = new FormData();
    form.append("file", file);
    form.append("title", title);
    form.append("source_type", sourceType);

    setDocs((d) => [{ id: String(Date.now()), title, status: "uploaded", source_type: sourceType }, ...d]);
    setTitle("");
    setFile(null);
  }

  return (
    <main className="mx-auto min-h-screen max-w-3xl px-6 py-10 text-foam">
      <h1 className="font-display text-2xl font-bold">Admin — AI Training Console</h1>
      <p className="mt-1 text-[13px] text-foam/50">
        Upload research papers, medical PDFs, WHO/CDC guidelines, and datasets into the custom hydration model&apos;s
        knowledge base. Each upload is chunked, embedded, and indexed automatically — see{" "}
        <code className="text-aqua-soft">backend/app/ai/ingestion/pipeline.py</code>.
      </p>

      <div className="glass mt-6 rounded-lg2 p-5">
        <h2 className="mb-3 text-[14px] font-semibold">Upload new source</h2>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="mb-1 block text-[10.5px] uppercase tracking-wide text-foam/40">Title</label>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="WHO Hydration Guidelines 2023"
              className="w-full rounded-xl border border-white/10 bg-white/[0.09] px-3 py-2.5 text-[13px] outline-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-[10.5px] uppercase tracking-wide text-foam/40">Format</label>
            <select
              value={sourceType}
              onChange={(e) => setSourceType(e.target.value)}
              className="w-full rounded-xl border border-white/10 bg-white/[0.09] px-3 py-2.5 text-[13px] outline-none"
            >
              {["pdf", "csv", "json", "markdown", "txt"].map((t) => (
                <option key={t} value={t}>{t.toUpperCase()}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="mt-3">
          <label className="mb-1 block text-[10.5px] uppercase tracking-wide text-foam/40">File</label>
          <input
            type="file"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="w-full rounded-xl border border-dashed border-white/15 bg-white/[0.04] px-3 py-3 text-[12.5px]"
          />
        </div>
        <button
          onClick={handleUpload}
          className="mt-4 rounded-xl bg-gradient-to-br from-aqua to-teal px-5 py-2.5 text-[13px] font-bold text-ink"
        >
          Upload &amp; index
        </button>
      </div>

      <div className="glass mt-6 rounded-lg2 p-5">
        <h2 className="mb-3 text-[14px] font-semibold">Knowledge base ({docs.length} documents)</h2>
        <table className="w-full text-left text-[12.5px]">
          <thead className="text-[10.5px] uppercase tracking-wide text-foam/40">
            <tr>
              <th className="pb-2">Title</th>
              <th className="pb-2">Format</th>
              <th className="pb-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {docs.map((d) => (
              <tr key={d.id} className="border-t border-white/[0.06]">
                <td className="py-2.5">{d.title}</td>
                <td className="py-2.5 uppercase text-foam/50">{d.source_type}</td>
                <td className={`py-2.5 font-semibold ${STATUS_COLOR[d.status]}`}>{d.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
