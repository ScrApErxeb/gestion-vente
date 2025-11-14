"""
Fonctions d'export (PDF, Excel)
"""
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
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