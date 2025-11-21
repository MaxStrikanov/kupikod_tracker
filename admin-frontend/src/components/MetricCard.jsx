import React from 'react'

function MetricCard({ title, value, subtitle, icon }) {
    return (
        <div
            style={{
                background: '#ffffff',
                borderRadius: 16,
                padding: 14,
                boxShadow: '0 12px 30px rgba(15,23,42,0.08)',
                border: '1px solid #e5e7eb',
                display: 'flex',
                gap: 10,
                alignItems: 'center',
            }}
        >
            <div
                style={{
                    width: 36,
                    height: 36,
                    borderRadius: 999,
                    background: '#eef2ff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 18,
                }}
            >
                {icon}
            </div>
            <div>
                <div style={{ fontSize: 11, textTransform: 'uppercase', opacity: 0.6 }}>
                    {title}
                </div>
                <div style={{ fontSize: 20, fontWeight: 700 }}>{value}</div>
                <div style={{ fontSize: 11, opacity: 0.7 }}>{subtitle}</div>
            </div>
        </div>
    )
}

export default MetricCard
