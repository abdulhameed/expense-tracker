export default function App() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-primary-50 to-primary-100">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-primary-900 mb-4">Expense Tracker</h1>
        <p className="text-lg text-primary-700 mb-8">Frontend development environment is ready!</p>
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-semibold text-neutral-900 mb-4">Setup Complete ✓</h2>
          <ul className="text-left text-neutral-700 space-y-2">
            <li>✓ Vite + React + TypeScript configured</li>
            <li>✓ Tailwind CSS with custom theme</li>
            <li>✓ Testing framework (Vitest) ready</li>
            <li>✓ ESLint & Prettier configured</li>
            <li>✓ Project structure created</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
