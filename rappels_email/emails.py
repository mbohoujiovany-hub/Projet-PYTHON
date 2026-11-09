import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()  # lit le fichier .env

SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "false").lower() == "true"
EXPEDITEUR = os.getenv("EXPEDITEUR", "scolarite@polytech-test.cm")


def formater_montant(montant):
    """300000 -> '300 000 FCFA'"""
    return f"{montant:,}".replace(",", " ") + " FCFA"


def construire_message(rappel):
    """Crée l'email à partir d'un dictionnaire renvoyé par get_rappels_a_envoyer()."""
    jours = rappel["jours_restants"]
    if jours == 0:
        delai = "aujourd'hui"
    elif jours == 1:
        delai = "demain"
    else:
        delai = f"dans {jours} jours"

    date_limite = rappel["date_limite"].strftime("%d/%m/%Y")

    msg = EmailMessage()
    msg["Subject"] = "Rappel : date limite de paiement de votre scolarité"
    msg["From"] = EXPEDITEUR
    msg["To"] = rappel["email"]
    msg.set_content(
        f"Bonjour {rappel['nom']},\n\n"
        f"La date limite de paiement de vos frais de scolarité est {delai} "
        f"({date_limite}).\n"
        f"Il vous reste {formater_montant(rappel['solde'])} à régler.\n\n"
        f"Vous pouvez terminer votre versement sur la plateforme de paiement "
        f"de Polytech Yaoundé.\n\n"
        f"Cordialement,\n"
        f"Le service de la scolarité"
    )
    return msg


def envoyer_email(rappel):
    """Envoie le rappel. Retourne True si réussi, False sinon."""
    msg = construire_message(rappel)
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as serveur:
            if SMTP_USE_TLS:
                serveur.starttls()
            if SMTP_USER:
                serveur.login(SMTP_USER, SMTP_PASSWORD)
            serveur.send_message(msg)
        return True
    except (smtplib.SMTPException, OSError) as erreur:
        print(f"  ERREUR d'envoi à {rappel['email']} : {erreur}")
        return False