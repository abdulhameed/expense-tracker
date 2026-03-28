import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Legend,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface PieChartProps {
  data: Array<{
    name: string;
    value: number;
    color?: string;
  }>;
  height?: number;
  showLabels?: boolean;
  showLegend?: boolean;
}

const defaultColors = [
  '#3b82f6',
  '#8b5cf6',
  '#ec4899',
  '#f59e0b',
  '#10b981',
  '#06b6d4',
  '#6366f1',
  '#f97316',
];

export function PieChart({
  data,
  height = 300,
  showLabels = false,
  showLegend = true,
}: PieChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-80 bg-neutral-50 rounded-lg">
        <p className="text-neutral-500">No data available</p>
      </div>
    );
  }

  // Assign colors if not provided
  const coloredData = data.map((item, index) => ({
    ...item,
    color: item.color || defaultColors[index % defaultColors.length],
  }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsPieChart>
        <Pie
          data={coloredData}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={showLabels ? renderLabel : undefined}
          outerRadius={100}
          fill="#8884d8"
          dataKey="value"
        >
          {coloredData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value: any) => {
            if (typeof value === 'number') {
              return `$${value.toFixed(2)}`;
            }
            return value;
          }}
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: '0.5rem',
          }}
        />
        {showLegend && <Legend />}
      </RechartsPieChart>
    </ResponsiveContainer>
  );
}

function renderLabel(entry: any) {
  const percent = (entry.value / 100).toFixed(0);
  return `${entry.name} ${percent}%`;
}
