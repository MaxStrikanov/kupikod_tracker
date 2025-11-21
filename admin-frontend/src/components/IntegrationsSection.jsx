import React from 'react'

function IntegrationsSection({
    integrations,
    briefForIntegration,
    briefForm,
    setBriefForm,
    briefResult,
    briefLoading,
    openBriefPanel,
    closeBriefPanel,
    runBriefCheck,
    StatusBadge,
}) {
    return (
        <div
            style={{
                background: '#ffffff',
                borderRadius: 16,
                padding: 14,
                boxShadow: '0 10px 30px rgba(15,23,42,0.06)',
                border: '1px solid #e5e7eb',
                display: 'flex',
                flexDirection: 'column',
                gap: 10,
                maxHeight: '80vh',
            }}
        >
            <div
                style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: 4,
                }}
            >
                <h2 style={{ fontSize: 16, margin: 0 }}>Интеграции Kupikod</h2>
                <span style={{ fontSize: 11, opacity: 0.7 }}>
                    Показаны до 100 последних записей
                </span>
            </div>

            <div
                style={{
                    display: 'grid',
                    gridTemplateRows: '1fr auto',
                    gap: 10,
                    height: '100%',
                    minHeight: 0,
                }}
            >
                {/* список интеграций */}
                <div
                    style={{
                        overflow: 'auto',
                        paddingRight: 4,
                    }}
                >
                    {integrations.map((it) => (
                        <div
                            key={it.id}
                            style={{
                                borderBottom: '1px solid #e5e7eb',
                                padding: '8px 4px',
                                background: it.is_ad ? '#ecfdf5' : '#f9fafb',
                                borderRadius: 10,
                                marginBottom: 6,
                            }}
                        >
                            <div
                                style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    fontSize: 11,
                                    opacity: 0.7,
                                }}
                            >
                                <span>
                                    Платформа: {it.post.platform} · Пост ID: {it.post.external_id}
                                </span>
                                <span>
                                    {new Date(
                                        it.post.published_at || it.detected_at,
                                    ).toLocaleDateString()}
                                </span>
                            </div>
                            <div style={{ fontSize: 13, marginTop: 4 }}>
                                {it.post.text.slice(0, 260)}
                                {it.post.text.length > 260 ? '…' : ''}
                            </div>
                            <div style={{ fontSize: 12, marginTop: 4 }}>
                                <strong>Реклама:</strong>{' '}
                                {it.is_ad ? 'да (детектор считает, что это реклама)' : 'скорее нет'} ·{' '}
                                <strong>Уверенность:</strong> {it.confidence}%
                            </div>
                            {it.promo_codes.length > 0 && (
                                <div style={{ fontSize: 12, marginTop: 2 }}>
                                    <strong>Промокоды:</strong> {it.promo_codes.join(', ')}
                                </div>
                            )}
                            <div
                                style={{ marginTop: 6, display: 'flex', justifyContent: 'flex-end' }}
                            >
                                <button
                                    onClick={() => openBriefPanel(it)}
                                    style={{
                                        padding: '4px 10px',
                                        fontSize: 11,
                                        borderRadius: 999,
                                        border: '1px solid #d1d5db',
                                        background: '#ffffff',
                                        cursor: 'pointer',
                                    }}
                                >
                                    Проверить ТЗ
                                </button>
                            </div>
                        </div>
                    ))}
                    {integrations.length === 0 && (
                        <div style={{ fontSize: 12, opacity: 0.7, marginTop: 8 }}>
                            Интеграций по текущим фильтрам не найдено.
                            Попробуй изменить фильтры или просканировать блогеров.
                        </div>
                    )}
                </div>

                {/* панель проверки ТЗ */}
                {briefForIntegration && (
                    <BriefPanel
                        briefForIntegration={briefForIntegration}
                        briefForm={briefForm}
                        setBriefForm={setBriefForm}
                        briefResult={briefResult}
                        briefLoading={briefLoading}
                        closeBriefPanel={closeBriefPanel}
                        runBriefCheck={runBriefCheck}
                        StatusBadge={StatusBadge}
                    />
                )}
            </div>
        </div>
    )
}

function BriefPanel({
    briefForIntegration,
    briefForm,
    setBriefForm,
    briefResult,
    briefLoading,
    closeBriefPanel,
    runBriefCheck,
    StatusBadge,
}) {
    return (
        <div
            style={{
                borderTop: '1px solid #e5e7eb',
                paddingTop: 8,
                marginTop: 4,
            }}
        >
            <div
                style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: 6,
                }}
            >
                <div>
                    <div style={{ fontSize: 13, fontWeight: 600 }}>
                        Проверка ТЗ для интеграции #{briefForIntegration.id}
                    </div>
                    <div style={{ fontSize: 11, opacity: 0.7 }}>
                        Пост ID: {briefForIntegration.post.external_id} · платформа:{' '}
                        {briefForIntegration.post.platform}
                    </div>
                </div>
                <button
                    onClick={closeBriefPanel}
                    style={{
                        border: 'none',
                        background: 'transparent',
                        cursor: 'pointer',
                        fontSize: 18,
                        lineHeight: 1,
                        opacity: 0.6,
                    }}
                >
                    ×
                </button>
            </div>

            <div
                style={{
                    display: 'grid',
                    gridTemplateColumns: '1.2fr 1.3fr',
                    gap: 10,
                }}
            >
                {/* форма */}
                <div>
                    <div style={{ fontSize: 11, opacity: 0.7, marginBottom: 2 }}>
                        Транскрипт интеграции
                    </div>
                    <textarea
                        value={briefForm.transcript}
                        onChange={(e) =>
                            setBriefForm((prev) => ({
                                ...prev,
                                transcript: e.target.value,
                            }))
                        }
                        rows={4}
                        placeholder="Вставь сюда текст, как блогер проговаривает интеграцию..."
                        style={{
                            width: '100%',
                            padding: '6px 8px',
                            borderRadius: 8,
                            border: '1px solid #d1d5db',
                            fontSize: 12,
                            resize: 'vertical',
                        }}
                    />

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
                            value={briefForm.duration_seconds}
                            placeholder="например, 600"
                            onChange={(v) =>
                                setBriefForm((prev) => ({ ...prev, duration_seconds: v }))
                            }
                        />
                        <SmallNumberField
                            label="Интеграция с, сек"
                            value={briefForm.integration_start}
                            placeholder="120"
                            onChange={(v) =>
                                setBriefForm((prev) => ({ ...prev, integration_start: v }))
                            }
                        />
                        <SmallNumberField
                            label="до, сек"
                            value={briefForm.integration_end}
                            placeholder="210"
                            onChange={(v) =>
                                setBriefForm((prev) => ({ ...prev, integration_end: v }))
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
                            value={briefForm.first_description_line}
                            onChange={(e) =>
                                setBriefForm((prev) => ({
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
                            value={briefForm.description}
                            onChange={(e) =>
                                setBriefForm((prev) => ({
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
                            gap: 8,
                        }}
                    >
                        <button
                            type="button"
                            onClick={runBriefCheck}
                            disabled={briefLoading}
                            style={{
                                padding: '6px 14px',
                                fontSize: 12,
                                borderRadius: 999,
                                border: 'none',
                                background: briefLoading ? '#c7d2fe' : '#4f46e5',
                                color: '#fff',
                                cursor: briefLoading ? 'default' : 'pointer',
                                boxShadow: '0 4px 12px rgba(79,70,229,0.5)',
                            }}
                        >
                            {briefLoading ? 'Проверка…' : 'Запустить проверку ТЗ'}
                        </button>
                    </div>
                </div>

                {/* результат проверки */}
                <div
                    style={{
                        borderRadius: 10,
                        border: '1px dashed #e5e7eb',
                        padding: 8,
                        background: '#f9fafb',
                        overflow: 'auto',
                        maxHeight: 230,
                    }}
                >
                    {!briefResult && (
                        <div style={{ fontSize: 12, opacity: 0.7 }}>
                            Вставь транскрипт и запусти проверку, чтобы увидеть анализ соответствия ТЗ
                            Kupikod.
                        </div>
                    )}

                    {briefResult && (
                        <div style={{ fontSize: 12 }}>
                            <div
                                style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    marginBottom: 4,
                                }}
                            >
                                <div
                                    style={{
                                        display: 'inline-flex',
                                        alignItems: 'center',
                                        gap: 6,
                                    }}
                                >
                                    <StatusBadge status={briefResult.overall_status} />
                                    <span style={{ fontSize: 11, opacity: 0.8 }}>
                                        Итог: {briefResult.overall_status}
                                    </span>
                                </div>
                            </div>
                            {briefResult.summary && (
                                <div style={{ marginBottom: 6 }}>
                                    <strong>Резюме:</strong> {briefResult.summary}
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
                                    {Object.entries(briefResult.checks || {}).map(([key, val]) => (
                                        <React.Fragment key={key}>
                                            <div style={{ fontSize: 11, opacity: 0.9 }}>
                                                {key}
                                                {val?.comment ? `: ${val.comment}` : ''}
                                            </div>
                                            <div style={{ fontSize: 11 }}>
                                                {val?.ok ? '✅ ок' : '⚠️ нет'}
                                            </div>
                                        </React.Fragment>
                                    ))}
                                </div>
                            </div>

                            {briefResult.recommended_edits &&
                                briefResult.recommended_edits.length > 0 && (
                                    <div>
                                        <strong>Рекомендуемые правки для блогера:</strong>
                                        <ul
                                            style={{
                                                marginTop: 4,
                                                paddingLeft: 16,
                                                maxHeight: 80,
                                                overflow: 'auto',
                                            }}
                                        >
                                            {briefResult.recommended_edits.map((item, idx) => (
                                                <li key={idx} style={{ fontSize: 11, marginBottom: 2 }}>
                                                    {item}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                        </div>
                    )}
                </div>
            </div>
        </div>
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

export default IntegrationsSection
