from logique import get_rappels_a_envoyer, enregistrer_rappel
from emails import envoyer_email


def main():
    rappels = get_rappels_a_envoyer()
    print(f"{len(rappels)} rappel(s) à envoyer.")

    envoyes = 0
    echecs = 0
    for r in rappels:
        print(f"Envoi à {r['nom']} ({r['email']}) - {r['type_rappel']}...")
        if envoyer_email(r):
            enregistrer_rappel(r["etudiant_id"], r["type_rappel"])  # seulement si réussi
            envoyes += 1
        else:
            echecs += 1

    print(f"Terminé : {envoyes} envoyé(s), {echecs} échec(s).")


if __name__ == "__main__":
    main()