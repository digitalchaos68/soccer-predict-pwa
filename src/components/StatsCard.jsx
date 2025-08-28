export default function StatsCard({ title, value, color = 'primary' }) {
  const colorMap = {
    success: 'bg-success',
    danger: 'bg-danger',
    warning: 'bg-warning',
    primary: 'bg-primary',
  };

  return (
    <div className={`p-4 rounded-lg ${colorMap[color]} text-white shadow`}>
      <h3 className="text-sm opacity-90">{title}</h3>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
}