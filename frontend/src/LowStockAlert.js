import React, { useState, useEffect } from 'react';

function LowStockAlert() {
  const [alertaProduto, setAlertaProduto] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/alert/low-stock/')
      .then(response => {
        if (!response.ok) {
          throw new Error('Erro ao buscar dados da API');
        }
        return response.json();
      })
      .then(data => {
        setAlertaProduto(data);
      })
      .catch(error => {
        console.error('Houve um erro:', error);
      });
  }, []);

  if (alertaProduto === null) {
    return <div>Carregando alertas de produtos em falta...</div>;
  }

  return (
    <div>
      <h1>Alerta de Produtos em Falta</h1>
      {alertaProduto.length > 0 ? (
        <ul>
          {alertaProduto.map(produto => (
            <li key={produto.id}>
              <p>Produto: {produto.product_name}</p>
              <p>Quantidade: {produto.quantity}</p>
              <p>ID do Produto: {produto.id}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p>O estoque está em bom estado.</p>
      )}
    </div>
  );
}


export default LowStockAlert;