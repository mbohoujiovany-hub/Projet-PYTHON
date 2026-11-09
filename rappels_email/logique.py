
from datetime import date, datetime
from database import get_connection

# Les paliers de rappel, en nombre de jours avant la date limite
ECHEANCES = [7, 3, 1]


def determiner_type_rappel(jours_restants):
    """Retourne 'J-7', 'J-3' ou 'J-1' selon les jours restants, ou None."""
    if jours_restants < 0:
        return None  # date limite déjà dépassée
    for seuil in sorted(ECHEANCES):  # on teste 1, puis 3, puis 7
        if jours_restants <= seuil:
            return f"J-{seuil}"
    return None  # échéance trop lointaine


def rappel_deja_envoye(conn, etudiant_id, type_rappel):
    """Vérifie dans la table 'rappels' si ce palier a déjà été envoyé."""
    ligne = conn.execute(
        "SELECT 1 FROM rappels WHERE etudiant_id = ? AND type_rappel = ?",
        (etudiant_id, type_rappel),
    ).fetchone()
    return ligne is not None


def get_rappels_a_envoyer(aujourdhui=None):
    """Retourne la liste des étudiants à qui il faut envoyer un rappel."""
    if aujourdhui is None:
        aujourdhui = date.today()

    conn = get_connection()
    etudiants = conn.execute("""
        SELECT e.id, e.nom, e.email, e.montant_total, e.date_limite,
               COALESCE(SUM(p.montant), 0) AS paye
        FROM etudiants e
        LEFT JOIN paiements p ON p.etudiant_id = e.id
        GROUP BY e.id
    """).fetchall()

    a_envoyer = []
    for etu in etudiants:
        solde = etu["montant_total"] - etu["paye"]
        if solde <= 0:
            continue  # tout est payé : pas de rappel

        date_limite = datetime.strptime(etu["date_limite"], "%Y-%m-%d").date()
        jours_restants = (date_limite - aujourdhui).days

        type_rappel = determiner_type_rappel(jours_restants)
        if type_rappel is None:
            continue  # trop tôt ou trop tard

        if rappel_deja_envoye(conn, etu["id"], type_rappel):
            continue  # déjà envoyé

        a_envoyer.append({
            "etudiant_id": etu["id"],
            "nom": etu["nom"],
            "email": etu["email"],
            "solde": solde,
            "date_limite": date_limite,
            "jours_restants": jours_restants,
            "type_rappel": type_rappel,
        })

    conn.close()
    return a_envoyer


def enregistrer_rappel(etudiant_id, type_rappel, aujourdhui=None):
    """Note dans la base qu'un rappel a été envoyé."""
    if aujourdhui is None:
        aujourdhui = date.today()

    conn = get_connection()
    conn.execute(
        "INSERT INTO rappels (etudiant_id, type_rappel, date_envoi) VALUES (?, ?, ?)",
        (etudiant_id, type_rappel, aujourdhui.isoformat()),
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    print("=== Test 1 : première exécution ===")
    liste = get_rappels_a_envoyer()
    for r in liste:
        print(f"{r['nom']:<15} -> {r['type_rappel']}  "
              f"({r['jours_restants']} jours, solde {r['solde']})")

    # On simule l'envoi réussi en enregistrant chaque rappel
    for r in liste:
        enregistrer_rappel(r["etudiant_id"], r["type_rappel"])

    print("\n=== Test 2 : deuxième exécution (doit être vide) ===")
    liste2 = get_rappels_a_envoyer()
    print(f"{len(liste2)} rappel(s) à envoyer")







