import React from 'react'

function BloggerSection({
    bloggers,
    newBlogger,
    setNewBlogger,
    addBlogger,
    selectedBlogger,
    setSelectedBlogger,
    loadingIds,
    scanBlogger,
    statsByDay,
    maxCount,
    platformFilter,
}) {
    return (
        <div>
            {/* форма добавления блогера */}
            <div
                style={{
                    background: '#ffffff',
                    borderRadius: 16,
                    padding: 14,
                    boxShadow: '0 10px 30px rgba(15,23,42,0.06)',
                    border: '1px solid #e5e7eb',
                    marginBottom: 14,
                }}
            >
                <h2 style={{ fontSize: 16, margin: 0 }}>Добавить блогера</h2>
                <p style={{ fontSize: 11, opacity: 0.7, marginTop: 4 }}>
                    Для VK: external_id = ID пользователя или -ID паблика (например, -27001778).
                </p>

                <form
                    onSubmit={addBlogger}
                    style={{
                        display: 'flex',
                        flexDirection: 'column',
                        gap: 10,
                        marginTop: 10,
                    }}
                >
                    {/* платформа + external_id */}
                    <div
                        style={{
                            display: 'flex',
                            flexWrap: 'wrap',
                            gap: 8,
                        }}
                    >
                        <div
                            style={{
                                flex: '0 0 130px',
                                minWidth: 120,
                            }}
                        >
                            <div style={{ fontSize: 11, opacity: 0.7, marginBottom: 2 }}>
                                Платформа
                            </div>
                            <select
                                value={newBlogger.platform}
                                onChange={(e) =>
                                    setNewBlogger((prev) => ({
                                        ...prev,
                                        platform: e.target.value,
                                    }))
                                }
                                style={{
                                    padding: '6px 10px',
                                    borderRadius: 999,
                                    border: '1px solid #d1d5db',
                                    fontSize: 13,
                                    width: '100%',
                                }}
                            >
                                <option value="vk">VK</option>
                                <option value="instagram">Instagram</option>
                            </select>
                        </div>

                        <div
                            style={{
                                flex: '1 1 200px',
                                minWidth: 180,
                            }}
                        >
                            <div style={{ fontSize: 11, opacity: 0.7, marginBottom: 2 }}>
                                external_id
                            </div>
                            <input
                                type="text"
                                value={newBlogger.external_id}
                                onChange={(e) =>
                                    setNewBlogger((prev) => ({
                                        ...prev,
                                        external_id: e.target.value,
                                    }))
                                }
                                placeholder="-27001778"
                                style={{
                                    padding: '6px 10px',
                                    borderRadius: 999,
                                    border: '1px solid #d1d5db',
                                    fontSize: 13,
                                    width: '100%',
                                }}
                            />
                        </div>
                    </div>

                    {/* handle + имя */}
                    <div
                        style={{
                            display: 'flex',
                            flexWrap: 'wrap',
                            gap: 8,
                        }}
                    >
                        <div
                            style={{
                                flex: '1 1 180px',
                                minWidth: 160,
                            }}
                        >
                            <div style={{ fontSize: 11, opacity: 0.7, marginBottom: 2 }}>
                                handle
                            </div>
                            <input
                                type="text"
                                value={newBlogger.handle}
                                onChange={(e) =>
                                    setNewBlogger((prev) => ({
                                        ...prev,
                                        handle: e.target.value,
                                    }))
                                }
                                placeholder="gstv"
                                style={{
                                    padding: '6px 10px',
                                    borderRadius: 999,
                                    border: '1px solid #d1d5db',
                                    fontSize: 13,
                                    width: '100%',
                                }}
                            />
                        </div>

                        <div
                            style={{
                                flex: '1 1 180px',
                                minWidth: 160,
                            }}
                        >
                            <div style={{ fontSize: 11, opacity: 0.7, marginBottom: 2 }}>
                                Имя / название
                            </div>
                            <input
                                type="text"
                                value={newBlogger.name}
                                onChange={(e) =>
                                    setNewBlogger((prev) => ({
                                        ...prev,
                                        name: e.target.value,
                                    }))
                                }
                                placeholder="GSTV"
                                style={{
                                    padding: '6px 10px',
                                    borderRadius: 999,
                                    border: '1px solid #d1d5db',
                                    fontSize: 13,
                                    width: '100%',
                                }}
                            />
                        </div>
                    </div>

                    <div
                        style={{
                            display: 'flex',
                            justifyContent: 'flex-end',
                            marginTop: 4,
                        }}
                    >
                        <button
                            type="submit"
                            style={{
                                padding: '6px 14px',
                                fontSize: 13,
                                borderRadius: 999,
                                border: 'none',
                                background: '#16a34a',
                                color: '#fff',
                                cursor: 'pointer',
                                boxShadow: '0 4px 12px rgba(22,163,74,0.4)',
                            }}
                        >
                            Добавить блогера
                        </button>
                    </div>
                </form>
            </div>

            {/* список блогеров */}
            <div
                style={{
                    background: '#ffffff',
                    borderRadius: 16,
                    padding: 14,
                    boxShadow: '0 10px 30px rgba(15,23,42,0.06)',
                    border: '1px solid #e5e7eb',
                }}
            >
                <div
                    style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: 8,
                    }}
                >
                    <h2 style={{ fontSize: 16, margin: 0 }}>Блогеры</h2>
                    <span style={{ fontSize: 11, opacity: 0.7 }}>
                        Всего: {bloggers.length || 0}
                    </span>
                </div>
                <div
                    style={{
                        maxHeight: 260,
                        overflow: 'auto',
                        paddingRight: 4,
                        marginTop: 6,
                    }}
                >
                    {bloggers.map((b) => {
                        const isLoading = !!loadingIds[b.id]
                        return (
                            <div
                                key={b.id}
                                onClick={() => setSelectedBlogger(b.id)}
                                style={{
                                    borderRadius: 12,
                                    padding: 10,
                                    marginBottom: 8,
                                    border:
                                        selectedBlogger === b.id
                                            ? '1px solid rgba(79,70,229,0.8)'
                                            : '1px solid #e5e7eb',
                                    background:
                                        selectedBlogger === b.id
                                            ? 'linear-gradient(135deg, #eef2ff, #e0f2fe)'
                                            : '#fff',
                                    cursor: 'pointer',
                                    transition: 'all 0.15s ease',
                                }}
                            >
                                <div
                                    style={{
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        gap: 8,
                                        alignItems: 'center',
                                    }}
                                >
                                    <div>
                                        <div style={{ fontSize: 14, fontWeight: 600 }}>
                                            {b.name || b.handle}
                                        </div>
                                        <div
                                            style={{
                                                fontSize: 11,
                                                opacity: 0.7,
                                                marginTop: 2,
                                            }}
                                        >
                                            Платформа: {b.platform} · external_id: {b.external_id}
                                        </div>
                                    </div>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation()
                                            scanBlogger(b.id)
                                        }}
                                        disabled={isLoading}
                                        style={{
                                            padding: '6px 10px',
                                            fontSize: 11,
                                            borderRadius: 999,
                                            border: 'none',
                                            background: isLoading ? '#c7d2fe' : '#4f46e5',
                                            color: '#fff',
                                            cursor: isLoading ? 'default' : 'pointer',
                                            boxShadow: '0 4px 12px rgba(79,70,229,0.5)',
                                            whiteSpace: 'nowrap',
                                        }}
                                    >
                                        {isLoading ? 'Сканирование…' : 'Сканировать'}
                                    </button>
                                </div>
                            </div>
                        )
                    })}
                    {bloggers.length === 0 && (
                        <div style={{ fontSize: 12, opacity: 0.7, marginTop: 8 }}>
                            Пока ни одного блогера. Добавь их через форму выше.
                        </div>
                    )}
                </div>
            </div>

            {/* график активности */}
            <div
                style={{
                    background: '#ffffff',
                    borderRadius: 16,
                    padding: 14,
                    marginTop: 14,
                    boxShadow: '0 10px 30px rgba(15,23,42,0.06)',
                    border: '1px solid #e5e7eb',
                }}
            >
                <div
                    style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: 8,
                    }}
                >
                    <h3 style={{ fontSize: 14, margin: 0 }}>Активность по дням</h3>
                    <span style={{ fontSize: 11, opacity: 0.7 }}>По выбранным фильтрам</span>
                </div>
                <ActivityChart
                    statsByDay={statsByDay}
                    maxCount={maxCount}
                    platformFilter={platformFilter}
                />
            </div>
        </div>
    )
}

function ActivityChart({ statsByDay, maxCount, platformFilter }) {
    if (statsByDay.length === 0) {
        return (
            <div style={{ fontSize: 12, opacity: 0.7 }}>
                Нет данных для графика. Попробуй изменить фильтры или просканировать блогеров.
            </div>
        )
    }

    return (
        <div
            style={{
                display: 'flex',
                alignItems: 'flex-end',
                gap: 8,
                padding: '8px 4px 4px',
                borderRadius: 10,
                background: '#f9fafb',
                border: '1px dashed #e5e7eb',
                height: 150,
            }}
        >
            {statsByDay.map((d) => (
                <div
                    key={d.day}
                    style={{
                        textAlign: 'center',
                        flex: 1,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: 4,
                    }}
                >
                    <div
                        style={{
                            width: '60%',
                            height: `${(d.count / maxCount) * 100}%`,
                            minHeight: 6,
                            borderRadius: 999,
                            background:
                                platformFilter === 'instagram'
                                    ? 'linear-gradient(180deg,#f9a8d4,#ec4899)'
                                    : platformFilter === 'vk'
                                        ? 'linear-gradient(180deg,#93c5fd,#3b82f6)'
                                        : 'linear-gradient(180deg,#6ee7b7,#22c55e)',
                            boxShadow: '0 6px 12px rgba(15,23,42,0.15)',
                            transition: 'height 0.2s ease',
                        }}
                    />
                    <div style={{ fontSize: 10, color: '#6b7280' }}>{d.day.slice(5)}</div>
                    <div style={{ fontSize: 10, opacity: 0.7 }}>{d.count}</div>
                </div>
            ))}
        </div>
    )
}

export default BloggerSection
