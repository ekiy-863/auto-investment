// 颜色
const colors = ['#22c55e', '#ef4444', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

// 加载数据
async function loadData() {
    try {
        const resp = await fetch('../data/dashboard.json?t=' + Date.now());
        if (!resp.ok) throw new Error('数据加载失败');
        const data = await resp.json();
        renderAll(data);
        document.getElementById('updateTime').textContent = '更新时间：' + (data.update_time || new Date().toLocaleString());
    } catch (e) {
        console.warn('加载数据失败:', e);
        document.getElementById('updateTime').textContent = '⚠️ 数据加载失败，使用模拟数据';
        loadMockData();
    }
}

// 渲染所有
function renderAll(data) {
    // 账户汇总
    const totalCost = document.getElementById('totalCost');
    totalCost.textContent = data.total_cost ? '¥' + data.total_cost.toFixed(2) : '--';
    const totalMarket = document.getElementById('totalMarket');
    totalMarket.textContent = data.total_market ? '¥' + data.total_market.toFixed(2) : '--';
    const totalPnl = document.getElementById('totalPnl');
    if (data.total_pnl !== undefined && data.total_pnl !== null) {
        totalPnl.textContent = (data.total_pnl >= 0 ? '+' : '') + data.total_pnl.toFixed(2);
        totalPnl.className = 'value ' + (data.total_pnl >= 0 ? 'positive' : 'negative');
    }
    const totalPnlRatio = document.getElementById('totalPnlRatio');
    if (data.total_pnl_ratio !== undefined && data.total_pnl_ratio !== null) {
        totalPnlRatio.textContent = (data.total_pnl_ratio >= 0 ? '+' : '') + data.total_pnl_ratio.toFixed(2) + '%';
        totalPnlRatio.className = 'value ' + (data.total_pnl_ratio >= 0 ? 'positive' : 'negative');
    }

    renderIndexes(data.indexes);
    renderHoldings(data.holdings);
    renderETF(data.etf);
    renderSector(data.sector);
    renderCharts(data.holdings);
}

function renderIndexes(indexes) {
    if (!indexes) return;
    const map = {};
    indexes.forEach(idx => map[idx.name] = idx);
    const list = ['上证指数', '深证成指', '创业板指', '科创50'];
    list.forEach(name => {
        const d = map[name] || { price: '--', change_pct: 0 };
        const id = name === '上证指数' ? 'sh' : name === '深证成指' ? 'sz' : name === '创业板指' ? 'cy' : 'kc';
        document.getElementById('idx_' + id).textContent = d.price || '--';
        const changeEl = document.getElementById('idx_' + id + '_change');
        const change = d.change_pct || 0;
        changeEl.textContent = (change >= 0 ? '+' : '') + change.toFixed(2) + '%';
        changeEl.className = 'idx-change ' + (change >= 0 ? 'positive' : 'negative');
    });
}

function renderHoldings(holdings) {
    const tbody = document.getElementById('holdingsBody');
    if (!holdings || holdings.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8">暂无持仓数据</td></tr>';
        return;
    }
    tbody.innerHTML = holdings.map(h => `
        <tr>
            <td>${h.name || h.code}</td>
            <td>${h.shares || 0}</td>
            <td>${h.cost_nav ? h.cost_nav.toFixed(4) : '--'}</td>
            <td>${h.current_nav ? h.current_nav.toFixed(4) : '--'}</td>
            <td>${h.market_value ? h.market_value.toFixed(2) : '--'}</td>
            <td class="${h.pnl >= 0 ? 'positive' : 'negative'}">${h.pnl !== undefined && h.pnl !== null ? (h.pnl >= 0 ? '+' : '') + h.pnl.toFixed(2) : '--'}</td>
            <td class="${h.pnl_ratio >= 0 ? 'positive' : 'negative'}">${h.pnl_ratio !== undefined && h.pnl_ratio !== null ? (h.pnl_ratio >= 0 ? '+' : '') + h.pnl_ratio.toFixed(2) + '%' : '--'}</td>
            <td class="${h.change_today >= 0 ? 'positive' : 'negative'}">${h.change_today !== undefined && h.change_today !== null ? (h.change_today >= 0 ? '+' : '') + h.change_today.toFixed(2) + '%' : '--'}</td>
        </tr>
    `).join('');
}

function renderETF(etf) {
    const tbody = document.getElementById('etfBody');
    if (!etf || etf.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4">暂无数据</td></tr>';
        return;
    }
    tbody.innerHTML = etf.slice(0, 5).map(e => `
        <tr>
            <td>${e.code || '--'}</td>
            <td>${e.name || '--'}</td>
            <td>${e.price !== undefined ? e.price.toFixed(3) : '--'}</td>
            <td class="${e.change_pct >= 0 ? 'positive' : 'negative'}">${e.change_pct !== undefined ? (e.change_pct >= 0 ? '+' : '') + e.change_pct.toFixed(2) + '%' : '--'}</td>
        </tr>
    `).join('');
}

function renderSector(sector) {
    const inflowBody = document.getElementById('sectorInflowBody');
    const outflowBody = document.getElementById('sectorOutflowBody');
    
    if (sector && sector.top_inflow && sector.top_inflow.length > 0) {
        inflowBody.innerHTML = sector.top_inflow.map(s => `
            <tr><td>${s.name}</td><td class="${s.inflow >= 0 ? 'positive' : 'negative'}">${s.inflow >= 0 ? '+' : ''}${s.inflow.toFixed(2)}</td></tr>
        `).join('');
    } else {
        inflowBody.innerHTML = '<tr><td colspan="2">暂无数据</td></tr>';
    }
    
    if (sector && sector.top_outflow && sector.top_outflow.length > 0) {
        outflowBody.innerHTML = sector.top_outflow.map(s => `
            <tr><td>${s.name}</td><td class="${s.inflow >= 0 ? 'positive' : 'negative'}">${s.inflow >= 0 ? '+' : ''}${s.inflow.toFixed(2)}</td></tr>
        `).join('');
    } else {
        outflowBody.innerHTML = '<tr><td colspan="2">暂无数据</td></tr>';
    }
}

function renderCharts(holdings) {
    if (!holdings || holdings.length === 0) return;
    const filtered = holdings.filter(h => h.shares > 0 && h.pnl !== undefined && h.pnl !== null);
    if (filtered.length === 0) return;

    // 盈亏柱状图
    const pnlChart = echarts.init(document.getElementById('pnlChart'));
    pnlChart.setOption({
        tooltip: { trigger: 'axis', formatter: p => p[0].name + '<br/>盈亏：' + p[0].value.toFixed(2) },
        grid: { left: 60, right: 20, top: 20, bottom: 40 },
        xAxis: { type: 'category', data: filtered.map(h => h.name || h.code), axisLabel: { rotate: 15, fontSize: 10 } },
        yAxis: { type: 'value', axisLabel: { formatter: v => v.toFixed(0) } },
        series: [{
            type: 'bar',
            data: filtered.map(h => ({ value: h.pnl, itemStyle: { color: h.pnl >= 0 ? '#ef4444' : '#22c55e' } })),
            barWidth: '40%'
        }]
    });
    window.addEventListener('resize', () => pnlChart.resize());

    // 持仓占比饼图
    const pieData = filtered.filter(h => h.market_value > 0).map((h, i) => ({
        name: h.name || h.code,
        value: h.market_value,
        itemStyle: { color: colors[i % colors.length] }
    }));
    if (pieData.length > 0) {
        const pieChart = echarts.init(document.getElementById('pieChart'));
        pieChart.setOption({
            tooltip: { trigger: 'item', formatter: '{b}<br/>市值：¥{c} 元<br/>占比：{d}%' },
            legend: { orient: 'vertical', right: 10, top: 10, itemWidth: 12, itemHeight: 12, textStyle: { fontSize: 10 } },
            series: [{
                type: 'pie',
                radius: ['40%', '70%'],
                center: ['45%', '50%'],
                data: pieData,
                label: { show: true, formatter: '{d}%', fontSize: 11 },
                labelLine: { length: 10, length2: 8 }
            }]
        });
        window.addEventListener('resize', () => pieChart.resize());
    }
}

// 模拟数据（备选）
function loadMockData() {
    const mock = {
        update_time: new Date().toLocaleString(),
        total_cost: 50000,
        total_market: 48000,
        total_pnl: -2000,
        total_pnl_ratio: -4.00,
        indexes: [
            { name: '上证指数', price: 3955.58, change_pct: -0.29 },
            { name: '深证成指', price: 14779.40, change_pct: -0.97 },
            { name: '创业板指', price: 3804.70, change_pct: -1.21 },
            { name: '科创50', price: 1924.27, change_pct: -4.25 }
        ],
        holdings: [
            { code: '024418', name: '华夏半导体C', shares: 10000, cost_nav: 1.2500, current_nav: 1.1745, market_value: 11745, pnl: -755, pnl_ratio: -6.04, change_today: -6.10 },
            { code: '024975', name: '华泰柏瑞半导体C', shares: 5000, cost_nav: 1.3800, current_nav: 1.2962, market_value: 6481, pnl: -419, pnl_ratio: -6.07, change_today: -6.10 },
            { code: '025500', name: '东方阿尔法科技C', shares: 8000, cost_nav: 0.9200, current_nav: 0.8602, market_value: 6881, pnl: -478, pnl_ratio: -6.50, change_today: -6.50 }
        ],
        etf: [
            { code: '516770.SH', name: '游戏ETF华泰柏瑞', price: 1.172, change_pct: 0.06 },
            { code: '159869.SZ', name: '游戏ETF华夏', price: 1.117, change_pct: 0.06 }
        ],
        sector: {
            top_inflow: [{ name: '医药生物', inflow: 95.60 }],
            top_outflow: [{ name: '电子', inflow: -406.81 }]
        }
    };
    renderAll(mock);
    document.getElementById('updateTime').textContent = '⚠️ 模拟数据（实际数据加载失败）';
}

// 启动
loadData();
// 每60秒刷新
setInterval(loadData, 60000);
