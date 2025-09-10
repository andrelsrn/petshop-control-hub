import React, { useState, useEffect } from 'react';
import Agenda from './Agenda';
import LowStockAlert from './LowStockAlert';



function Dashboard() {
  const [kpis, setKpis] = useState(null);

  useEffect(() => {
    // Faz a chamada à sua API de KPIs
    fetch('http://localhost:8000/api/dashboard/kpis/')
      .then(response => {
        // Verifica se a resposta foi bem-sucedida
        if (!response.ok) {
          throw new Error('Erro ao buscar dados da API');
        }
        return response.json();
      })
      .then(data => {
        // Atualiza o estado com os dados recebidos da API
        setKpis(data);
      })
      .catch(error => {
        console.error('Houve um erro:', error);
      });
  }, []); // O array vazio [] garante que o useEffect rode apenas uma vez

  // Se os dados ainda não foram carregados, exibe uma mensagem
  if (!kpis) {
    return <div>Carregando KPIs...</div>;
  }

  return (
    <div>
      <h1>Painel de Controle Pet Control Hub</h1>
      <p>Receita Total: {kpis.total_revenue}</p>
      <p>Vendas Totais: {kpis.total_sales}</p>
      <p>Agendamentos Totais: {kpis.total_bookings}</p>
      <p>Clientes Totais: {kpis.total_customers}</p>
    
      <Agenda />
      <LowStockAlert />
    </div>
  );
    
}

export default Dashboard;