// 存储历史查询数据
const queryHistory = [];
let atQueryHistory = [];

// 新的关系图相关变量
const relationshipChart = document.getElementById('relationshipChart');
const originalCharts = document.getElementById('originalCharts');

const loadingIndicator = document.getElementById('loadingIndicator');
const errorMessage = document.getElementById('errorMessage');
const statisticsContainer = document.getElementById('statisticsContainer');
const methodsContainer = document.getElementById('methodsContainer');

// 初始化新的关系图
const chartDom = document.getElementById('mainChart');
const myChart = echarts.init(chartDom);
const tooltip = document.getElementById('tooltip');

// 关键词搜索相关变量
const keywordSearch = document.getElementById('keywordSearch');
const autocompleteResults = document.getElementById('autocompleteResults');
const searchButton = document.getElementById('searchButton');
let searchTimeout;

// 页面导航相关
document.addEventListener('DOMContentLoaded', function() {
    // 获取所有页面内容
    const homeContent = document.getElementById('homeContent');
    const detailContent = document.getElementById('detailContent');
    const atContent = document.getElementById('atContent');
    
    // 获取导航按钮
    const homeBtn = document.getElementById('homeBtn');
    const detailBtn = document.getElementById('detailBtn');
    const atBtn = document.getElementById('atBtn');

    // 页面切换函数
    function switchPage(page) {
        // 隐藏所有页面
        homeContent.style.display = 'none';
        detailContent.style.display = 'none';
        atContent.style.display = 'none';
        
        // 移除所有按钮的active类
        homeBtn.classList.remove('active');
        detailBtn.classList.remove('active');
        atBtn.classList.remove('active');
        
        // 显示选中的页面
        page.style.display = 'block';
        
        // 添加active类到当前按钮
        if (page === homeContent) homeBtn.classList.add('active');
        if (page === detailContent) detailBtn.classList.add('active');
        if (page === atContent) atBtn.classList.add('active');
    }

    // 添加按钮点击事件
    homeBtn.addEventListener('click', () => switchPage(homeContent));
    detailBtn.addEventListener('click', () => switchPage(detailContent));
    atBtn.addEventListener('click', () => switchPage(atContent));

    // 默认显示home页面
    switchPage(homeContent);
});

// 图表配置（初始状态）
const option = {
    backgroundColor: '#141414',
    title: {
        text: 'Research Relationship Network',
        left: 'center',
        textStyle: {
            color: '#F2F3F5',
            fontSize: 18,
            fontWeight: 'bold'
        }
    },
    tooltip: {
        trigger: 'item',
        formatter: function(params) {
            if (params.data && params.data.extra) {
                let content = `<div class="tooltip-title">${params.data.name}</div>`;
                content += `<div class="tooltip-item"><span class="tooltip-label">Type:</span> ${params.data.extra.type}</div>`;

                if (params.data.extra.count) {
                    content += `<div class="tooltip-item"><span class="tooltip-label">Count:</span> ${params.data.extra.count}</div>`;
                }

                if (params.data.extra.relatedPair) {
                    content += `<div class="tooltip-item"><span class="tooltip-label">Related Pair:</span> ${params.data.extra.relatedPair}</div>`;
                }

                if (params.data.extra.theoreticalSupport && params.data.extra.theoreticalSupport.length > 0) {
                    content += `<div class="tooltip-item"><span class="tooltip-label">Theoretical Support:</span> ${params.data.extra.theoreticalSupport.join(', ')}</div>`;
                }

                if (params.data.extra.researchMethods && params.data.extra.researchMethods.length > 0) {
                    content += `<div class="tooltip-item"><span class="tooltip-label">Research Methods:</span> ${params.data.extra.researchMethods.join(', ')}</div>`;
                }

                return content;
            }
            return params.data ? params.data.name : '';
        }
    },
    legend: {
        type: 'scroll',
        bottom: 10,
        left: 'center',
        data: [],
        textStyle: {
            color: '#fff',
            fontSize: 12
        }
    },
    animationDurationUpdate: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [
        {
            type: 'graph',
            layout: 'force',
            force: {
                repulsion: 200,
                edgeLength: 100,
                gravity: 0.1
            },
            roam: true,
            draggable: true,
            focusNodeAdjacency: true,
            symbolSize: function (value) {
                return 30 + value * 2;
            },
            label: {
                show: true,
                position: 'inside',
                formatter: function(params) {
                    return params.data.name.length > 10 ? params.data.name.substring(0, 10) + '...' : params.data.name;
                },
                color: '#fff',
                fontSize: 10
            },
            lineStyle: {
                opacity: 0.7,
                width: 1.5,
                curveness: 0.1
            },
            categories: [],
            data: [],
            links: []
        }
    ]
};

// 设置初始图表选项
myChart.setOption(option);

// 监听鼠标事件，自定义tooltip样式
myChart.on('mouseover', function(params) {
    if (params.data.extra) {
        tooltip.style.display = 'block';

        let content = `<div class="tooltip-title">${params.data.name}</div>`;
        content += `<div class="tooltip-item"><span class="tooltip-label">Type:</span> ${params.data.extra.type}</div>`;

        if (params.data.extra.count) {
            content += `<div class="tooltip-item"><span class="tooltip-label">Count:</span> ${params.data.extra.count}</div>`;
        }

        if (params.data.extra.relatedPair) {
            content += `<div class="tooltip-item"><span class="tooltip-label">Related Pair:</span> ${params.data.extra.relatedPair}</div>`;
        }

        if (params.data.extra.theoreticalSupport && params.data.extra.theoreticalSupport.length > 0) {
            content += `<div class="tooltip-item"><span class="tooltip-label">Theoretical Support:</span> ${params.data.extra.theoreticalSupport.join(', ')}</div>`;
        }

        if (params.data.extra.researchMethods && params.data.extra.researchMethods.length > 0) {
            content += `<div class="tooltip-item"><span class="tooltip-label">Research Methods:</span> ${params.data.extra.researchMethods.join(', ')}</div>`;
        }

        tooltip.innerHTML = content;

        // 计算tooltip位置
        const point = myChart.convertToPixel('grid', [params.event.event.offsetX, params.event.event.offsetY]);
        tooltip.style.left = (point[0] + 20) + 'px';
        tooltip.style.top = (point[1] - 20) + 'px';
    }
});

myChart.on('mouseout', function() {
    tooltip.style.display = 'none';
});

// 监听窗口大小变化，调整图表
window.addEventListener('resize', function() {
    myChart.resize();
});


// 处理数据并更新图表
function updateChart(relations) {
    // 处理数据
    const nodes = [];
    const links = [];
    const categories = [
        { name: 'Variable Pair' },
        { name: 'Mediating Variable' },
        { name: 'Moderating Variable' }
    ];

    // 为每个关系创建节点和链接
    relations.forEach((relation, index) => {
        const pair = relation['Variable Pair'];
        const [sourceVar, targetVar] = pair.split(' → ');

        // 添加源变量节点
        let sourceNode = nodes.find(node => node.name === sourceVar);
        if (!sourceNode) {
            sourceNode = {
                name: sourceVar,
                category: 0,
                value: 1,
                symbolSize: 50 + (relation.count || 1) * 2,
                itemStyle: {
                    color: '#4080FF'
                },
                label: {
                    show: true,
                    formatter: sourceVar,
                    fontSize: 12
                },
                // 存储额外信息
                extra: {
                    type: 'Variable Pair',
                    count: relation.count || 1,
                    theoreticalSupport: relation['Theoretical Support'] || [],
                    researchMethods: relation['Research Methods'] || []
                }
            };
            nodes.push(sourceNode);
        } else {
            // 如果节点已存在，增加其值和大小
            sourceNode.value += 1;
            sourceNode.symbolSize = 50 + (relation.count || 1) * 2;
        }

        // 添加目标变量节点
        let targetNode = nodes.find(node => node.name === targetVar);
        if (!targetNode) {
            targetNode = {
                name: targetVar,
                category: 0,
                value: 1,
                symbolSize: 50 + (relation.count || 1) * 2,
                itemStyle: {
                    color: '#4080FF'
                },
                label: {
                    show: true,
                    formatter: targetVar,
                    fontSize: 12
                },
                // 存储额外信息
                extra: {
                    type: 'Variable Pair',
                    count: relation.count || 1,
                    theoreticalSupport: relation['Theoretical Support'] || [],
                    researchMethods: relation['Research Methods'] || []
                }
            };
            nodes.push(targetNode);
        } else {
            // 如果节点已存在，增加其值和大小
            targetNode.value += 1;
            targetNode.symbolSize = 50 + (relation.count || 1) * 2;
        }

        // 添加源和目标之间的链接
        links.push({
            source: sourceNode.name,
            target: targetNode.name,
            value: relation.count || 1,
            lineStyle: {
                width: 2 + (relation.count || 1) * 0.2,
                color: '#4080FF',
                opacity: 0.7
            },
            label: {
                show: true,
                formatter: (relation.count || 1).toString(),
                fontSize: 10
            }
        });

        // 添加中介变量节点和链接
        if (relation['Mediating Variable'] && relation['Mediating Variable'] !== 'None') {
            const mediatingVar = relation['Mediating Variable'];
            let mediatingNode = nodes.find(node => node.name === mediatingVar);
            if (!mediatingNode) {
                mediatingNode = {
                    name: mediatingVar,
                    category: 1,
                    value: 1,
                    symbolSize: 40,
                    itemStyle: {
                        color: '#916BBF'
                    },
                    label: {
                        show: true,
                        formatter: mediatingVar,
                        fontSize: 10
                    },
                    // 存储额外信息
                    extra: {
                        type: 'Mediating Variable',
                        relatedPair: pair
                    }
                };
                nodes.push(mediatingNode);
            } else {
                mediatingNode.value += 1;
            }

            // 添加源变量到中介变量的链接
            links.push({
                source: sourceNode.name,
                target: mediatingNode.name,
                lineStyle: {
                    width: 1.5,
                    color: '#916BBF',
                    opacity: 0.6
                }
            });

            // 添加中介变量到目标变量的链接
            links.push({
                source: mediatingNode.name,
                target: targetNode.name,
                lineStyle: {
                    width: 1.5,
                    color: '#916BBF',
                    opacity: 0.6
                }
            });
        }

        // 添加调节变量节点和链接
        if (relation['Moderating Variable'] && relation['Moderating Variable'] !== 'None') {
            const moderatingVar = relation['Moderating Variable'];
            let moderatingNode = nodes.find(node => node.name === moderatingVar);
            if (!moderatingNode) {
                moderatingNode = {
                    name: moderatingVar,
                    category: 2,
                    value: 1,
                    symbolSize: 35,
                    itemStyle: {
                        color: '#00C4C4'
                    },
                    label: {
                        show: true,
                        formatter: moderatingVar,
                        fontSize: 10
                    },
                    // 存储额外信息
                    extra: {
                        type: 'Moderating Variable',
                        relatedPair: pair
                    }
                };
                nodes.push(moderatingNode);
            } else {
                moderatingNode.value += 1;
            }

            // 添加调节变量到源变量的链接
            links.push({
                source: moderatingNode.name,
                target: sourceNode.name,
                lineStyle: {
                    width: 1,
                    color: '#00C4C4',
                    opacity: 0.5,
                    curveness: 0.2
                }
            });

            // 添加调节变量到目标变量的链接
            links.push({
                source: moderatingNode.name,
                target: targetNode.name,
                lineStyle: {
                    width: 1,
                    color: '#00C4C4',
                    opacity: 0.5,
                    curveness: 0.2
                }
            });
        }
    });

    // 更新图表配置
    option.legend.data = categories.map(function(a) {
        return a.name;
    });
    option.series[0].categories = categories;
    option.series[0].data = nodes;
    option.series[0].links = links;

    // 应用更新后的配置
    myChart.setOption(option);
    myChart.resize(); // 数据更新后强制Resize
}



// 页面跳转逻辑
let currentChartIndex = 0;

function showChart(index) {
    const originalCharts = document.getElementById('originalCharts');
    const relationshipChart = document.getElementById('relationshipChart');
    
    if (index === 0) {
        // 显示四个图表
        originalCharts.style.display = 'grid';
        relationshipChart.style.display = 'none';
        
        // 重新调整所有图表大小
        const charts = [
            document.getElementById('variable-bar-chart'),
            document.getElementById('theory-bar-chart'),
            document.getElementById('type-pie-chart')
        ];
        
        charts.forEach(chart => {
            if (chart && chart.__echarts__) {
                chart.__echarts__.resize();
            }
        });
    } else {
        // 显示关系图
        originalCharts.style.display = 'none';
        relationshipChart.style.display = 'block';
        
        // 确保关系图正确显示
        setTimeout(() => {
            myChart.resize();
        }, 100);
    }
}

// 添加箭头按钮事件监听
document.addEventListener('DOMContentLoaded', function() {
    const prevBtn = document.getElementById('prevChartBtn');
    const nextBtn = document.getElementById('nextChartBtn');
    
    if (prevBtn && nextBtn) {
        prevBtn.addEventListener('click', () => {
            currentChartIndex = 0;
            showChart(currentChartIndex);
        });
        
        nextBtn.addEventListener('click', () => {
            currentChartIndex = 1;
            showChart(currentChartIndex);
        });
    }
});

function initCharts(answerData) {
    const variables = answerData.researchVariables || [];
    const theories = answerData.theoreticalFrameworks || [];
    const methods = answerData.researchMethods || [];

    // 初始化图表容器
    const variableChart = echarts.init(document.getElementById('variable-bar-chart'));
    const theoryChart = echarts.init(document.getElementById('theory-bar-chart'));
    const typeChart = echarts.init(document.getElementById('type-pie-chart'));
    const methodsTable = document.getElementById('methods-table');

    // 确保图表容器可见
    document.getElementById('originalCharts').style.display = 'grid';
    document.getElementById('relationshipChart').style.display = 'none';

    // 时间区间选择监听
    document.getElementById('time-period-selector').addEventListener('change', (e) => {
        renderVariableBarChart(variableChart, variables, e.target.value);
        renderTheoryBarChart(theoryChart, theories, e.target.value);
    });

    // 类型选择监听
    document.getElementById('type-selector').addEventListener('change', (e) => {
        renderTypePieChart(typeChart, variables, e.target.value);
    });

    // 初始渲染（使用默认时间区间）
    const defaultPeriod = '2020-2024';
    renderVariableBarChart(variableChart, variables, defaultPeriod);
    renderTheoryBarChart(theoryChart, theories, defaultPeriod);
    renderTypePieChart(typeChart, variables, 'dependent');
    renderMethodsTable(methodsTable, methods);

    // 确保所有图表正确渲染
    setTimeout(() => {
        variableChart.resize();
        theoryChart.resize();
        typeChart.resize();
    }, 100);

    // 监听窗口大小变化
    window.addEventListener('resize', () => {
        variableChart.resize();
        theoryChart.resize();
        typeChart.resize();
        if (myChart) {
            myChart.resize();
        }
    });
}

// 变量横向柱状图渲染（带过滤和悬浮提示）
function renderVariableBarChart(chart, variables, period) {
    if (!variables || !Array.isArray(variables)) {
        console.warn('Invalid variables data:', variables);
        return;
    }

    // 过滤该年份区间无数据的变量
    const filteredVariables = variables
        .filter(v => v && v.fiveYearCounts && v.fiveYearCounts[period] > 0)
        .sort((a, b) => b.fiveYearCounts[period] - a.fiveYearCounts[period])
        .slice(0, 10);

    const maxValue = filteredVariables.length > 0
        ? Math.max(...filteredVariables.map(v => v.fiveYearCounts[period]))
        : 0;

    chart.setOption({
        tooltip: {
            trigger: 'item',
            formatter: (params) => `Variable: ${params.name}<br>Count: ${params.value}`
        },
        xAxis: { 
            type: 'value', 
            axisLabel: { color: '#fff' },
            max: maxValue + 4
        },
        yAxis: {
            type: 'category',
            data: filteredVariables.map(v => v.variable),
            axisLabel: { show: false }
        },
        series: [{
            name: 'Variables',
            type: 'bar',
            data: filteredVariables.map(v => ({
                value: v.fiveYearCounts[period],
                name: v.variable
            })),
            itemStyle: { color: '#4CAF50' },
            label: {
                show: true,
                position: 'right',
                formatter: '{b}',
                color: '#fff',
                fontSize: 12,
                margin: 8
            },
            emphasis: {
                scale: 1.05,
                itemStyle: {
                    shadowBlur: 10,
                    shadowColor: 'rgba(76, 175, 80, 0.5)'
                }
            }
        }]
    });
}

// 理论框架柱状图渲染（带过滤和完整标签显示）
function renderTheoryBarChart(chart, theories, period) {
    // 过滤该年份区间无数据的理论
    const filteredTheories = theories
        .filter(t => t.fiveYearCounts[period] > 0)
        .sort((a, b) => b.fiveYearCounts[period] - a.fiveYearCounts[period])
        .slice(0, 10);
    const maxValue = filteredTheories.length > 0
        ? Math.max(...filteredTheories.map(v => v.fiveYearCounts[period]))
         : 0;
    chart.setOption({
        tooltip: {
            trigger: 'item',
            formatter: (params) => `Theory: ${params.name}<br>Count: ${params.value}`
        },
        xAxis: {
            type: 'category',
            data: filteredTheories.map(t => t.theory),
            axisLabel: { show: false }
        },
        yAxis: { type: 'value', axisLabel: { color: '#fff' },max: maxValue + 2 },
        series: [{
            name: 'Theories',
            type: 'bar',
            data: filteredTheories.map(t => ({
                value: t.fiveYearCounts[period],
                name: t.theory // 绑定理论名到data项
            })),
            itemStyle: { color: period === '2015-2019' ? '#2196F3' : '#FF5722' },
            label: { // 顶部显示理论名
                show: true,
                position: 'top', // 纵向柱状图顶部
                formatter: '{b}', // 仅显示名称
                color: '#fff',
                fontSize: 12,
                margin: 8,
                rotate: 45 // 标签旋转45度
            },
            emphasis: { // 悬浮放大
                scale: 1.05,
                itemStyle: {
                    shadowBlur: 10,
                    shadowColor: period === '2015-2019' ? 'rgba(33, 150, 243, 0.5)' : 'rgba(255, 87, 34, 0.5)'
                }
            }
        }] // 此处补充了对象闭合的花括号，确保 `series` 数组内的对象完整闭合
    });
}

// 类型饼图渲染
function renderTypePieChart(chart, variables, selectedType) {
const typeMap = {
    independent: 'Independent Variable',
    dependent: 'Dependent Variable',
    mediator: 'Mediator Variable',
    control: 'Control Variable',
    moderator: 'Moderator Variable'
};
// 过滤该类型下的有效变量
const typeVariables = variables.filter(v => v.types[selectedType] > 0);
const total = typeVariables.reduce((acc, v) => acc + v.types[selectedType], 0);
const data = typeVariables.map(v => ({
    name: v.variable,
    value: v.types[selectedType],
    percent: (v.types[selectedType] / total * 100).toFixed(1)
})).filter(item => item.value > 0);

chart.setOption({
    tooltip: {
        trigger: 'item',
        formatter: (params) => `${params.name}<br>Count: ${params.value}<br>占比: ${params.percent}%`
    },
    series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        label: {
            color: '#fff',
            formatter: '{b}: {c} ({d}%)'
        },
        data: data.length ? data : [{name: 'No data', value: 0}]
    }]
});
}

// 方法表格渲染
function renderMethodsTable(table, methods) {
    table.innerHTML = `
        <thead><tr><th>Method</th><th>Count</th></tr></thead>
        <tbody>${methods.map(m => `<tr><td>${m.method}</td><td>${m.count}</td></tr>`).join('')}</tbody>
    `;
}

    // 更新历史记录视图
    function updateHistoryView() {
        const keywordList = document.getElementById('keywordList');
        const dataDisplay = document.getElementById('dataDisplay');
        keywordList.innerHTML = '<h3>Query History</h3>';
        dataDisplay.innerHTML = '<h3>Data Details</h3>';

        if (queryHistory.length === 0) {
            keywordList.innerHTML += '<p>No query history yet</p>';
            return;
        }

        queryHistory.forEach((queryItem, index) => {
            const keywordItem = document.createElement('div');
            keywordItem.className = 'keyword-item';
            keywordItem.innerHTML = `
                <h4>${queryItem.query}</h4>
                <p>Time: ${new Date(queryItem.timestamp).toLocaleString()}</p>
            `;
            keywordItem.addEventListener('click', () => showDataDetails(index));
            keywordList.appendChild(keywordItem);
        });
    }

    // 更新A&T历史记录视图
    function updateAtHistoryView() {
        const atKeywordList = document.getElementById('atKeywordList');
        const atDataDisplay = document.getElementById('atDataDisplay');
        atKeywordList.innerHTML = '<h3>A&T Query History</h3>';
        atDataDisplay.innerHTML = '<h3>A&T Data Details</h3>';

        if (atQueryHistory.length === 0) {
            atKeywordList.innerHTML += '<p>No query history yet</p>';
            return;
        }

        atQueryHistory.forEach((queryItem, index) => {
            const keywordItem = document.createElement('div');
            keywordItem.className = 'keyword-item';
            keywordItem.innerHTML = `
                <h4>${queryItem.query}</h4>
                <p>Time: ${new Date(queryItem.timestamp).toLocaleString()}</p>
            `;
            keywordItem.addEventListener('click', () => showAtDataDetails(index));
            atKeywordList.appendChild(keywordItem);
        });
    }

    // 显示A&T数据详情
    function showAtDataDetails(index) {
        if (!atQueryHistory[index]) {
            const atDataDisplay = document.getElementById('atDataDisplay');
            atDataDisplay.innerHTML = `<p class="error">无效的查询记录</p>`;
            return;
        }
        const queryItem = atQueryHistory[index];
        const tableName = `${queryItem.query}_result`;
        const atDataDisplay = document.getElementById('atDataDisplay');
        atDataDisplay.innerHTML = `
            <h3>Details for: ${queryItem.query}</h3>
            <p><strong>Time:</strong> ${new Date(queryItem.timestamp).toLocaleString()}</p>
            <p>Loading data from backend...</p>
        `;
        fetch(`/api/at_prediction?table_name=${encodeURIComponent(tableName)}`)
           .then(response => response.json())
           .then(data => {
                if (data.error) {
                    atDataDisplay.innerHTML += `<p class="error">${data.error}</p>`;
                    return;
                }
                const { thinking, prediction } = data;
                atDataDisplay.innerHTML = `
                    <h3>Details for: ${queryItem.query}</h3>
                    <p><strong>Time:</strong> ${new Date(queryItem.timestamp).toLocaleString()}</p>
                    <div class="data-content">
                        <h4>Thinking:</h4>
                        <p>${thinking}</p>
                        <h4>Prediction:</h4>
                        <p>${prediction}</p>
                    </div>
                `;
            })
           .catch(error => {
                atDataDisplay.innerHTML = `
                    <p class="error">加载失败: ${error.message}</p>
                    <p>请检查表名 "${tableName}" 是否存在</p>
                `;
            });
    }

    // 显示数据详情
    function showDataDetails(index) {
        const user_input = sessionStorage.getItem('user_input');
        const queryItem = queryHistory[index];
        if (!user_input) {
            console.error('user_input 未找到');
            return;
        }
        const targetQuery = queryItem.query || user_input;
        const dataDisplay = document.getElementById('dataDisplay');
        dataDisplay.innerHTML = `
            <h3>Details for: ${targetQuery}</h3>
            <p>Loading data from backend...</p>
        `;
        fetch(`/api/scopus?user_input=${encodeURIComponent(targetQuery)}`)
           .then(response => response.json())
           .then(data => {
                if (data.error) {
                    dataDisplay.innerHTML += `<p class="error">${data.error}</p>`;
                    return;
                }
                const dataHTML = data.map(paper => `
                    <div class="paper-entry">
                        <h4>${paper.title || 'No title'}</h4>
                        <p><strong>Authors:</strong> ${paper.author || 'Unknown'}</p>
                        <p><strong>Publication:</strong> ${paper.publication || 'No publication'}</p>
                        <p><strong>Year:</strong> ${paper.year || 'No year'}</p>
                        <p><strong>Citation:</strong> ${paper.citation || '0'}</p>
                        <p><strong>Abstract:</strong> ${paper.abstract || 'No abstract available'}</p>
                    </div>
                `).join('');
                dataDisplay.innerHTML += dataHTML;
            })
           .catch(error => {
                dataDisplay.innerHTML += `<p class="error">Failed to load data: ${error.message}</p>`;
            });
    }

    // 等待 DOM 加载完成
    document.addEventListener('DOMContentLoaded', function() {
        // 关键词搜索相关变量
        const keywordSearch = document.getElementById('keywordSearch');
        const autocompleteResults = document.getElementById('autocompleteResults');
        const searchButton = document.getElementById('searchButton');
        let searchTimeout;

        if (!keywordSearch || !autocompleteResults || !searchButton) {
            console.error('Required elements not found:', {
                keywordSearch: !!keywordSearch,
                autocompleteResults: !!autocompleteResults,
                searchButton: !!searchButton
            });
            return;
        }

        // 添加关键词搜索功能
        keywordSearch.addEventListener('input', function() {
            const searchTerm = this.value.trim();
            console.log('Search term:', searchTerm);
            
            // 清除之前的定时器
            if (searchTimeout) {
                clearTimeout(searchTimeout);
            }
            
            // 如果搜索词为空，隐藏结果
            if (!searchTerm) {
                autocompleteResults.style.display = 'none';
                return;
            }
            
            // 设置新的定时器，延迟300ms执行搜索
            searchTimeout = setTimeout(() => {
                fetch(`/api/search_keywords?term=${encodeURIComponent(searchTerm)}`)
                    .then(response => {
                        console.log('Search response status:', response.status);
                        return response.json();
                    })
                    .then(data => {
                        console.log('Search results:', data);
                        
                        if (Array.isArray(data) && data.length > 0) {
                            // 显示匹配的关键词
                            autocompleteResults.innerHTML = data
                                .map(keyword => `<div class="autocomplete-item">${keyword}</div>`)
                                .join('');
                            autocompleteResults.style.display = 'block';
                        } else {
                            autocompleteResults.innerHTML = '<div class="autocomplete-item">No matches found</div>';
                            autocompleteResults.style.display = 'block';
                        }
                    })
                    .catch(error => {
                        console.error('Search error:', error);
                        autocompleteResults.innerHTML = '<div class="autocomplete-item">Error searching keywords</div>';
                        autocompleteResults.style.display = 'block';
                    });
            }, 300);
        });

        // 搜索按钮点击事件
        searchButton.addEventListener('click', function() {
            const keyword = keywordSearch.value.trim();
            if (keyword) {
                fetchAndDisplayResult(keyword);
            }
        });

        // 点击自动完成项时获取结果
        autocompleteResults.addEventListener('click', function(e) {
            if (e.target.classList.contains('autocomplete-item')) {
                const keyword = e.target.textContent;
                console.log('Selected keyword:', keyword);
                
                // 更新搜索框
                keywordSearch.value = keyword;
                autocompleteResults.style.display = 'none';
                
                // 获取并显示结果
                fetchAndDisplayResult(keyword);
            }
        });

        // 获取并显示结果的函数
        function fetchAndDisplayResult(keyword) {
            // 显示加载指示器
            const loadingIndicator = document.getElementById('loadingIndicator');
            if (loadingIndicator) {
                loadingIndicator.style.display = 'block';
            }
            
            // 获取该关键词的最新结果
            fetch(`/api/get_keyword_result?keyword=${encodeURIComponent(keyword)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.result) {
                        try {
                            // 解析JSON结果
                            const answerData = JSON.parse(data.result);
                            
                            // 初始化所有图表
                            initCharts(answerData);
                            
                            // 更新关系图
                            if (answerData.relation) {
                                updateChart(answerData.relation);
                            }
                            
                            // 确保显示正确的视图
                            showChart(0);
                        } catch (error) {
                            console.error('Error parsing result:', error);
                            alert('Error processing the result data');
                        }
                    } else {
                        console.log('No result found for keyword:', keyword);
                        alert('No result found for this keyword');
                    }
                })
                .catch(error => {
                    console.error('Error fetching result:', error);
                    alert('Error fetching result: ' + error.message);
                })
                .finally(() => {
                    // 隐藏加载指示器
                    if (loadingIndicator) {
                        loadingIndicator.style.display = 'none';
                    }
                });
        }

        // 点击页面其他地方时隐藏自动完成结果
        document.addEventListener('click', function(e) {
            if (!keywordSearch.contains(e.target) && !autocompleteResults.contains(e.target)) {
                autocompleteResults.style.display = 'none';
            }
        });
    });