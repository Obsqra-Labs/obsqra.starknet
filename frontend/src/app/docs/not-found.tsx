import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0a0a0b] text-white">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">404</h1>
        <p className="text-gray-400 mb-8">Documentation page not found</p>
        <Link
          href="/docs/01-introduction/01-overview"
          className="text-blue-400 hover:text-blue-300 underline"
        >
          Go to Documentation Home
        </Link>
      </div>
    </div>
  );
}
