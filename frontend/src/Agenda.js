import React, { useState, useEffect } from 'react';

function Agenda() {
  const [agendamentos, setAgendamentos] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/schedule/today/')
      .then(response => {
        if (!response.ok) {
          throw new Error('Erro ao buscar dados da API');
        }
        return response.json();
      })
      .then(data => {
        setAgendamentos(data);
      })
      .catch(error => {
        console.error('Houve um erro:', error);
      });
  }, []);

  if (agendamentos === null) {
    return <div>Carregando agendamentos...</div>;
  }

  return (
    <div>
      <h1>Agenda do Dia</h1>
      {agendamentos.length > 0 ? (
        <ul>
          {agendamentos.map(agendamento => (
            <li key={agendamento.id}>
              <h3>{agendamento.service_name}</h3>
              <p>Pet ID: {agendamento.pet_id}</p>
              <p>Horário: {agendamento.scheduled_time}</p>
              <p>Funcionário ID: {agendamento.employee_id}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p>Não há agendamentos para hoje.</p>
      )}
    </div>
  );
}

export default Agenda;