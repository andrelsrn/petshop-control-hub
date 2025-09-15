import React, { useState, useEffect, useRef } from 'react';
import Agenda from './Agenda';
import LowStockAlert from './LowStockAlert';
import Chart from 'chart.js/auto'; // Importa a biblioteca do Chart.js

function Dashboard() {
  const [kpis, setKpis] = useState(null);
  // Cria uma referência para o elemento canvas do gráfico
  const chartRef = useRef(null);
  // Armazena a instância do gráfico para poder destruí-la depois
  const chartInstance = useRef(null);

  // useEffect para buscar os dados da API (o que você já tinha)
  useEffect(() => {
    fetch('http://localhost:8000/api/dashboard/kpis/')
      .then(response => {
        if (!response.ok) {
          throw new Error('Erro ao buscar dados da API');
        }
        return response.json();
      })
      .then(data => {
        setKpis(data);
      })
      .catch(error => {
        console.error('Houve um erro:', error);
      });
  }, []);

  // Novo useEffect para criar e atualizar o gráfico
  // Este hook só executa quando 'kpis' muda de valor
  useEffect(() => {
    // Garante que o gráfico só seja criado se os dados já estiverem carregados
    if (kpis) {
        // Se já existe um gráfico, destrói-o para evitar conflitos
        if (chartInstance.current) {
            chartInstance.current.destroy();
        }

        const ctx = chartRef.current.getContext('2d');
        
        // Dados de exemplo para o gráfico (podemos substituir por dados da API depois)
        const revenueData = {
          labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai'],
          datasets: [{
            label: 'Receita Mensal ($)',
            data: [1200, 1900, 3000, 5000, 2300],
            backgroundColor: 'rgba(34, 136, 75, 0.6)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
            fill: true,
            tension: 0.3
          }]
        };

        const config = {
          type: 'line',
          data: revenueData,
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true
              }
            }
          }
        };

        // Cria uma nova instância do gráfico e armazena a referência
        chartInstance.current = new Chart(ctx, config);
    }
  }, [kpis]); // Dependência: roda sempre que o estado 'kpis' é atualizado

  if (!kpis) {
    return <div>Carregando KPIs...</div>;
  }

  return (
    <div>
      <h1>Painel de Controle </h1>
    

      <h2>Visão Geral</h2>
            {/* --- Estrutura das Boxes de KPI --- */}
      <div className="kpis-container">
        
        <div className="kpi-box">
          <div className="kpi-title">Receita Total</div>
          <div className="kpi-value">R$ {kpis.total_revenue.toLocaleString('pt-BR')}</div>
        </div>

        <div className="kpi-box">
          <div className="kpi-title">Total de Vendas</div>
          <div className="kpi-value">{kpis.total_sales.toLocaleString('pt-BR')}</div>
        </div>

        <div className="kpi-box">
          <div className="kpi-title">Total de Agendamentos</div>
          <div className="kpi-value">{kpis.total_bookings.toLocaleString('pt-BR')}</div>
        </div>

        <div className="kpi-box">
          <div className="kpi-title">Total de Clientes</div>
          <div className="kpi-value">{kpis.total_customers.toLocaleString('pt-BR')}</div>
        </div>

      </div>
      <h2>Evolução da Receita</h2>
            <div style={{ height: '400px' }}>
        {/* O ref "chartRef" conecta este elemento ao hook useRef() */}
        <canvas ref={chartRef}></canvas>
      </div>
      <Agenda />
      <LowStockAlert />
    </div>
  );
}

export default Dashboard;