"""
Fonctions d'export (PDF, Excel)
"""
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

def exporter_ventes_pdf(ventes, filename=None):
    """Exporte les ventes en PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Rapport des Ventes", styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Préparer les données du tableau
    data = [['Facture', 'Client', 'Produit', 'Quantité', 'Montant', 'Date']]
    
    for vente in ventes:
        data.append([
            vente.numero_facture,
            vente.client.nom if vente.client else 'Anonyme',
            vente.produit.nom,
            str(vente.quantite),
            f"{vente.montant_total:,.0f} F",
            vente.date_vente.strftime('%d/%m/%Y')
        ])
    
    # Créer le tableau
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return buffer


import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def exporter_facture_pdf(vente):
    """
    Exporte une facture PDF pour une vente multi-produits
    vente.items: liste d'objets VenteItem avec .produit.nom, .quantite, .prix_unitaire, .remise
    vente.devise, vente.numero_facture, vente.date_vente, vente.client, vente.mode_paiement, vente.notes
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterTitle', alignment=1, fontSize=18, spaceAfter=12))
    styles.add(ParagraphStyle(name='Right', alignment=2))

    # Titre
    elements.append(Paragraph(f"Facture N° {vente.numero_facture}", styles['CenterTitle']))

    # Infos client et vente
    client_nom = getattr(vente, 'client', 'Client anonyme')
    info_text = f"""
    <b>Client :</b> {client_nom}<br/>
    <b>Date :</b> {vente.date_vente.strftime('%d/%m/%Y %H:%M')}<br/>
    <b>Mode de paiement :</b> {vente.mode_paiement}<br/>
    <b>Devise :</b> {vente.devise}
    """
    elements.append(Paragraph(info_text, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Tableau produits
    data = [['Produit', 'Quantité', 'Prix Unitaire', 'Remise (%)', 'Montant']]
    total = 0

    for item in getattr(vente, 'items', []):
        produit_nom = item.produit.nom if item.produit else "Produit inconnu"
        quantite = item.quantite
        prix_unitaire = item.prix_unitaire
        remise = getattr(item, 'remise', 0) or 0

        montant_item = prix_unitaire * quantite * (1 - remise / 100)
        total += montant_item

        data.append([
            produit_nom,
            str(quantite),
            f"{prix_unitaire:,.2f} {vente.devise}",
            f"{remise:.2f}%",
            f"{montant_item:,.2f} {vente.devise}"
        ])

    # Création du tableau
    table = Table(data, colWidths=[200, 60, 80, 60, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Total
    elements.append(Paragraph(f"<b>Total à payer : {total:,.2f} {vente.devise}</b>", styles['Heading2']))

    # Notes
    if getattr(vente, 'notes', None):
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"<b>Notes :</b> {vente.notes}", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def exporter_produits_excel(produits, filename=None):


    """Exporte les produits en Excel"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Produits"
    
    # En-têtes
    headers = ['Référence', 'Nom', 'Catégorie', 'Prix Achat', 'Prix Vente', 'Stock', 'Stock Min', 'Fournisseur']
    for col, header in enumerate(headers, 1):
        ws.cell(row=1, column=col, value=header)
        ws.cell(row=1, column=col).font = Font(bold=True)
        ws.cell(row=1, column=col).fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
    
    # Données
    for row, produit in enumerate(produits, 2):
        ws.cell(row=row, column=1, value=produit.reference)
        ws.cell(row=row, column=2, value=produit.nom)
        ws.cell(row=row, column=3, value=produit.categorie.nom if produit.categorie else '')
        ws.cell(row=row, column=4, value=produit.prix_achat)
        ws.cell(row=row, column=5, value=produit.prix_vente)
        ws.cell(row=row, column=6, value=produit.stock_actuel)
        ws.cell(row=row, column=7, value=produit.stock_min)
        ws.cell(row=row, column=8, value=produit.fournisseur.nom if produit.fournisseur else '')
    
    # Ajuster la largeur des colonnes
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer