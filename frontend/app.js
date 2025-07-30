async function uploadFile() {
  const input = document.getElementById("fileInput");
  const output = document.getElementById("output");
  const loader = document.getElementById("loader");
  const btn = document.getElementById("analyzeBtn");

  if (input.files.length === 0) {
    alert("Veuillez choisir un fichier.");
    return;
  }

  const file = input.files[0];
  const formData = new FormData();
  formData.append("file", file);

  output.innerHTML = "";
  loader.classList.remove("hidden");
  btn.disabled = true;

  try {
    const response = await fetch("http://localhost:8000/extract", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      throw new Error("Erreur : " + response.statusText);
    }

    const result = await response.json();

    // 🔍 Ajout du type de document détecté
    let html = `<h3>📄 Type de document détecté :</h3>
                <p style="font-weight:bold; color:#764ba2;">${result.type_document.toUpperCase()}</p>`;

    

    
// === Séparer entités produits et autres ===
const lignesProduits = [];
const autresEntites = [];

let ligneTemp = {};

for (const ent of result.entites) {
  const label = ent.label.trim();
  
  // S’il s'agit d’un champ de produit
  if (["DESCRIPTION_LIGNE", "QUANTITE", "PRIX_UNITAIRE_HT", "MONTANT_LIGNE"].includes(label)) {
    ligneTemp[label] = ent.text;
    
    // Quand une ligne est complète
    if (ligneTemp["DESCRIPTION_LIGNE"] && ligneTemp["QUANTITE"] && ligneTemp["PRIX_UNITAIRE_HT"] && ligneTemp["MONTANT_LIGNE"]) {
      lignesProduits.push({ ...ligneTemp }); // Copie
      ligneTemp = {}; // Reset
    }

  } else {
    autresEntites.push(ent);
  }
}

// === Affichage des entités hors lignes ===
html += `<h3>📌 Informations Générales :</h3>`;
if (autresEntites.length > 0) {
  html += autresEntites.map(ent =>
    `<div class="entite"><strong>${ent.label}</strong> : ${ent.text}</div>`
  ).join("");
} else {
  html += `<p>Aucune entité détectée.</p>`;
}

// === Affichage des produits ===
html += `<h3>🛒 Produits  :</h3>`;
if (lignesProduits.length > 0) {
  lignesProduits.forEach((prod, i) => {
    html += `<div class="produit">
      <h4>Produit ${i + 1}</h4>
      <ul>
        <li><strong>Description :</strong> ${prod.DESCRIPTION_LIGNE}</li>
        <li><strong>Quantité :</strong> ${prod.QUANTITE}</li>
        <li><strong>Prix unitaire HT :</strong> ${prod.PRIX_UNITAIRE_HT}</li>
        <li><strong>Montant ligne :</strong> ${prod.MONTANT_LIGNE}</li>
      </ul>
    </div>`;
  });
} else {
  html += `<p>Aucun produit détecté.</p>`;
}

output.innerHTML = html;
  } catch (error) {
    output.innerHTML = `<p style="color:red;">Erreur : ${error.message}</p>`;
    console.error(error);
  } finally {
    loader.classList.add("hidden");
    btn.disabled = false;
  }
}
