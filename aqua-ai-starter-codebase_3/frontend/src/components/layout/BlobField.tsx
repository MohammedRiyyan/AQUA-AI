export function BlobField() {
  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      <div className="animate-drift absolute -left-24 -top-20 h-[340px] w-[340px] rounded-full bg-aqua opacity-55 mix-blend-screen blur-[60px]" />
      <div
        className="absolute -right-24 bottom-14 h-[280px] w-[280px] rounded-full bg-teal opacity-55 mix-blend-screen blur-[60px]"
        style={{ animation: "drift 26s ease-in-out infinite reverse" }}
      />
      <div
        className="absolute left-3/5 top-2/5 h-[220px] w-[220px] rounded-full bg-[#3A6FF7] opacity-55 mix-blend-screen blur-[60px]"
        style={{ animation: "drift 30s ease-in-out infinite" }}
      />
    </div>
  );
}
