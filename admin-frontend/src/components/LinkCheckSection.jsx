import React from 'react'
import StatusBadge from './StatusBadge'

function LinkCheckSection({
    linkForm,
    setLinkForm,
    linkLoading,
    linkResult,
    onRunLinkCheck,
}) {
    return (
        <section
            style={{
                marginTop: 16,
                display: 'grid',
                gridTemplateColumns: '1.7fr 1.3fr',
                gap: 16,
            }}
        >
            <div
                style={{
                    background: '#ffffff',
                    borderRadius: 16,
                    padding: 14,
                    boxShadow: '0 10px 30px rgba(15,23,42,0.06)',
                    border: '1px solid #e5e7eb',
                }}
            >
                <h2 style={{ fontSize: 16, margin: 0 }}>Проверка видео по ссылке</h2>
                <p style={{ fontSize: 11, opacity: 0.7, marginTop: 4 }}>
                    Вставь ссылку на видео VK или Instagram. По тексту интеграции проверим,
                    есть ли Kupikod и насколько интеграция соответствует ТЗ.
                </p>

                <div style={{ marginTop: 8 }}>
                    <div style={{ fontSize: 11, opacity: 0.7, marginBottom: 2 }}>Ссылка</div>
                    <input
                        type="text"
                        value={linkForm.url}
                        onChange={(e) =>
                            setLinkForm((prev) => ({ ...prev, url: e.target.value }))
                        }
                        placeholder="https://vk.com/video-123_456 или https://www.instagram.com/reel/..."
                        style={{
                            width: '100%',
                            padding: '6px 10px',
                            borderRadius: 999,
                            border: '1px solid #d1d5db',
                            fontSize: 12,
                        }}
                    />
                </div>

                <div style={{ marginTop: 8 }}>
                    <div style={{ fontSize: 11, opacity: 0.7, marginBottom: 2 }}>
                        Транскрипт интеграции (речь блогера во время рекламы)
                    </div>
                    <textarea
                        value={linkForm.transcript}
                        onChange={(e) =>
                            setLinkForm((prev) => ({ ...prev, transcript: e.target.value }))
                        }
                        rows={4}
                        placeholder="Вставь сюда текст интеграции (можно из транскрибации). Это нужно для проверки ТЗ."
                        style={{
                            width: '100%',
                            padding: '6px 8px',
                            borderRadius: 8,
                            border: '1px solid #d1d5db',
                            fontSize: 12,
                            resize: 'vertical',
                        }}
                    />
                </div>

                <div
                    style={{
                        display: 'flex',
                        gap: 8,
                        marginTop: 6,
                        flexWrap: 'wrap',
                    }}
                >
                    <SmallNumberField
                        label="Длительность ролика, сек"
                        value={linkForm.duration_seconds}
                        placeholder="например, 600"
                        onChange={(v) =>
                            setLinkForm((prev) => ({ ...prev, duration_seconds: v }))
                        }
                    />
                    <SmallNumberField
                        label="Интеграция с, сек"
                        value={linkForm.integration_start}
                        placeholder="120"
                        onChange={(v) =>
                            setLinkForm((prev) => ({ ...prev, integration_start: v }))
                        }
                    />
                    <SmallNumberField
                        label="до, сек"
                        value={linkForm.integration_end}
                        placeholder="210"
                        onChange={(v) =>
                            setLinkForm((prev) => ({ ...prev, integration_end: v }))
                        }
                    />
                </div>

                <div style={{ marginTop: 6 }}>
                    <div
                        style={{
                            fontSize: 11,
                            opacity: 0.7,
                            marginBottom: 2,
                        }}
                    >
                        Первая строка описания под видео
                    </div>
                    <input
                        type="text"
                        value={linkForm.first_description_line}
                        onChange={(e) =>
                            setLinkForm((prev) => ({
                                ...prev,
                                first_description_line: e.target.value,
                            }))
                        }
                        placeholder="[ТВОЯ ССЫЛКА]: 0% комиссия на пополнение Steam - Kupikod!"
                        style={{
                            width: '100%',
                            padding: '4px 8px',
                            borderRadius: 999,
                            border: '1px solid #d1d5db',
                            fontSize: 12,
                        }}
                    />
                </div>

                <div style={{ marginTop: 6 }}>
                    <div
                        style={{
                            fontSize: 11,
                            opacity: 0.7,
                            marginBottom: 2,
                        }}
                    >
                        Описание ролика (опционально)
                    </div>
                    <textarea
                        value={linkForm.description}
                        onChange={(e) =>
                            setLinkForm((prev) => ({
                                ...prev,
                                description: e.target.value,
                            }))
                        }
                        rows={2}
                        style={{
                            width: '100%',
                            padding: '4px 8px',
                            borderRadius: 8,
                            border: '1px solid #d1d5db',
                            fontSize: 12,
                            resize: 'vertical',
                        }}
                    />
                </div>

                <div
                    style={{
                        display: 'flex',
                        justifyContent: 'flex-end',
                        marginTop: 8,
                    }}
                >
                    <button
                        type="button"
                        onClick={onRunLinkCheck}
                        disabled={linkLoading}
                        style={{
                            padding: '6px 14px',
                            fontSize: 12,
                            borderRadius: 999,
                            border: 'none',
                            background: linkLoading ? '#c7d2fe' : '#4f46e5',
                            color: '#fff',
                            cursor: linkLoading ? 'default' : 'pointer',
                            boxShadow: '0 4px 12px rgba(79,70,229,0.5)',
                        }}
                    >
                        {linkLoading ? 'Анализ…' : 'Проверить видео по ссылке'}
                    </button>
                </div>
            </div>

            {/* правая половина: результат по ссылке */}
            <div
                style={{
                    background: '#ffffff',
                    borderRadius: 16,
                    padding: 14,
                    boxShadow: '0 10px 30px rgba(15,23,42,0.06)',
                    border: '1px solid #e5e7eb',
                }}
            >
                <h3 style={{ fontSize: 14, margin: 0 }}>Результат по ссылке</h3>
                <div style={{ fontSize: 12, marginTop: 6 }}>
                    {!linkResult && (
                        <div style={{ opacity: 0.7 }}>
                            Пока ничего не проверено. Вставь ссылку, заполни транскрипт и запусти
                            анализ.
                        </div>
                    )}

                    {linkResult && (
                        <>
                            <div style={{ marginBottom: 6 }}>
                                <div style={{ fontSize: 11, opacity: 0.7 }}>Платформа / ID</div>
                                <div>
                                    {linkResult.platform || 'не определено'} ·{' '}
                                    {linkResult.external_id || '—'}
                                </div>
                            </div>

                            <div style={{ marginBottom: 6 }}>
                                <div style={{ fontSize: 11, opacity: 0.7 }}>Наличие Kupikod</div>
                                <div>
                                    {linkResult.has_kupikod_integration ? (
                                        <span>✅ Kupikod обнаружен (по тексту)</span>
                                    ) : (
                                        <span>⚪ Не найдено упоминаний Kupikod в переданном тексте</span>
                                    )}
                                </div>
                            </div>

                            {linkResult.brief ? (
                                <div
                                    style={{
                                        marginTop: 8,
                                        paddingTop: 6,
                                        borderTop: '1px solid #e5e7eb',
                                    }}
                                >
                                    <div
                                        style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: 6,
                                            marginBottom: 4,
                                        }}
                                    >
                                        <StatusBadge status={linkResult.brief.overall_status} />
                                        <span style={{ fontSize: 11, opacity: 0.8 }}>
                                            Итог: {linkResult.brief.overall_status}
                                        </span>
                                    </div>
                                    {linkResult.brief.summary && (
                                        <div style={{ marginBottom: 6 }}>
                                            <strong>Резюме:</strong> {linkResult.brief.summary}
                                        </div>
                                    )}

                                    <div style={{ marginBottom: 6 }}>
                                        <strong>Чеки по ТЗ:</strong>
                                        <div
                                            style={{
                                                marginTop: 4,
                                                display: 'grid',
                                                gridTemplateColumns: '1.3fr 0.7fr',
                                                gap: 4,
                                            }}
                                        >
                                            {Object.entries(linkResult.brief.checks || {}).map(
                                                ([key, val]) => (
                                                    <React.Fragment key={key}>
                                                        <div style={{ fontSize: 11, opacity: 0.9 }}>
                                                            {key}
                                                            {val?.comment ? `: ${val.comment}` : ''}
                                                        </div>
                                                        <div style={{ fontSize: 11 }}>
                                                            {val?.ok ? '✅ ок' : '⚠️ нет'}
                                                        </div>
                                                    </React.Fragment>
                                                ),
                                            )}
                                        </div>
                                    </div>

                                    {linkResult.brief.recommended_edits &&
                                        linkResult.brief.recommended_edits.length > 0 && (
                                            <div>
                                                <strong>Рекомендуемые правки:</strong>
                                                <ul
                                                    style={{
                                                        marginTop: 4,
                                                        paddingLeft: 16,
                                                        maxHeight: 90,
                                                        overflow: 'auto',
                                                    }}
                                                >
                                                    {linkResult.brief.recommended_edits.map((item, idx) => (
                                                        <li key={idx} style={{ fontSize: 11, marginBottom: 2 }}>
                                                            {item}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                </div>
                            ) : linkResult.has_kupikod_integration ? (
                                <div style={{ marginTop: 8, opacity: 0.8, fontSize: 11 }}>
                                    Kupikod найден в тексте, но проверка ТЗ не выполнена. Скорее всего не
                                    был передан транскрипт интеграции.
                                </div>
                            ) : null}
                        </>
                    )}
                </div>
            </div>
        </section>
    )
}

function SmallNumberField({ label, value, onChange, placeholder }) {
    return (
        <div style={{ flex: '1 1 120px', minWidth: 100 }}>
            <div
                style={{
                    fontSize: 11,
                    opacity: 0.7,
                    marginBottom: 2,
                }}
            >
                {label}
            </div>
            <input
                type="number"
                min="0"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder={placeholder}
                style={{
                    width: '100%',
                    padding: '4px 8px',
                    borderRadius: 999,
                    border: '1px solid #d1d5db',
                    fontSize: 12,
                }}
            />
        </div>
    )
}

export default LinkCheckSection
