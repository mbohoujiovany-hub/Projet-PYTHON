


import sqlite3
from datetime import date, timedelta

NOM_BASE = "plateforme_test.db"


def get_connection():
    """Ouvre une connexion à la base de données."""
    conn = sqlite3.connect(NOM_BASE)
    conn.row_factory = sqlite3.Row          # permet d'accéder aux colonnes par leur nom
    conn.execute("PRAGMA foreign_keys = ON")  # active les liens entre tables
    return conn


def reinitialiser_base():
    """Supprime puis recrée les tables (utile pour recommencer les essais)."""
    conn = get_connection()
    conn.executescript("""
        DROP TABLE IF EXISTS rappels;
        DROP TABLE IF EXISTS paiements;
        DROP TABLE IF EXISTS etudiants;

        CREATE TABLE etudiants (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            nom            TEXT    NOT NULL,
            email          TEXT    NOT NULL UNIQUE,
            montant_total  INTEGER NOT NULL,
            date_limite    TEXT    NOT NULL
        );

        CREATE TABLE paiements (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            etudiant_id    INTEGER NOT NULL,
            montant        INTEGER NOT NULL,
            date_paiement  TEXT    NOT NULL,
            FOREIGN KEY (etudiant_id) REFERENCES etudiants(id)
        );

        CREATE TABLE rappels (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            etudiant_id    INTEGER NOT NULL,
            type_rappel    TEXT    NOT NULL,
            date_envoi     TEXT    NOT NULL,
            FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
            UNIQUE (etudiant_id, type_rappel)
        );
    """)
    conn.commit()
    conn.close()


def inserer_donnees_test():
    """Ajoute 5 étudiants fictifs couvrant les cas qu'on devra gérer."""
    aujourdhui = date.today()

    # (nom, email, montant_total, jours avant la date limite, montant déjà payé)
    etudiants_test = [
        ("Alice Nkomo",     "alice@example.com",  500000,  7, 200000),  # doit recevoir un rappel J-7
        ("Brice Mballa",    "brice@example.com",  500000,  3, 300000),  # doit recevoir un rappel J-3
        ("Carine Fotso",    "carine@example.com", 500000,  1, 100000),  # doit recevoir un rappel J-1
        ("David Essomba",   "david@example.com",  500000,  7, 500000),  # a tout payé : aucun rappel
        ("Estelle Tchamba", "estelle@example.com", 500000, 20, 250000), # échéance trop lointaine
    ]

    conn = get_connection()
    for nom, email, total, jours, paye in etudiants_test:
        date_limite = aujourdhui + timedelta(days=jours)
        curseur = conn.execute(
            "INSERT INTO etudiants (nom, email, montant_total, date_limite) VALUES (?, ?, ?, ?)",
            (nom, email, total, date_limite.isoformat()),
        )
        conn.execute(
            "INSERT INTO paiements (etudiant_id, montant, date_paiement) VALUES (?, ?, ?)",
            (curseur.lastrowid, paye, aujourdhui.isoformat()),
        )
    conn.commit()
    conn.close()


def afficher_situation():
    """Affiche pour chaque étudiant : total, payé, solde, date limite."""
    conn = get_connection()
    lignes = conn.execute("""
        SELECT e.nom,
               e.montant_total,
               COALESCE(SUM(p.montant), 0) AS paye,
               e.date_limite
        FROM etudiants e
        LEFT JOIN paiements p ON p.etudiant_id = e.id
        GROUP BY e.id
    """).fetchall()
    conn.close()

    print(f"{'Nom':<18}{'Total':>10}{'Payé':>10}{'Solde':>10}   Date limite")
    for l in lignes:
        solde = l["montant_total"] - l["paye"]
        print(f"{l['nom']:<18}{l['montant_total']:>10}{l['paye']:>10}{solde:>10}   {l['date_limite']}")


if __name__ == "__main__":
    reinitialiser_base()
    inserer_donnees_test()
    afficher_situation()




