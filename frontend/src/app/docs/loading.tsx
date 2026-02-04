export default function DocsLoading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0a0a0b]">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-blue-400/30 border-t-blue-400 rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-400">Loading documentation...</p>
      </div>
    </div>
  );
}
