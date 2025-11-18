import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface RankHistoryChartProps {
  history: Array<{ date: string; position: number | null }>
  keywordText: string
}

export default function RankHistoryChart({ history, keywordText }: RankHistoryChartProps) {
  // Reverse Y-axis so position 1 is at top
  const maxPosition = Math.max(...history.map(h => h.position || 0).filter(p => p > 0), 20)

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">Rank History: {keywordText}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={history}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis
            reversed
            domain={[1, maxPosition]}
            tick={{ fontSize: 12 }}
            label={{ value: 'Rank Position', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip
            contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
            labelStyle={{ fontWeight: 'bold' }}
            formatter={(value: any) => [`Position ${value}`, 'Rank']}
          />
          <Line
            type="monotone"
            dataKey="position"
            stroke="#0ea5e9"
            strokeWidth={2}
            dot={{ fill: '#0ea5e9', r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
