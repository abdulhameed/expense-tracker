import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface BarChartProps {
  data: Array<{ [key: string]: any }>;
  bars: Array<{
    key: string;
    color: string;
    name: string;
  }>;
  xAxisKey?: string;
  height?: number;
  layout?: 'vertical' | 'horizontal';
}

export function BarChart({
  data,
  bars,
  xAxisKey = 'name',
  height = 300,
  layout = 'horizontal',
}: BarChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-80 bg-neutral-50 rounded-lg">
        <p className="text-neutral-500">No data available</p>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsBarChart
        data={data}
        layout={layout === 'vertical' ? 'vertical' : undefined}
        margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        {layout === 'vertical' ? (
          <>
            <XAxis type="number" stroke="#6b7280" />
            <YAxis dataKey={xAxisKey} type="category" stroke="#6b7280" width={80} />
          </>
        ) : (
          <>
            <XAxis dataKey={xAxisKey} stroke="#6b7280" />
            <YAxis stroke="#6b7280" />
          </>
        )}
        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: '0.5rem',
          }}
          formatter={(value: any) => {
            if (typeof value === 'number') {
              return `$${value.toFixed(2)}`;
            }
            return value;
          }}
        />
        <Legend />
        {bars.map((bar) => (
          <Bar
            key={bar.key}
            dataKey={bar.key}
            fill={bar.color}
            name={bar.name}
            radius={[8, 8, 0, 0]}
          />
        ))}
      </RechartsBarChart>
    </ResponsiveContainer>
  );
}
