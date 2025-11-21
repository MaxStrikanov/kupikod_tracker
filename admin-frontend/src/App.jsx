import React, { useEffect, useMemo, useState } from 'react'

import Toast from './components/Toast'
import StatusBadge from './components/StatusBadge'
import MetricCard from './components/MetricCard'
import FilterBlock from './components/FilterBlock'
import LinkCheckSection from './components/LinkCheckSection'
import BloggerSection from './components/BloggerSection'
import IntegrationsSection from './components/IntegrationsSection'

const API_BASE = 'http://localhost:8000'

function App() {
  const [bloggers, setBloggers] = useState([])
  const [integrations, setIntegrations] = useState([])
  const [loadingIds, setLoadingIds] = useState({})
  const [selectedBlogger, setSelectedBlogger] = useState(null)
  const [platformFilter, setPlatformFilter] = useState('all')

  const [toast, setToast] = useState(null)

  const [newBlogger, setNewBlogger] = useState({
    platform: 'vk',
    external_id: '',
    handle: '',
    name: '',
  })

  // проверка ТЗ для интеграции из базы
  const [briefForIntegration, setBriefForIntegration] = useState(null)
  const [briefForm, setBriefForm] = useState({
    transcript: '',
    description: '',
    duration_seconds: '',
    integration_start: '',
    integration_end: '',
    first_description_line: '',
  })
  const [briefResult, setBriefResult] = useState(null)
  const [briefLoading, setBriefLoading] = useState(false)

  // проверка по ссылке
  const [linkForm, setLinkForm] = useState({
    url: '',
    transcript: '',
    description: '',
    duration_seconds: '',
    integration_start: '',
    integration_end: '',
    first_description_line: '',
  })
  const [linkLoading, setLinkLoading] = useState(false)
  const [linkResult, setLinkResult] = useState(null)

  const isAnythingLoading = useMemo(
    () => Object.values(loadingIds).some(Boolean),
    [loadingIds],
  )

  const showToast = (type, message) => {
    setToast({ type, message })
    setTimeout(() => {
      setToast((current) => (current?.message === message ? null : current))
    }, 4000)
  }

  const loadBloggers = async () => {
    const res = await fetch(`${API_BASE}/bloggers/`)
    const data = await res.json()
    setBloggers(data)
  }

  const loadIntegrations = async () => {
    const res = await fetch(`${API_BASE}/integrations/kupikod`)
    const data = await res.json()
    setIntegrations(data)
    return data
  }

  const scanBlogger = async (id) => {
    if (loadingIds[id]) return

    setLoadingIds((prev) => ({ ...prev, [id]: true }))
    try {
      const beforeCount = integrations.filter((it) => it.post.blogger_id === id).length

      const res = await fetch(`${API_BASE}/integrations/kupikod/scan/${id}`, {
        method: 'POST',
      })

      if (!res.ok) {
        const text = await res.text()
        showToast('error', `Ошибка при сканировании: ${res.status} ${text || ''}`)
        return
      }

      const data = await loadIntegrations()
      const afterCount = data.filter((it) => it.post.blogger_id === id).length
      const diff = afterCount - beforeCount

      if (diff > 0) {
        showToast(
          'success',
          `Сканирование завершено: найдено ${diff} новых интеграций у блогера #${id}`,
        )
      } else {
        showToast('info', 'Сканирование завершено: новых интеграций не найдено')
      }
    } catch (e) {
      console.error(e)
      showToast('error', 'Не удалось выполнить запрос. Проверь API и сеть.')
    } finally {
      setLoadingIds((prev) => ({ ...prev, [id]: false }))
    }
  }

  const addBlogger = async (e) => {
    e.preventDefault()
    if (!newBlogger.external_id.trim()) {
      showToast('error', 'Укажи external_id (для VK — id или -id паблика)')
      return
    }
    if (!newBlogger.platform) {
      showToast('error', 'Выбери платформу')
      return
    }

    try {
      const res = await fetch(`${API_BASE}/bloggers/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newBlogger),
      })

      if (!res.ok) {
        const text = await res.text()
        showToast('error', `Не удалось добавить блогера: ${res.status} ${text || ''}`)
        return
      }

      const created = await res.json()
      setBloggers((prev) => [...prev, created])
      setNewBlogger({
        platform: 'vk',
        external_id: '',
        handle: '',
        name: '',
      })
      showToast(
        'success',
        `Блогер «${created.name || created.handle || created.id}» успешно добавлен`,
      )
    } catch (err) {
      console.error(err)
      showToast('error', 'Ошибка сети при добавлении блогера')
    }
  }

  useEffect(() => {
    loadBloggers()
    loadIntegrations()
  }, [])

  const filteredIntegrations = useMemo(() => {
    return integrations.filter((it) => {
      if (selectedBlogger && it.post.blogger_id !== selectedBlogger) return false
      if (platformFilter !== 'all' && it.post.platform !== platformFilter) return false
      return true
    })
  }, [integrations, selectedBlogger, platformFilter])

  const stats = useMemo(() => {
    if (filteredIntegrations.length === 0) {
      return {
        total: 0,
        ads: 0,
        avgConfidence: 0,
        byDay: [],
      }
    }
    const total = filteredIntegrations.length
    const ads = filteredIntegrations.filter((i) => i.is_ad).length
    const avgConfidence =
      filteredIntegrations.reduce((sum, i) => sum + i.confidence, 0) / total

    const byDayMap = {}
    filteredIntegrations.forEach((i) => {
      const dt = new Date(i.detected_at || i.post.published_at)
      const key = dt.toISOString().slice(0, 10)
      byDayMap[key] = (byDayMap[key] || 0) + 1
    })
    const byDay = Object.entries(byDayMap)
      .sort(([a], [b]) => (a < b ? -1 : 1))
      .map(([day, count]) => ({ day, count }))

    return { total, ads, avgConfidence: Math.round(avgConfidence), byDay }
  }, [filteredIntegrations])

  const maxCount = stats.byDay.reduce((m, d) => Math.max(m, d.count), 0) || 1

  // открытие / закрытие панели проверки ТЗ по интеграции
  const openBriefPanel = (integration) => {
    setBriefForIntegration(integration)
    setBriefResult(null)
    setBriefForm({
      transcript: '',
      description: integration.post.text || '',
      duration_seconds: '',
      integration_start: '',
      integration_end: '',
      first_description_line: '',
    })
  }

  const closeBriefPanel = () => {
    setBriefForIntegration(null)
    setBriefResult(null)
    setBriefLoading(false)
  }

  const runBriefCheck = async () => {
    if (!briefForIntegration) return
    if (!briefForm.transcript.trim()) {
      showToast('error', 'Нужен транскрипт интеграции, без него модель не поймёт контекст')
      return
    }

    setBriefLoading(true)
    try {
      const body = {
        transcript: briefForm.transcript,
        description: briefForm.description || '',
        duration_seconds: briefForm.duration_seconds
          ? Number(briefForm.duration_seconds)
          : null,
        integration_start: briefForm.integration_start
          ? Number(briefForm.integration_start)
          : null,
        integration_end: briefForm.integration_end
          ? Number(briefForm.integration_end)
          : null,
        first_description_line: briefForm.first_description_line || null,
      }

      const res = await fetch(
        `${API_BASE}/integrations/kupikod/${briefForIntegration.id}/brief-check`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        },
      )

      if (!res.ok) {
        const text = await res.text()
        showToast('error', `Ошибка проверки ТЗ: ${res.status} ${text || ''}`)
        return
      }

      const data = await res.json()
      setBriefResult(data)
      showToast('success', 'Проверка ТЗ выполнена')
    } catch (e) {
      console.error(e)
      showToast('error', 'Не удалось вызвать проверку ТЗ (DeepSeek)')
    } finally {
      setBriefLoading(false)
    }
  }

  // проверка по ссылке
  const runLinkCheck = async () => {
    if (!linkForm.url.trim()) {
      showToast('error', 'Вставь ссылку на видео VK или Instagram')
      return
    }

    setLinkLoading(true)
    setLinkResult(null)
    try {
      const body = {
        url: linkForm.url,
        transcript: linkForm.transcript || '',
        description: linkForm.description || '',
        duration_seconds: linkForm.duration_seconds
          ? Number(linkForm.duration_seconds)
          : null,
        integration_start: linkForm.integration_start
          ? Number(linkForm.integration_start)
          : null,
        integration_end: linkForm.integration_end
          ? Number(linkForm.integration_end)
          : null,
        first_description_line: linkForm.first_description_line || null,
      }

      const res = await fetch(`${API_BASE}/integrations/kupikod/link-check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      if (!res.ok) {
        const text = await res.text()
        showToast('error', `Ошибка анализа ссылки: ${res.status} ${text || ''}`)
        return
      }

      const data = await res.json()
      setLinkResult(data)

      if (!data.has_kupikod_integration) {
        showToast('info', 'Интеграция Kupikod в этом видео не обнаружена (по тексту)')
      } else if (!data.brief) {
        showToast(
          'info',
          'Kupikod найден, но для проверки ТЗ нужен транскрипт интеграции. Заполни его и перезапусти.',
        )
      } else {
        showToast('success', 'Интеграция Kupikod найдена и проверена по ТЗ')
      }
    } catch (e) {
      console.error(e)
      showToast('error', 'Не удалось проанализировать ссылку')
    } finally {
      setLinkLoading(false)
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        background:
          'radial-gradient(circle at top left, #eef2ff 0, transparent 55%), radial-gradient(circle at bottom right, #ecfeff 0, transparent 55%), #f9fafb',
        fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
        color: '#0f172a',
      }}
    >
      <div style={{ maxWidth: 1300, margin: '0 auto', padding: '20px 20px 40px' }}>
        <header
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: 16,
          }}
        >
          <div>
            <h1 style={{ fontSize: 26, margin: 0 }}>Kupikod Monitor</h1>
            <p style={{ margin: '4px 0 0', fontSize: 13, opacity: 0.75 }}>
              Отслеживание и проверка рекламных интеграций Kupikod у блогеров (VK +
              Instagram).
            </p>
          </div>
          <div
            style={{
              fontSize: 12,
              padding: '6px 10px',
              borderRadius: 999,
              background: '#eef2ff',
              color: '#4338ca',
              border: '1px solid rgba(129,140,248,0.5)',
            }}
          >
            {isAnythingLoading ? 'Сканирование в процессе…' : 'Готов к сканированию'}
          </div>
        </header>

        {/* секция проверки по ссылке */}
        <LinkCheckSection
          linkForm={linkForm}
          setLinkForm={setLinkForm}
          linkLoading={linkLoading}
          linkResult={linkResult}
          onRunLinkCheck={runLinkCheck}
        />

        {/* метрики */}
        <section
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, minmax(0, 1fr))',
            gap: 16,
            marginTop: 20,
          }}
        >
          <MetricCard
            title="Всего интеграций"
            value={stats.total}
            subtitle="С учётом выбранных фильтров"
            icon="📊"
          />
          <MetricCard
            title="Рекламных интеграций"
            value={stats.ads}
            subtitle="is_ad = true"
            icon="🎯"
          />
          <MetricCard
            title="Средняя уверенность"
            value={`${stats.avgConfidence}%`}
            subtitle="Оценка детектора + ML"
            icon="🤖"
          />
        </section>

        {/* фильтры */}
        <section
          style={{
            display: 'flex',
            gap: 16,
            alignItems: 'center',
            marginTop: 18,
            flexWrap: 'wrap',
          }}
        >
          <FilterBlock label="Платформа">
            <select
              value={platformFilter}
              onChange={(e) => setPlatformFilter(e.target.value)}
              style={selectStyle}
            >
              <option value="all">Все</option>
              <option value="vk">VK</option>
              <option value="instagram">Instagram</option>
            </select>
          </FilterBlock>

          <FilterBlock label="Блогер">
            <select
              value={selectedBlogger || ''}
              onChange={(e) =>
                setSelectedBlogger(e.target.value ? Number(e.target.value) : null)
              }
              style={{ ...selectStyle, minWidth: 220 }}
            >
              <option value="">Все блогеры</option>
              {bloggers.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name || b.handle} ({b.platform})
                </option>
              ))}
            </select>
          </FilterBlock>
        </section>

        {/* основная сетка */}
        <section
          style={{
            marginTop: 24,
            display: 'grid',
            gridTemplateColumns: '1.1fr 2fr',
            gap: 20,
          }}
        >
          <BloggerSection
            bloggers={bloggers}
            newBlogger={newBlogger}
            setNewBlogger={setNewBlogger}
            addBlogger={addBlogger}
            selectedBlogger={selectedBlogger}
            setSelectedBlogger={setSelectedBlogger}
            loadingIds={loadingIds}
            scanBlogger={scanBlogger}
            statsByDay={stats.byDay}
            maxCount={maxCount}
            platformFilter={platformFilter}
          />

          <IntegrationsSection
            integrations={filteredIntegrations}
            briefForIntegration={briefForIntegration}
            briefForm={briefForm}
            setBriefForm={setBriefForm}
            briefResult={briefResult}
            briefLoading={briefLoading}
            openBriefPanel={openBriefPanel}
            closeBriefPanel={closeBriefPanel}
            runBriefCheck={runBriefCheck}
            StatusBadge={StatusBadge}
          />
        </section>
      </div>

      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  )
}

const selectStyle = {
  padding: '6px 10px',
  borderRadius: 999,
  border: '1px solid #d1d5db',
  fontSize: 13,
  background: '#ffffff',
}

export default App
