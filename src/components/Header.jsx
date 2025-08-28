export default function Header({ league, setLeague }) {
  return (
    <header className="bg-primary text-white p-4 shadow-md">
      <div className="container mx-auto flex items-center">
        {/* Logo */}
        <img
          src="/assets/logo.png"
          alt="SoccerPredict"
          width="32"
          height="32"
          className="w-8 h-8 mr-2 rounded-full object-contain"
        />
        <h1 className="text-xl font-bold">⚽ SoccerPredict</h1>
        <p className="text-sm opacity-90 ml-2">AI-Powered Predictions</p>
      </div>
    </header>
  );
}