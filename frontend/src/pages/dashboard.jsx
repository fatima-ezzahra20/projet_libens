import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend, ResponsiveContainer } from "recharts";
import "./dashboard.css";

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [facturesProches, setFacturesProches] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/dashboard/")
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error(err));

    fetch("http://localhost:8000/dashboard/proches-echeances?jours=17")
      .then(res => res.json())
      .then(data => setFacturesProches(Array.isArray(data) ? data : []))
      .catch(err => console.error(err));
  }, []);

  if (!stats) return <p>Chargement...</p>;

  const chartData = mergeData(stats.factures_par_mois || [], stats.releves_par_mois || []);

  return (
    <div className="dashboard-container">
      <h1>Dashboard</h1>

      <div className="stats-cards">
        <div className="card-factures">
          <h2>Factures</h2>
          <p>Nombre : {stats.total_nombre_factures}</p>
          <p>Montant total : {stats.total_montant_factures} DH</p>
        </div>
        <div className="card-releves">
          <h2>Relevés</h2>
          <p>Nombre : {stats.total_nombre_releves}</p>
          <p>Montant total : {stats.total_montant_releves} DH</p>
        </div>
      </div>

      <div className="chart-section">
        <h2>Évolution mensuelle</h2>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="mois" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="factures" stroke="#4caf50" />
            <Line type="monotone" dataKey="releves" stroke="#2196f3" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="proches-echeances-section">
        <h2>Factures à échéance proche</h2>
        {facturesProches.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>Numéro</th>
                <th>Fournisseur</th>
                <th>Montant TTC</th>
                <th>Date d'échéance</th>
              </tr>
            </thead>
            <tbody>
              {facturesProches.map(f => (
                <tr key={f.num_facture}>
                  <td>{f.num_facture}</td>
                  <td>{f.fournisseur}</td>
                  <td>{f.montant_total_ttc} DH</td>
                  <td>{f.date_echeance}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>Aucune facture proche de l'échéance.</p>
        )}
      </div>
    </div>
  );
}

function mergeData(factures, releves) {
  const monthsMap = {
    "01": "Janvier", "02": "Février", "03": "Mars", "04": "Avril",
    "05": "Mai", "06": "Juin", "07": "Juillet", "08": "Août",
    "09": "Septembre", "10": "Octobre", "11": "Novembre", "12": "Décembre"
  };
  const allMonths = ["01","02","03","04","05","06","07","08","09","10","11","12"];

  return allMonths.map(monthNum => {
    const monthName = monthsMap[monthNum];
    const f = factures.find(f => f.mois.endsWith(monthNum));
    const r = releves.find(r => r.mois.toLowerCase().startsWith(monthName.toLowerCase()));
    return {
      mois: monthName,
      factures: f ? f.total : 0,
      releves: r ? r.total : 0
    };
  });
}

export default Dashboard;
